from __future__ import annotations

from datetime import datetime, timedelta
from fastapi import APIRouter, Query
from fastapi.responses import Response

from src.services.audit_exporter import AuditExporter
from src.observability.metrics import chat_metrics
from src.observability.feature_flags import flags

router = APIRouter(prefix="/v1", tags=["compliance", "observability"])


@router.get("/audit/exports")
async def export_audit(
    session_id: str | None = Query(None),
    user_id: str | None = Query(None),
    format: str = Query("json", regex="^(csv|json)$"),
    days: int = Query(7, ge=1, le=365),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
):
    """Exporta trilhas de auditoria em CSV ou JSON."""
    exporter = AuditExporter(None)  # TODO: injetar audit_logger
    
    if format == "csv":
        csv_content = await exporter.export_session_csv(None)  # TODO: usar session_id real
        return Response(content=csv_content, media_type="text/csv")
    else:
        json_data = await exporter.export_session_json(
            session_id=session_id,
            user_id=user_id,
            days=days,
        )
        return json_data


@router.get("/observability/health")
async def health_check():
    """Retorna status de saúde do sistema e métricas SLO."""
    from src.database import db
    from src.services.llm_service import LLMService
    
    # Verifica status do banco de dados
    db_status = "unknown"
    db_version = "unknown"
    try:
        result = await db.execute_query("SELECT version()")
        if result:
            db_version = result[0].get('version', 'unknown')
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
    
    # Verifica status dos LLM providers
    llm_providers = []
    llm_count_healthy = 0
    try:
        from src.services.llm_service import LLMService
        providers_list = LLMService.get_providers_status()  # Retorna lista diretamente
        
        # Processa cada provider
        if isinstance(providers_list, list):
            for provider in providers_list:
                if isinstance(provider, dict):
                    # Mapeia campos do LLMService para formato do observability
                    provider_status = provider.get('status', 'unknown')
                    is_healthy = provider_status == 'healthy' or provider_status == 'available'
                    
                    # Extrai nome do provider
                    provider_id = provider.get('provider_id', 'unknown')
                    provider_type = provider.get('provider_type', 'unknown')
                    
                    # Cria nome amigável
                    if 'google' in provider_id.lower() or provider_type == 'google':
                        name = f"Google Gemini ({provider_id})"
                        model = "gemini-1.5-flash"
                    elif 'anthropic' in provider_id.lower() or provider_type == 'anthropic':
                        name = f"Anthropic Claude ({provider_id})"
                        model = "claude-3-5-sonnet"
                    elif 'openai' in provider_id.lower() or provider_type == 'openai':
                        name = f"OpenAI GPT ({provider_id})"
                        model = "gpt-4-turbo"
                    elif 'huggingface' in provider_id.lower() or provider_type == 'huggingface':
                        name = f"HuggingFace ({provider_id})"
                        model = "meta-llama/Meta-Llama-3-8B-Instruct"
                    else:
                        name = provider_id
                        model = "N/A"
                    
                    llm_providers.append({
                        "name": name,
                        "type": provider_type,
                        "status": "healthy" if is_healthy else "unhealthy",
                        "model": model,
                        "enabled": provider.get('enabled', False),
                        "circuit_breaker_open": provider.get('circuit_breaker_open', False),
                        "consecutive_failures": provider.get('consecutive_failures', 0),
                    })
                    if is_healthy:
                        llm_count_healthy += 1
    except Exception as e:
        print(f"[observability] Error getting LLM providers: {e}")
        import traceback
        traceback.print_exc()
        llm_providers = [{"error": str(e)[:100]}]
    
    # Calcula latência P95
    p95_latency = chat_metrics.p95_latency() * 1000 if chat_metrics.p95_latency() > 0 else 0
    
    # Status geral do sistema
    overall_status = "healthy"
    if db_status != "connected":
        overall_status = "degraded"
    elif not any(p.get('status') == 'healthy' for p in llm_providers if isinstance(p, dict)):
        overall_status = "degraded"
    elif flags.read_only_mode:
        overall_status = "read_only"
    
    # Calcula uptime (simplificado: se banco conectado e tem LLMs = 100%, senão 99%)
    uptime_percent = 100.0 if (db_status == "connected" and llm_count_healthy > 0) else 99.0
    
    # Obtém estatísticas de métricas
    stats = chat_metrics.get_stats() if hasattr(chat_metrics, 'get_stats') else {}
    
    # Retorna apenas dados novos e detalhados
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_percent": uptime_percent,
        "p95_latency_ms": round(p95_latency, 2),
        
        # Dados detalhados do banco de dados
        "database": {
            "name": "PostgreSQL (NeonDB)",
            "status": "connected" if db_status == "connected" else "disconnected",
            "version": db_version[:80] if len(db_version) > 80 else db_version,
            "last_check": datetime.utcnow().isoformat(),
            "healthy": db_status == "connected"
        },
        
        # Dados detalhados dos LLM providers
        "llm_providers": llm_providers,
        "llm_summary": {
            "total_providers": len(llm_providers),
            "active_providers": llm_count_healthy,
            "status": "healthy" if llm_count_healthy > 0 else "degraded",
            "last_check": datetime.utcnow().isoformat()
        },
        
        # Métricas detalhadas
        "metrics": {
            "p95_latency_ms": round(p95_latency, 2),
            "avg_latency_ms": round(chat_metrics.avg_latency() * 1000, 2),
            "total_requests": stats.get('total_requests', 0),
            "successful_requests": stats.get('successful_requests', 0),
            "failed_requests": stats.get('failed_requests', 0),
        },
        
        # Features ativas
        "features": {
            "read_only_mode": flags.read_only_mode,
            "smart_detection": True,
            "cache_enabled": True,
        }
    }
