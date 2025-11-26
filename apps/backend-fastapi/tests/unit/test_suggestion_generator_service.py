"""Unit tests for SuggestionGeneratorService."""

from __future__ import annotations

import pytest

from src.domain.question_analysis import SmartResponse, QuestionAnalysis, QuestionIntent


class TestSuggestionGeneratorService:
    """Test suite for SuggestionGeneratorService."""
    
    def test_generate_smart_response_unanswerable(self, sample_schema):
        """
        T034: GIVEN: Question cannot be answered (confidence = 0.0)
        AND: Entities not found: ["protocolo", "isolamento"]
        WHEN: generate_smart_response() is called
        THEN: Returns SmartResponse with message, entities, 3 suggestions
        """
        from src.services.suggestion_generator_service import SuggestionGeneratorService
        from src.domain.question_analysis import QuestionAnalysis, QuestionIntent
        
        # Mock question analysis
        analysis = QuestionAnalysis(
            question="Qual protocolo aplicar para isolamento?",
            entities_mentioned=["protocolo", "isolamento"],
            entities_found_in_schema=[],
            entities_not_found=["protocolo", "isolamento"],
            confidence_score=0.0,
            intent=QuestionIntent.FILTER,
            can_answer=False,
            reason="Entities not found"
        )
        
        response = SuggestionGeneratorService.generate_smart_response(analysis, sample_schema)
        
        assert isinstance(response, SmartResponse)
        assert response.can_answer is False
        assert "protocolo" in response.message or "isolamento" in response.message
        assert len(response.available_entities) >= 3
        assert len(response.suggestions) == 3
    
    def test_suggestions_are_diverse(self, sample_schema):
        """
        T035: GIVEN: Schema with multiple tables
        WHEN: generate_suggestions() is called
        THEN: Returns 3 diverse suggestions (different types)
        """
        from src.services.suggestion_generator_service import SuggestionGeneratorService
        
        suggestions = SuggestionGeneratorService.generate_suggestions(sample_schema)
        
        assert len(suggestions) == 3
        assert len(set(suggestions)) == 3  # All unique
        
        # At least 2 different question patterns
        suggestion_text = " ".join(suggestions).lower()
        patterns_found = 0
        if "quantos" in suggestion_text or "quantas" in suggestion_text:
            patterns_found += 1
        if "quais" in suggestion_text:
            patterns_found += 1
        if "qual" in suggestion_text and "média" not in suggestion_text:
            patterns_found += 1
            
        assert patterns_found >= 2
    
    def test_suggestions_prioritize_important_tables(self, sample_schema):
        """
        T036: GIVEN: No context from original question
        WHEN: generate_suggestions() is called
        THEN: Prioritizes leitos, atendimentos (important tables)
        """
        from src.services.suggestion_generator_service import SuggestionGeneratorService
        
        suggestions = SuggestionGeneratorService.generate_suggestions(sample_schema)
        
        suggestions_text = " ".join(suggestions).lower()
        
        # Should include at least one priority keyword
        priority_keywords = ["leitos", "atendimentos", "especialidades"]
        assert any(keyword in suggestions_text for keyword in priority_keywords)
    
    def test_partial_match_response(self, sample_schema):
        """
        T037: GIVEN: Partial match (some entities found, others not)
        WHEN: generate_smart_response() is called
        THEN: Response includes partial_match=True, found_entities
        """
        from src.services.suggestion_generator_service import SuggestionGeneratorService
        from src.domain.question_analysis import QuestionAnalysis, QuestionIntent
        
        analysis = QuestionAnalysis(
            question="Quantos leitos e protocolos temos?",
            entities_mentioned=["leitos", "protocolos"],
            entities_found_in_schema=["leitos"],
            entities_not_found=["protocolos"],
            confidence_score=0.50,
            intent=QuestionIntent.COUNT,
            can_answer=False,
            reason="Partial match"
        )
        
        response = SuggestionGeneratorService.generate_smart_response(
            analysis, 
            sample_schema,
            is_partial_match=True
        )
        
        assert response.partial_match is True
        assert len(response.found_entities) > 0
        assert "leitos" in response.found_entities or "leitos" in response.message

