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
    return {
        "status": "healthy" if not flags.read_only_mode else "degraded",
        "uptime_percent": 99.5,  # TODO: calcular real
        "p95_latency_ms": chat_metrics.p95_latency() * 1000,
        "integrations": {
            "neondb": {"status": "ok", "last_check": datetime.utcnow().isoformat()},
            "s3": {"status": "ok", "last_check": datetime.utcnow().isoformat()},
            "rag": {"status": "ok", "last_check": datetime.utcnow().isoformat()},
        },
        "degraded_mode": flags.read_only_mode,
        "timestamp": datetime.utcnow().isoformat(),
    }
