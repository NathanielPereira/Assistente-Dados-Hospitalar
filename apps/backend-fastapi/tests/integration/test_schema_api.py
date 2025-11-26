"""Testes de integração para API de schema."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSchemaAPI:
    """Testes para endpoints de schema."""
    
    async def test_get_schema_info_returns_200(self):
        """
        T063: GIVEN: Schema está cacheado
        WHEN: GET /v1/schema/info
        THEN: Retorna 200 com SchemaInfo e headers
        """
        from src.api.main import app
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/v1/schema/info")
            
            assert response.status_code == 200
            
            # Verifica headers
            assert "x-cache-age" in response.headers
            assert "x-schema-version" in response.headers
            
            # Verifica conteúdo
            data = response.json()
            assert "tables" in data
            assert "last_updated" in data
            assert "version" in data
            assert isinstance(data["tables"], list)
    
    async def test_get_schema_stats(self):
        """Testa endpoint de estatísticas do schema."""
        from src.api.main import app
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/v1/schema/stats")
            
            assert response.status_code == 200
            
            data = response.json()
            assert "tables_count" in data
            assert "total_columns" in data
            assert "cache_age_seconds" in data
            assert "column_types_distribution" in data
    
    async def test_refresh_schema(self):
        """Testa atualização forçada do cache."""
        from src.api.main import app
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/v1/schema/refresh")
            
            assert response.status_code == 200
            
            data = response.json()
            assert "message" in data
            assert "tables_count" in data
            assert data["message"] == "Schema cache atualizado com sucesso"

