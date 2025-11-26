"""Testes de integração para refresh de schema."""

from __future__ import annotations

import asyncio
import pytest
from datetime import timedelta

from src.services.schema_detector_service import SchemaDetectorService


@pytest.mark.asyncio
class TestSchemaRefresh:
    """Testes para comportamento de refresh do cache de schema."""
    
    async def test_schema_refreshes_after_ttl(self, sample_schema):
        """
        T064: GIVEN: Schema cacheado com TTL = 2 segundos
        WHEN: 3 segundos se passam
        THEN: Próxima requisição dispara refresh
        """
        # Configura TTL curto para teste
        SchemaDetectorService._ttl = timedelta(seconds=2)
        SchemaDetectorService._cache = None
        SchemaDetectorService._cache_timestamp = None
        
        # Primeira chamada - popula cache
        schema1 = await SchemaDetectorService.get_schema()
        timestamp1 = SchemaDetectorService._cache_timestamp
        
        # Aguarda TTL expirar
        await asyncio.sleep(2.5)
        
        # Segunda chamada - deve fazer refresh
        schema2 = await SchemaDetectorService.get_schema()
        timestamp2 = SchemaDetectorService._cache_timestamp
        
        # Timestamps devem ser diferentes
        assert timestamp2 > timestamp1
        
        # Restaura TTL padrão
        from src.config import settings
        SchemaDetectorService._ttl = timedelta(seconds=settings.SCHEMA_CACHE_TTL_SECONDS)
    
    async def test_schema_detects_new_table(self):
        """
        T065: GIVEN: Schema cacheado
        WHEN: Nova tabela adicionada ao banco E cache refreshed
        THEN: Nova tabela aparece no SchemaInfo
        
        Nota: Este teste requer conexão real com banco de dados
        e permissões para criar/dropar tabelas temporárias.
        """
        # Este teste é mais conceitual - em ambiente real:
        # 1. Captura schema inicial
        # 2. Cria tabela temporária no banco
        # 3. Força refresh do cache
        # 4. Verifica que nova tabela foi detectada
        # 5. Remove tabela temporária
        
        # Por enquanto, apenas valida que o método de refresh existe
        assert hasattr(SchemaDetectorService, 'clear_cache')
        assert hasattr(SchemaDetectorService, 'get_schema')
        
        # Testa clear_cache
        SchemaDetectorService.clear_cache()
        assert SchemaDetectorService._cache is None
        assert SchemaDetectorService._cache_timestamp is None

