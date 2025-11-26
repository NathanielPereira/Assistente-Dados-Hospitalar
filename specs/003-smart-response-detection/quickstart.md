# Quickstart: Smart Response Detection
## Test-Driven Development Guide

**Feature**: 003-smart-response-detection  
**Date**: 2024-11-26  
**Purpose**: Define test scenarios BEFORE implementation (TDD approach)

---

## Table of Contents

1. [Setup](#setup)
2. [Test Data Fixtures](#test-data-fixtures)
3. [Unit Tests](#unit-tests)
4. [Integration Tests](#integration-tests)
5. [Contract Tests](#contract-tests)
6. [Performance Benchmarks](#performance-benchmarks)
7. [Running Tests](#running-tests)

---

## Setup

### Prerequisites

```bash
# Navigate to backend directory
cd apps/backend-fastapi

# Install dependencies (if not already installed)
poetry install

# Activate virtual environment
poetry shell

# Set up test database (if needed)
# ... database setup commands ...
```

### Test Configuration

Create `apps/backend-fastapi/tests/conftest.py` with test fixtures:

```python
import pytest
from datetime import datetime
from src.domain.schema_info import SchemaInfo, TableInfo, ColumnInfo

@pytest.fixture
def sample_schema() -> SchemaInfo:
    """Typical hospital database schema for testing."""
    return SchemaInfo(
        tables=[
            TableInfo(
                name="leitos",
                columns=[
                    ColumnInfo(name="id", type="integer", nullable=False),
                    ColumnInfo(name="numero", type="varchar", nullable=False),
                    ColumnInfo(name="status", type="varchar", nullable=True),
                ],
                description="Hospital beds",
                row_count=150
            ),
            TableInfo(
                name="atendimentos",
                columns=[
                    ColumnInfo(name="id", type="integer", nullable=False),
                    ColumnInfo(name="paciente_id", type="integer", nullable=False),
                    ColumnInfo(name="data", type="date", nullable=False),
                    ColumnInfo(name="valor", type="decimal", nullable=True),
                ],
                description="Patient appointments",
                row_count=5420
            ),
            TableInfo(
                name="especialidades",
                columns=[
                    ColumnInfo(name="id", type="integer", nullable=False),
                    ColumnInfo(name="nome", type="varchar", nullable=False),
                ],
                description="Medical specialties",
                row_count=25
            ),
        ],
        last_updated=datetime.utcnow(),
        version="1.0.0"
    )

@pytest.fixture
def synonyms_dict() -> dict:
    """Common synonym mappings."""
    return {
        "camas": "leitos",
        "cama": "leitos",
        "quartos": "leitos",
        "consultas": "atendimentos",
        "consulta": "atendimentos",
        "doutores": "especialidades",
        "médicos": "especialidades",
    }
```

---

## Test Data Fixtures

### Test Questions (Known Outcomes)

```python
# tests/fixtures/test_questions.py

ANSWERABLE_QUESTIONS = [
    ("Quantos leitos estão disponíveis?", ["leitos"], 0.90),
    ("Qual a receita média por atendimento?", ["atendimentos"], 0.85),
    ("Quais especialidades estão cadastradas?", ["especialidades"], 0.95),
    ("Quantas camas temos?", ["leitos"], 0.80),  # Synonym
]

UNANSWERABLE_QUESTIONS = [
    ("Qual protocolo aplicar para isolamento?", ["protocolo", "isolamento"], 0.0),
    ("Quanto custa o medicamento Xanax?", ["medicamento", "xanax"], 0.0),
    ("Qual o estoque de EPIs?", ["estoque", "epis"], 0.0),
]

PARTIAL_MATCH_QUESTIONS = [
    ("Quantos leitos e protocolos temos?", ["leitos", "protocolos"], 0.50),
    ("Listar atendimentos e medicamentos", ["atendimentos", "medicamentos"], 0.50),
]

AMBIGUOUS_QUESTIONS = [
    ("O que você sabe?", [], 0.0),
    ("Me ajuda", [], 0.0),
    ("Informações", [], 0.0),
]
```

---

## Unit Tests

### Test 1: Schema Detection Service

**File**: `tests/unit/test_schema_detector_service.py`

```python
import pytest
from datetime import datetime, timedelta
from src.services.schema_detector_service import SchemaDetectorService
from src.domain.schema_info import SchemaInfo

@pytest.mark.asyncio
class TestSchemaDetectorService:
    """Test suite for SchemaDetectorService."""
    
    async def test_detect_schema_from_database(self, db_connection):
        """
        GIVEN: Connected PostgreSQL database with known schema
        WHEN: detect_schema() is called
        THEN: Returns SchemaInfo with all public tables and columns
        """
        schema = await SchemaDetectorService.detect_schema(db_connection)
        
        assert isinstance(schema, SchemaInfo)
        assert len(schema.tables) > 0
        assert schema.last_updated is not None
        assert schema.version == "1.0.0"
        
        # Verify known table exists
        leitos_table = schema.get_table("leitos")
        assert leitos_table is not None
        assert len(leitos_table.columns) > 0
    
    async def test_cache_returns_same_instance_within_ttl(self):
        """
        GIVEN: Schema cached with TTL = 1 hour
        WHEN: get_schema() called twice within TTL
        THEN: Returns same cached instance (no database query)
        """
        SchemaDetectorService._cache = None
        
        schema1 = await SchemaDetectorService.get_schema()
        schema2 = await SchemaDetectorService.get_schema()
        
        assert schema1 is schema2
        assert SchemaDetectorService._cache_timestamp is not None
    
    async def test_cache_refreshes_after_ttl_expiration(self):
        """
        GIVEN: Schema cached but TTL expired
        WHEN: get_schema() is called
        THEN: Refreshes cache from database
        """
        SchemaDetectorService._cache = None
        SchemaDetectorService._ttl = timedelta(seconds=1)
        
        schema1 = await SchemaDetectorService.get_schema()
        
        # Wait for TTL to expire
        import asyncio
        await asyncio.sleep(1.1)
        
        schema2 = await SchemaDetectorService.get_schema()
        
        assert schema1 is not schema2
        assert schema2.last_updated > schema1.last_updated
    
    async def test_graceful_degradation_on_db_failure(self, sample_schema):
        """
        GIVEN: Database connection fails
        AND: Valid stale cache exists
        WHEN: get_schema() is called
        THEN: Returns stale cache (degraded mode)
        AND: Logs warning but does not raise exception
        """
        # Pre-populate cache
        SchemaDetectorService._cache = sample_schema
        SchemaDetectorService._cache_timestamp = datetime.utcnow()
        
        # Simulate database failure (mock connection)
        # ... mock setup ...
        
        schema = await SchemaDetectorService.get_schema()
        
        assert schema is sample_schema
        # Verify warning logged (check logs)
    
    async def test_concurrent_cache_refresh_uses_lock(self):
        """
        GIVEN: Cache expired
        AND: 10 concurrent requests
        WHEN: All requests call get_schema() simultaneously
        THEN: Only ONE database query is executed (lock prevents duplicate work)
        """
        SchemaDetectorService._cache = None
        
        import asyncio
        tasks = [SchemaDetectorService.get_schema() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All results should be the same instance
        assert all(r is results[0] for r in results)
        # Verify only 1 DB query was made (check query counter mock)
```

---

### Test 2: Question Analyzer Service

**File**: `tests/unit/test_question_analyzer_service.py`

```python
import pytest
from src.services.question_analyzer_service import QuestionAnalyzerService
from src.domain.question_analysis import QuestionAnalysis, QuestionIntent

class TestQuestionAnalyzerService:
    """Test suite for QuestionAnalyzerService."""
    
    def test_extract_entities_removes_stop_words(self):
        """
        GIVEN: Question "Quantos leitos estão disponíveis?"
        WHEN: extract_entities() is called
        THEN: Returns ["leitos", "disponíveis"] (removes "quantos", "estão")
        """
        question = "Quantos leitos estão disponíveis?"
        entities = QuestionAnalyzerService.extract_entities(question)
        
        assert "leitos" in entities
        assert "quantos" not in entities
        assert "estão" not in entities
    
    def test_synonym_mapping_applied(self, synonyms_dict):
        """
        GIVEN: Question "Quantas camas temos?" and synonym "camas" → "leitos"
        WHEN: extract_entities() is called
        THEN: Returns ["leitos"] (synonym mapped)
        """
        QuestionAnalyzerService._synonyms = synonyms_dict
        
        question = "Quantas camas temos?"
        entities = QuestionAnalyzerService.extract_entities(question)
        
        assert "leitos" in entities
        assert "camas" not in entities
    
    def test_analyze_question_high_confidence(self, sample_schema, synonyms_dict):
        """
        GIVEN: Question "Quantos leitos estão disponíveis?"
        AND: Schema contains "leitos" table
        WHEN: analyze_question() is called
        THEN: Returns QuestionAnalysis with:
              - can_answer = True
              - confidence_score >= 0.70
              - entities_found = ["leitos"]
        """
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
        GIVEN: Question "Qual protocolo aplicar para isolamento?"
        AND: Schema does NOT contain "protocolo" or "isolamento"
        WHEN: analyze_question() is called
        THEN: Returns QuestionAnalysis with:
              - can_answer = False
              - confidence_score < 0.70
              - entities_not_found = ["protocolo", "isolamento"]
        """
        question = "Qual protocolo aplicar para isolamento?"
        analysis = QuestionAnalyzerService.analyze_question(question, sample_schema)
        
        assert analysis.can_answer is False
        assert analysis.confidence_score < 0.70
        assert "protocolo" in analysis.entities_not_found or "isolamento" in analysis.entities_not_found
        assert len(analysis.entities_found_in_schema) == 0
        assert analysis.reason is not None
    
    def test_analyze_question_partial_match(self, sample_schema):
        """
        GIVEN: Question "Quantos leitos e protocolos temos?"
        AND: Schema contains "leitos" but NOT "protocolos"
        WHEN: analyze_question() is called
        THEN: Returns QuestionAnalysis with:
              - entities_found = ["leitos"]
              - entities_not_found = ["protocolos"]
              - confidence_score = 0.50 (1 of 2 entities found)
              - Behavior depends on threshold (≥70% → reject, <70% → accept partial)
        """
        question = "Quantos leitos e protocolos temos?"
        analysis = QuestionAnalyzerService.analyze_question(question, sample_schema)
        
        assert "leitos" in analysis.entities_found_in_schema
        assert "protocolos" in analysis.entities_not_found
        assert 0.4 <= analysis.confidence_score <= 0.6  # Around 50%
    
    def test_similarity_matching(self, sample_schema):
        """
        GIVEN: Question with misspelled entity "leitoss" (similar to "leitos")
        WHEN: analyze_question() is called
        THEN: Detects similarity and includes in similar_entities dict
        """
        question = "Quantos leitoss temos?"
        analysis = QuestionAnalyzerService.analyze_question(question, sample_schema)
        
        assert "leitos" in analysis.similar_entities
        assert analysis.similar_entities["leitos"] >= 0.70
    
    def test_intent_detection_count(self):
        """
        GIVEN: Question "Quantos X?"
        WHEN: detect_intent() is called
        THEN: Returns QuestionIntent.COUNT
        """
        questions = [
            "Quantos leitos?",
            "Quantas consultas?",
            "Qual o total de atendimentos?",
        ]
        
        for q in questions:
            intent = QuestionAnalyzerService.detect_intent(q)
            assert intent == QuestionIntent.COUNT
    
    def test_intent_detection_list(self):
        """
        GIVEN: Question "Quais X?"
        WHEN: detect_intent() is called
        THEN: Returns QuestionIntent.LIST
        """
        questions = [
            "Quais leitos estão disponíveis?",
            "Liste as especialidades",
            "Mostre os atendimentos",
        ]
        
        for q in questions:
            intent = QuestionAnalyzerService.detect_intent(q)
            assert intent == QuestionIntent.LIST
    
    def test_intent_detection_aggregate(self):
        """
        GIVEN: Question "Qual a média de X?"
        WHEN: detect_intent() is called
        THEN: Returns QuestionIntent.AGGREGATE
        """
        questions = [
            "Qual a média de atendimentos?",
            "Calcule a receita total",
            "Qual o valor médio?",
        ]
        
        for q in questions:
            intent = QuestionAnalyzerService.detect_intent(q)
            assert intent == QuestionIntent.AGGREGATE
```

---

### Test 3: Suggestion Generator Service

**File**: `tests/unit/test_suggestion_generator_service.py`

```python
import pytest
from src.services.suggestion_generator_service import SuggestionGeneratorService
from src.domain.question_analysis import SmartResponse

class TestSuggestionGeneratorService:
    """Test suite for SuggestionGeneratorService."""
    
    def test_generate_smart_response_unanswerable(self, sample_schema):
        """
        GIVEN: Question cannot be answered (confidence = 0.0)
        AND: Entities not found: ["protocolo", "isolamento"]
        WHEN: generate_smart_response() is called
        THEN: Returns SmartResponse with:
              - can_answer = False
              - message explaining what's not available
              - available_entities from schema
              - exactly 3 suggestions
        """
        question_analysis = ... # QuestionAnalysis with can_answer=False
        
        response = SuggestionGeneratorService.generate_smart_response(
            question_analysis, 
            sample_schema
        )
        
        assert isinstance(response, SmartResponse)
        assert response.can_answer is False
        assert "protocolo" in response.message or "isolamento" in response.message
        assert len(response.available_entities) >= 3
        assert len(response.suggestions) == 3
    
    def test_suggestions_are_diverse(self, sample_schema):
        """
        GIVEN: Schema with multiple tables
        WHEN: generate_suggestions() is called
        THEN: Returns 3 suggestions of different types (count, list, aggregate)
        """
        suggestions = SuggestionGeneratorService.generate_suggestions(sample_schema)
        
        assert len(suggestions) == 3
        assert len(set(suggestions)) == 3  # All unique
        
        # At least 2 different question types
        types_used = set()
        if "Quantos" in suggestions[0] or "Quantas" in suggestions[0]:
            types_used.add("count")
        if "Quais" in suggestions[1]:
            types_used.add("list")
        assert len(types_used) >= 2
    
    def test_suggestions_prioritize_important_tables(self, sample_schema):
        """
        GIVEN: No context from original question
        WHEN: generate_suggestions() is called
        THEN: Prioritizes suggestions from common tables (leitos, atendimentos, UTI)
        """
        suggestions = SuggestionGeneratorService.generate_suggestions(sample_schema)
        
        # Convert suggestions to lowercase for easier checking
        suggestions_text = " ".join(suggestions).lower()
        
        # Should include at least one of the priority tables
        priority_keywords = ["leitos", "atendimentos", "uti", "ocupação"]
        assert any(keyword in suggestions_text for keyword in priority_keywords)
    
    def test_partial_match_response_includes_both_found_and_not_found(self, sample_schema):
        """
        GIVEN: Partial match (some entities found, others not)
        WHEN: generate_smart_response() is called
        THEN: Response includes:
              - partial_match = True
              - found_entities list
              - Message mentions both found and not found
        """
        question_analysis = ... # QuestionAnalysis with partial match
        
        response = SuggestionGeneratorService.generate_smart_response(
            question_analysis,
            sample_schema,
            is_partial_match=True
        )
        
        assert response.partial_match is True
        assert len(response.found_entities) > 0
        assert "leitos" in response.message or "disponível" in response.message
```

---

## Integration Tests

### Test 4: End-to-End Smart Detection Flow

**File**: `tests/integration/test_smart_detection_flow.py`

```python
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.mark.asyncio
class TestSmartDetectionFlow:
    """End-to-end integration tests for smart detection."""
    
    async def test_unanswerable_question_returns_smart_response(self):
        """
        GIVEN: User asks about non-existent entity (protocols)
        WHEN: GET /v1/chat/stream?prompt="Quais protocolos?"
        THEN: Returns SSE stream with:
              - [SMART_RESPONSE] marker
              - Explanation message
              - Available entities
              - 3 suggestions
              - [DONE] marker
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/v1/chat/stream",
                params={
                    "session_id": "test-123",
                    "prompt": "Quais protocolos de isolamento estão cadastrados?"
                }
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream"
            
            # Parse SSE stream
            lines = response.text.strip().split("\n")
            data_lines = [line.replace("data: ", "") for line in lines if line.startswith("data:")]
            
            assert "[SMART_RESPONSE]" in data_lines
            assert "[DONE]" in data_lines
            assert any("não está disponível" in line for line in data_lines)
            assert any("Sugestões:" in line for line in data_lines)
            
            # Count suggestions (lines starting with •)
            suggestions = [line for line in data_lines if line.strip().startswith("•")]
            assert len(suggestions) == 3
    
    async def test_answerable_question_proceeds_normally(self):
        """
        GIVEN: User asks about existing entity (leitos)
        WHEN: GET /v1/chat/stream?prompt="Quantos leitos?"
        THEN: Proceeds with normal SQL generation (no smart response)
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/v1/chat/stream",
                params={
                    "session_id": "test-456",
                    "prompt": "Quantos leitos estão disponíveis?"
                }
            )
            
            assert response.status_code == 200
            
            lines = response.text.strip().split("\n")
            data_lines = [line.replace("data: ", "") for line in lines if line.startswith("data:")]
            
            # Should NOT have smart response marker
            assert "[SMART_RESPONSE]" not in data_lines
            # Should have SQL execution
            assert any("Executando SQL" in line or "SELECT" in line for line in data_lines)
            assert "[DONE]" in data_lines
    
    async def test_partial_match_shows_warning(self):
        """
        GIVEN: User asks about mixed entities (leitos + protocolos)
        WHEN: GET /v1/chat/stream?prompt="Quantos leitos e protocolos?"
        THEN: Returns [PARTIAL_MATCH] marker and warning message
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/v1/chat/stream",
                params={
                    "session_id": "test-789",
                    "prompt": "Quantos leitos e protocolos temos?"
                }
            )
            
            assert response.status_code == 200
            
            lines = response.text.strip().split("\n")
            data_lines = [line.replace("data: ", "") for line in lines if line.startswith("data:")]
            
            assert "[PARTIAL_MATCH]" in data_lines
            assert any("⚠️" in line for line in data_lines)
            assert any("leitos" in line.lower() for line in data_lines)
            assert any("protocolos" in line.lower() for line in data_lines)
```

---

### Test 5: Schema Cache Refresh

**File**: `tests/integration/test_schema_refresh.py`

```python
import pytest
import asyncio
from datetime import timedelta
from src.services.schema_detector_service import SchemaDetectorService

@pytest.mark.asyncio
class TestSchemaRefresh:
    """Test schema cache refresh behavior."""
    
    async def test_schema_refreshes_after_ttl(self, db_connection):
        """
        GIVEN: Schema cached with TTL = 2 seconds
        WHEN: 3 seconds elapse
        THEN: Next request triggers refresh
        """
        SchemaDetectorService._ttl = timedelta(seconds=2)
        SchemaDetectorService._cache = None
        
        # Initial load
        schema1 = await SchemaDetectorService.get_schema()
        timestamp1 = SchemaDetectorService._cache_timestamp
        
        # Wait for TTL to expire
        await asyncio.sleep(3)
        
        # Should trigger refresh
        schema2 = await SchemaDetectorService.get_schema()
        timestamp2 = SchemaDetectorService._cache_timestamp
        
        assert timestamp2 > timestamp1
        assert schema2.last_updated > schema1.last_updated
    
    async def test_schema_detects_new_table(self, db_connection):
        """
        GIVEN: Schema cached
        WHEN: New table added to database AND cache refreshed
        THEN: New table appears in SchemaInfo
        """
        # Initial schema
        schema1 = await SchemaDetectorService.get_schema()
        initial_table_count = len(schema1.tables)
        
        # Add new table to database
        await db_connection.execute(
            "CREATE TABLE test_protocolos (id INTEGER PRIMARY KEY, nome VARCHAR(100))"
        )
        
        # Force refresh
        SchemaDetectorService._cache = None
        schema2 = await SchemaDetectorService.get_schema()
        
        assert len(schema2.tables) == initial_table_count + 1
        assert schema2.get_table("test_protocolos") is not None
        
        # Cleanup
        await db_connection.execute("DROP TABLE test_protocolos")
```

---

## Contract Tests

### Test 6: API Backward Compatibility

**File**: `tests/contract/test_chat_api_backward_compat.py`

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestChatAPIBackwardCompatibility:
    """Ensure no breaking changes to existing API."""
    
    async def test_existing_sse_format_still_works(self):
        """
        GIVEN: Existing client expects 'data:' prefix lines
        WHEN: Answerable question is asked
        THEN: Response format matches existing contract
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/v1/chat/stream",
                params={"session_id": "test", "prompt": "Quantos leitos?"}
            )
            
            lines = response.text.strip().split("\n")
            
            # All lines should start with 'data:' (SSE format)
            non_empty_lines = [line for line in lines if line.strip()]
            assert all(line.startswith("data:") for line in non_empty_lines)
            
            # Must end with [DONE]
            assert "data: [DONE]" in lines
    
    async def test_old_clients_can_ignore_new_markers(self):
        """
        GIVEN: Old client ignores unknown SSE event types
        WHEN: Smart response includes new markers like [SMART_RESPONSE]
        THEN: Client can still parse the response by ignoring unknown markers
        """
        # This test validates that new markers are just data lines
        # and don't break SSE parsing (no new event types, just data)
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/v1/chat/stream",
                params={"session_id": "test", "prompt": "Quais protocolos?"}
            )
            
            lines = response.text.strip().split("\n")
            data_lines = [line for line in lines if line.startswith("data:")]
            
            # Verify all markers are just data lines (not event types)
            assert all(":" in line for line in data_lines)  # 'data:' prefix
            # No 'event:' lines introduced (would break old clients)
            assert not any(line.startswith("event:") for line in lines)
```

---

## Performance Benchmarks

### Test 7: Performance Targets

**File**: `tests/performance/test_benchmarks.py`

```python
import pytest
import time
from src.services.schema_detector_service import SchemaDetectorService
from src.services.question_analyzer_service import QuestionAnalyzerService

class TestPerformanceBenchmarks:
    """Validate performance targets from spec."""
    
    @pytest.mark.asyncio
    async def test_schema_detection_cached_under_100ms(self):
        """
        GIVEN: Schema already cached
        WHEN: get_schema() is called
        THEN: Returns in < 100ms
        """
        # Warm up cache
        await SchemaDetectorService.get_schema()
        
        # Measure
        start = time.perf_counter()
        schema = await SchemaDetectorService.get_schema()
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 100, f"Cached schema took {duration_ms:.2f}ms (target: <100ms)"
    
    @pytest.mark.asyncio
    async def test_schema_detection_fresh_under_500ms(self, db_connection):
        """
        GIVEN: Empty cache
        WHEN: get_schema() is called
        THEN: Returns in < 500ms (including DB query)
        """
        SchemaDetectorService._cache = None
        
        start = time.perf_counter()
        schema = await SchemaDetectorService.get_schema()
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 500, f"Fresh schema took {duration_ms:.2f}ms (target: <500ms)"
    
    def test_question_analysis_under_500ms(self, sample_schema):
        """
        GIVEN: Question to analyze
        WHEN: analyze_question() is called
        THEN: Returns in < 500ms
        """
        question = "Quantos leitos e atendimentos e especialidades temos?"
        
        start = time.perf_counter()
        analysis = QuestionAnalyzerService.analyze_question(question, sample_schema)
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 500, f"Analysis took {duration_ms:.2f}ms (target: <500ms)"
    
    def test_complete_smart_response_under_1_second(self, sample_schema):
        """
        GIVEN: Unanswerable question
        WHEN: Full analysis + suggestion generation
        THEN: Completes in < 1 second
        """
        question = "Quais protocolos de isolamento existem?"
        
        start = time.perf_counter()
        
        # Full flow
        analysis = QuestionAnalyzerService.analyze_question(question, sample_schema)
        response = SuggestionGeneratorService.generate_smart_response(analysis, sample_schema)
        
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 1000, f"Full flow took {duration_ms:.2f}ms (target: <1000ms)"
```

---

## Running Tests

### Run All Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Contract tests only
pytest tests/contract/ -v

# Performance benchmarks
pytest tests/performance/ -v -s
```

### Run Tests in Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw tests/ -- -v
```

---

## Success Criteria Validation

After implementation, verify all spec criteria are met:

| Criteria | Target | Test File | Status |
|----------|--------|-----------|--------|
| Question Detection Accuracy | 90%+ correct identification in <500ms | `test_question_analyzer_service.py` | ⏳ |
| User Understanding | 85%+ understand explanation | Manual user testing | ⏳ |
| Suggestion Relevance | 70%+ suggestions relevant | `test_suggestion_generator_service.py` | ⏳ |
| System Adaptability | Detects schema changes in <60 min | `test_schema_refresh.py` | ⏳ |
| Response Time | Complete analysis in <1s | `test_benchmarks.py` | ⏳ |
| False Positives | <5% answerable questions rejected | `test_smart_detection_flow.py` | ⏳ |

---

## Next Steps

1. ✅ **Test fixtures defined**
2. ⏳ **Implement services to pass tests** (TDD red → green → refactor)
3. ⏳ **Run tests and iterate until all pass**
4. ⏳ **Performance optimization if benchmarks fail**
5. ⏳ **User acceptance testing for subjective criteria**

---

**Quickstart Status**: ✅ COMPLETE  
**Ready for**: Implementation (follow TDD approach)

