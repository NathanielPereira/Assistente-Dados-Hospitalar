"""Unit tests for QuestionAnalyzerService."""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from src.domain.question_analysis import QuestionAnalysis, QuestionIntent


class TestQuestionAnalyzerService:
    """Test suite for QuestionAnalyzerService."""
    
    def test_extract_entities_removes_stop_words(self):
        """
        T020: GIVEN: Question "Quantos leitos estão disponíveis?"
        WHEN: extract_entities() is called
        THEN: Returns ["leitos", "disponíveis"] (removes "quantos", "estão")
        """
        from src.services.question_analyzer_service import QuestionAnalyzerService
        
        question = "Quantos leitos estão disponíveis?"
        entities = QuestionAnalyzerService.extract_entities(question)
        
        assert "leitos" in entities
        assert "disponíveis" in entities or "disponivel" in entities  # May normalize
        assert "quantos" not in entities
        assert "estão" not in entities
    
    def test_synonym_mapping_applied(self, synonyms_dict):
        """
        T021: GIVEN: Question "Quantas camas temos?" and synonym "camas" → "leitos"
        WHEN: extract_entities() with synonym mapping
        THEN: Returns ["leitos"] (synonym mapped)
        """
        from src.services.question_analyzer_service import QuestionAnalyzerService
        
        # Load synonyms
        QuestionAnalyzerService._synonyms = synonyms_dict
        
        question = "Quantas camas temos?"
        entities, mappings = QuestionAnalyzerService.extract_entities(question, apply_synonyms=True)
        
        assert "leitos" in entities or "leitos" in mappings.values()
        assert mappings.get("camas") == "leitos" or "camas" not in entities
    
    def test_analyze_question_high_confidence(self, sample_schema, synonyms_dict):
        """
        T022: GIVEN: Question "Quantos leitos estão disponíveis?"
        AND: Schema contains "leitos" table
        WHEN: analyze_question() is called
        THEN: Returns QuestionAnalysis with can_answer=True, confidence>=0.70
        """
        from src.services.question_analyzer_service import QuestionAnalyzerService
        
        QuestionAnalyzerService._synonyms = synonyms_dict
        
        question = "Quantos leitos estão disponíveis?"
        analysis = QuestionAnalyzerService.analyze_question(question, sample_schema)
        
        assert isinstance(analysis, QuestionAnalysis)
        assert analysis.can_answer is True
        assert analysis.confidence_score >= 0.70
        assert "leitos" in analysis.entities_found_in_schema
        assert len(analysis.entities_not_found) == 0
        assert analysis.intent == QuestionIntent.COUNT
    
    def test_analyze_question_low_confidence(self, sample_schema):
        """
        T023: GIVEN: Question "Qual protocolo aplicar para isolamento?"
        AND: Schema does NOT contain "protocolo" or "isolamento"
        WHEN: analyze_question() is called
        THEN: Returns can_answer=False, confidence<0.70
        """
        from src.services.question_analyzer_service import QuestionAnalyzerService
        
        question = "Qual protocolo aplicar para isolamento?"
        analysis = QuestionAnalyzerService.analyze_question(question, sample_schema)
        
        assert analysis.can_answer is False
        assert analysis.confidence_score < 0.70
        assert len(analysis.entities_not_found) > 0
        assert "protocolo" in analysis.entities_not_found or "isolamento" in analysis.entities_not_found
        assert len(analysis.entities_found_in_schema) == 0
        assert analysis.reason is not None
    
    def test_analyze_question_partial_match(self, sample_schema):
        """
        T024: GIVEN: Question "Quantos leitos e protocolos temos?"
        AND: Schema contains "leitos" but NOT "protocolos"
        WHEN: analyze_question() is called
        THEN: Some entities found, others not (partial match)
        """
        from src.services.question_analyzer_service import QuestionAnalyzerService
        
        question = "Quantos leitos e protocolos temos?"
        analysis = QuestionAnalyzerService.analyze_question(question, sample_schema)
        
        assert "leitos" in analysis.entities_found_in_schema
        assert "protocolos" in analysis.entities_not_found or "protocolo" in analysis.entities_not_found
        assert 0.4 <= analysis.confidence_score <= 0.6  # Around 50%
        assert analysis.is_partial_match is True
    
    def test_similarity_matching(self, sample_schema):
        """
        T025: GIVEN: Question with misspelled entity "leitoss" (similar to "leitos")
        WHEN: analyze_question() is called
        THEN: Detects similarity and includes in similar_entities dict
        """
        from src.services.question_analyzer_service import QuestionAnalyzerService
        
        question = "Quantos leitoss temos?"
        analysis = QuestionAnalyzerService.analyze_question(question, sample_schema)
        
        # Should find "leitos" as similar
        assert "leitos" in analysis.similar_entities or "leitos" in analysis.entities_found_in_schema
        if "leitos" in analysis.similar_entities:
            assert analysis.similar_entities["leitos"] >= 0.70
    
    def test_intent_detection_count(self):
        """
        T026: GIVEN: Question "Quantos X?"
        WHEN: detect_intent() is called
        THEN: Returns QuestionIntent.COUNT
        """
        from src.services.question_analyzer_service import QuestionAnalyzerService
        
        questions = [
            "Quantos leitos?",
            "Quantas consultas?",
            "Qual o total de atendimentos?",
        ]
        
        for q in questions:
            intent = QuestionAnalyzerService.detect_intent(q)
            assert intent == QuestionIntent.COUNT, f"Failed for: {q}"
    
    def test_intent_detection_list(self):
        """
        T026: GIVEN: Question "Quais X?"
        WHEN: detect_intent() is called
        THEN: Returns QuestionIntent.LIST
        """
        from src.services.question_analyzer_service import QuestionAnalyzerService
        
        questions = [
            "Quais leitos estão disponíveis?",
            "Liste as especialidades",
            "Mostre os atendimentos",
        ]
        
        for q in questions:
            intent = QuestionAnalyzerService.detect_intent(q)
            assert intent == QuestionIntent.LIST, f"Failed for: {q}"
    
    def test_intent_detection_aggregate(self):
        """
        T026: GIVEN: Question "Qual a média de X?"
        WHEN: detect_intent() is called
        THEN: Returns QuestionIntent.AGGREGATE
        """
        from src.services.question_analyzer_service import QuestionAnalyzerService
        
        questions = [
            "Qual a média de atendimentos?",
            "Calcule a receita total",
            "Qual o valor médio?",
        ]
        
        for q in questions:
            intent = QuestionAnalyzerService.detect_intent(q)
            assert intent == QuestionIntent.AGGREGATE, f"Failed for: {q}"


class TestSynonymMapper:
    """Tests for SynonymMapper helper class."""
    
    def test_load_synonyms_from_json(self):
        """Test loading synonym mappings from config file."""
        from src.services.question_analyzer_service import SynonymMapper
        from pathlib import Path
        
        # Should load from config/synonyms.json
        config_path = Path("config/synonyms.json")
        if config_path.exists():
            SynonymMapper.load()
            
            assert SynonymMapper._loaded is True
            assert len(SynonymMapper._cache) > 0
            assert SynonymMapper.get("camas") == "leitos"
    
    def test_synonym_mapping_returns_original_if_not_found(self):
        """Test that unmapped terms return original."""
        from src.services.question_analyzer_service import SynonymMapper
        
        SynonymMapper._cache = {"camas": "leitos"}
        SynonymMapper._loaded = True
        
        assert SynonymMapper.get("camas") == "leitos"
        assert SynonymMapper.get("unknown_term") == "unknown_term"

