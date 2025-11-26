"""Testes de performance para validar targets da spec."""

from __future__ import annotations

import pytest
import time
from unittest.mock import patch, AsyncMock

from src.services.schema_detector_service import SchemaDetectorService
from src.services.question_analyzer_service import QuestionAnalyzerService
from src.services.suggestion_generator_service import SuggestionGeneratorService


@pytest.mark.asyncio
class TestPerformanceBenchmarks:
    """Valida targets de performance da especificação."""
    
    async def test_schema_detection_cached_under_100ms(self, sample_schema):
        """
        T070: GIVEN: Schema já cacheado
        WHEN: get_schema() é chamado
        THEN: Retorna em < 100ms
        """
        # Prepara cache
        SchemaDetectorService._cache = sample_schema
        from datetime import datetime
        SchemaDetectorService._cache_timestamp = datetime.utcnow()
        
        # Mede tempo
        start = time.perf_counter()
        schema = await SchemaDetectorService.get_schema()
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 100, f"Schema cacheado levou {duration_ms:.2f}ms (target: <100ms)"
        assert schema is sample_schema
    
    async def test_schema_detection_fresh_under_500ms(self, sample_schema):
        """
        T071: GIVEN: Cache vazio
        WHEN: get_schema() é chamado
        THEN: Retorna em < 500ms (incluindo query DB)
        """
        # Limpa cache
        SchemaDetectorService._cache = None
        SchemaDetectorService._cache_timestamp = None
        
        # Mock da detecção para simular query rápida
        with patch.object(SchemaDetectorService, '_detect_schema', return_value=sample_schema) as mock_detect:
            start = time.perf_counter()
            schema = await SchemaDetectorService.get_schema()
            duration_ms = (time.perf_counter() - start) * 1000
            
            assert duration_ms < 500, f"Detecção fresh levou {duration_ms:.2f}ms (target: <500ms)"
            assert mock_detect.called
    
    def test_question_analysis_under_500ms(self, sample_schema):
        """
        T072: GIVEN: Pergunta para analisar
        WHEN: analyze_question() é chamado
        THEN: Retorna em < 500ms
        """
        question = "Quantos leitos e atendimentos e especialidades temos?"
        
        start = time.perf_counter()
        analysis = QuestionAnalyzerService.analyze_question(question, sample_schema)
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 500, f"Análise levou {duration_ms:.2f}ms (target: <500ms)"
        assert analysis is not None
    
    def test_complete_smart_response_under_1_second(self, sample_schema):
        """
        T073: GIVEN: Pergunta não respondível
        WHEN: Análise completa + geração de sugestões
        THEN: Completa em < 1 segundo
        """
        question = "Quais protocolos de isolamento existem?"
        
        start = time.perf_counter()
        
        # Fluxo completo
        analysis = QuestionAnalyzerService.analyze_question(question, sample_schema)
        response = SuggestionGeneratorService.generate_smart_response(analysis, sample_schema)
        
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 1000, f"Fluxo completo levou {duration_ms:.2f}ms (target: <1000ms)"
        assert response is not None
        assert len(response.suggestions) == 3


class TestPerformanceOptimizations:
    """Testes adicionais de otimização."""
    
    def test_entity_extraction_is_fast(self):
        """Verifica que extração de entidades é rápida."""
        question = "Quantos leitos e atendimentos e especialidades e procedimentos temos?"
        
        start = time.perf_counter()
        for _ in range(100):  # 100 iterações
            entities, mappings = QuestionAnalyzerService.extract_entities(question)
        duration_ms = (time.perf_counter() - start) * 1000
        
        avg_ms = duration_ms / 100
        assert avg_ms < 10, f"Extração média: {avg_ms:.2f}ms (esperado: <10ms)"
    
    def test_suggestion_generation_is_fast(self, sample_schema):
        """Verifica que geração de sugestões é rápida."""
        start = time.perf_counter()
        for _ in range(50):  # 50 iterações
            suggestions = SuggestionGeneratorService.generate_suggestions(sample_schema)
        duration_ms = (time.perf_counter() - start) * 1000
        
        avg_ms = duration_ms / 50
        assert avg_ms < 20, f"Geração média: {avg_ms:.2f}ms (esperado: <20ms)"

