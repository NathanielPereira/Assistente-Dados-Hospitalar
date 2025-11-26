"""Rotas da API para inspeção de schema."""

from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.services.schema_detector_service import SchemaDetectorService

router = APIRouter(prefix="/v1/schema", tags=["schema"])


@router.get("/info")
async def get_schema_info():
    """
    Retorna informações do schema atual do banco de dados.
    
    Útil para:
    - Entender quais dados estão disponíveis
    - Debugging de problemas de detecção de entidades
    - Monitoramento da idade do cache
    
    Returns:
        SchemaInfo: Schema atual com todas as tabelas e colunas
        
    Headers:
        X-Cache-Age: Segundos desde a última atualização
        X-Schema-Version: Versão do schema
    """
    try:
        # Obtém schema do cache
        schema = await SchemaDetectorService.get_schema()
        
        # Calcula idade do cache
        cache_age = SchemaDetectorService.get_cache_age()
        cache_age_seconds = int(cache_age.total_seconds()) if cache_age else 0
        
        # Prepara resposta
        response_data = schema.model_dump(mode='json')
        
        # Adiciona headers informativos
        headers = {
            "X-Cache-Age": str(cache_age_seconds),
            "X-Schema-Version": schema.version
        }
        
        # Verifica se está em modo degradado (cache muito antigo)
        if cache_age_seconds > 7200:  # 2 horas
            return JSONResponse(
                content={
                    **response_data,
                    "warning": "Schema cache is stale (> 2 hours old)",
                    "degraded_mode": True
                },
                headers=headers,
                status_code=200
            )
        
        return JSONResponse(
            content=response_data,
            headers=headers,
            status_code=200
        )
        
    except Exception as e:
        # Se falhar ao obter schema, retorna 503 (serviço indisponível)
        raise HTTPException(
            status_code=503,
            detail=f"Falha ao detectar schema: {str(e)}"
        )


@router.post("/refresh")
async def refresh_schema():
    """
    Força atualização do cache de schema.
    
    Útil para:
    - Testar detecção de mudanças no schema
    - Forçar atualização após ALTER TABLE
    - Recuperação de modo degradado
    
    Returns:
        Mensagem de sucesso com timestamp da atualização
    """
    try:
        # Limpa cache para forçar refresh
        SchemaDetectorService.clear_cache()
        
        # Obtém schema novamente (vai detectar do banco)
        schema = await SchemaDetectorService.get_schema()
        
        return {
            "message": "Schema cache atualizado com sucesso",
            "tables_count": len(schema.tables),
            "columns_count": schema.total_columns,
            "updated_at": schema.last_updated.isoformat(),
            "version": schema.version
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar schema: {str(e)}"
        )


@router.get("/stats")
async def get_schema_stats():
    """
    Retorna estatísticas sobre o schema e cache.
    
    Returns:
        Estatísticas: contadores e métricas do schema
    """
    try:
        schema = await SchemaDetectorService.get_schema()
        cache_age = SchemaDetectorService.get_cache_age()
        
        # Coleta estatísticas
        stats = {
            "tables_count": len(schema.tables),
            "total_columns": schema.total_columns,
            "cache_age_seconds": int(cache_age.total_seconds()) if cache_age else 0,
            "cache_ttl_seconds": SchemaDetectorService._ttl.total_seconds(),
            "version": schema.version,
            "last_updated": schema.last_updated.isoformat(),
            "tables_by_column_count": {},
            "column_types_distribution": {}
        }
        
        # Agrupa tabelas por número de colunas
        for table in schema.tables:
            col_count = len(table.columns)
            if col_count not in stats["tables_by_column_count"]:
                stats["tables_by_column_count"][col_count] = 0
            stats["tables_by_column_count"][col_count] += 1
            
            # Conta tipos de colunas
            for column in table.columns:
                col_type = column.type
                if col_type not in stats["column_types_distribution"]:
                    stats["column_types_distribution"][col_type] = 0
                stats["column_types_distribution"][col_type] += 1
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )

