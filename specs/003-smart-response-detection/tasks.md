# Tasks: Smart Response Detection

**Feature**: 003-smart-response-detection  
**Input**: Design documents from `/specs/003-smart-response-detection/`  
**Prerequisites**: ✅ plan.md, ✅ spec.md, ✅ research.md, ✅ data-model.md, ✅ contracts/api.yaml, ✅ quickstart.md

**Tests**: Included (TDD approach as defined in quickstart.md)

**Organization**: Tasks are grouped by user story/functional requirement to enable independent implementation and testing.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story/requirement this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `apps/backend-fastapi/src/`, `apps/backend-fastapi/tests/`
- **Config**: `apps/backend-fastapi/config/`
- **Domain Models**: `apps/backend-fastapi/src/domain/`
- **Services**: `apps/backend-fastapi/src/services/`
- **API Routes**: `apps/backend-fastapi/src/api/routes/`

## Verificações Constitucionais

- [x] Dados clínicos protegidos: Opera apenas em metadados (nomes de tabelas/colunas), não em dados de pacientes
- [x] Auditoria: Reutiliza `audit_logger.py` existente para decisões de análise
- [x] Evidências/Testes: 28 testes TDD definidos em quickstart.md antes da implementação
- [x] Interoperabilidade: APIs internas, sem breaking changes, formato SSE existente preservado
- [x] Observabilidade/Resiliência: Feature flag, circuit breaker (degraded mode), métricas definidas

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and configuration files

- [x] T001 Create synonym configuration file at `apps/backend-fastapi/config/synonyms.json` with initial mappings from research.md
- [x] T002 [P] Add configuration variables to `apps/backend-fastapi/src/config.py` (ENABLE_SMART_DETECTION, CONFIDENCE_THRESHOLD, SIMILARITY_THRESHOLD, SCHEMA_CACHE_TTL_SECONDS, SYNONYMS_FILE_PATH)
- [x] T003 [P] Create test fixtures directory and base conftest at `apps/backend-fastapi/tests/conftest.py` with sample_schema and synonyms_dict fixtures

---

## Phase 2: Foundational (Domain Models)

**Purpose**: Core data models that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Create `SchemaInfo` model in `apps/backend-fastapi/src/domain/schema_info.py` with methods: get_table(), get_all_entities(), find_similar_tables()
- [x] T005 [P] Create `TableInfo` model in `apps/backend-fastapi/src/domain/schema_info.py` with computed properties: column_count, nullable_columns, numeric_columns, has_status_column()
- [x] T006 [P] Create `ColumnInfo` model in `apps/backend-fastapi/src/domain/schema_info.py` with properties: is_numeric, is_text, is_temporal
- [x] T007 [P] Create `QuestionIntent` enum and `QuestionAnalysis` model in `apps/backend-fastapi/src/domain/question_analysis.py` with validation
- [x] T008 [P] Create `SmartResponse` model in `apps/backend-fastapi/src/domain/question_analysis.py` with format_for_streaming() method

**Checkpoint**: All domain models created - service implementation can now begin

---

## Phase 3: User Story 1 - Schema Detection and Caching (FR1) 🎯 MVP Foundation

**Goal**: System automatically detects and caches PostgreSQL schema with configurable TTL

**Independent Test**: 
```python
schema = await SchemaDetectorService.get_schema()
assert len(schema.tables) > 0
assert schema.get_table("leitos") is not None
```

**Priority**: P1 (Foundational - blocks all other user stories)

### Tests for User Story 1 (TDD - Write First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Create unit test file `apps/backend-fastapi/tests/unit/test_schema_detector_service.py` with test_detect_schema_from_database()
- [x] T010 [P] [US1] Add test_cache_returns_same_instance_within_ttl() to test_schema_detector_service.py
- [x] T011 [P] [US1] Add test_cache_refreshes_after_ttl_expiration() to test_schema_detector_service.py
- [x] T012 [P] [US1] Add test_graceful_degradation_on_db_failure() to test_schema_detector_service.py
- [x] T013 [P] [US1] Add test_concurrent_cache_refresh_uses_lock() to test_schema_detector_service.py

### Implementation for User Story 1

- [x] T014 [US1] Implement `SchemaDetectorService` class in `apps/backend-fastapi/src/services/schema_detector_service.py` with async get_schema() method
- [x] T015 [US1] Implement _detect_schema() private method with optimized single-query approach from research.md
- [x] T016 [US1] Add in-memory cache with asyncio.Lock for thread-safe writes
- [x] T017 [US1] Implement TTL expiration logic and automatic refresh
- [x] T018 [US1] Add degraded mode handling (use stale cache on DB failure)
- [x] T019 [US1] Add logging for schema detection success/failure and cache age

**Checkpoint**: Schema detection fully functional - can detect and cache schema with automatic refresh

---

## Phase 4: User Story 2 - Question Analysis and Confidence (FR2, FR3, FR4) 🎯 MVP Core

**Goal**: Extract entities from questions, map to schema, calculate confidence score

**Independent Test**:
```python
analysis = QuestionAnalyzerService.analyze_question("Quantos leitos?", schema)
assert analysis.can_answer is True
assert analysis.confidence_score >= 0.70
```

**Priority**: P1 (Core MVP functionality)

**Dependencies**: Depends on US1 (SchemaDetectorService)

### Tests for User Story 2 (TDD - Write First)

- [x] T020 [P] [US2] Create unit test file `apps/backend-fastapi/tests/unit/test_question_analyzer_service.py` with test_extract_entities_removes_stop_words()
- [x] T021 [P] [US2] Add test_synonym_mapping_applied() to test_question_analyzer_service.py
- [x] T022 [P] [US2] Add test_analyze_question_high_confidence() to test_question_analyzer_service.py
- [x] T023 [P] [US2] Add test_analyze_question_low_confidence() to test_question_analyzer_service.py
- [x] T024 [P] [US2] Add test_analyze_question_partial_match() to test_question_analyzer_service.py
- [x] T025 [P] [US2] Add test_similarity_matching() to test_question_analyzer_service.py
- [x] T026 [P] [US2] Add test_intent_detection_count(), test_intent_detection_list(), test_intent_detection_aggregate() to test_question_analyzer_service.py

### Implementation for User Story 2

- [x] T027 [US2] Create `SynonymMapper` class in `apps/backend-fastapi/src/services/question_analyzer_service.py` to load and cache synonyms from JSON
- [x] T028 [US2] Implement extract_entities() method with Portuguese stop words from research.md
- [x] T029 [US2] Implement detect_intent() method to classify question type (COUNT, LIST, AGGREGATE, etc.)
- [x] T030 [US2] Implement map_entities_to_schema() method using difflib.SequenceMatcher from research.md
- [x] T031 [US2] Implement calculate_confidence_score() method with weighted formula (70% exact + 30% similarity)
- [x] T032 [US2] Implement analyze_question() orchestration method that combines all steps
- [x] T033 [US2] Add logging for entity extraction, mapping results, and confidence calculations

**Checkpoint**: Question analysis fully functional - can determine if question is answerable with high accuracy

---

## Phase 5: User Story 3 - Smart Response and Suggestions (FR5, FR6) 🎯 MVP User-Facing

**Goal**: Generate helpful responses with explanations and alternative question suggestions when question is unanswerable

**Independent Test**:
```python
response = SuggestionGeneratorService.generate_smart_response(analysis, schema)
assert response.can_answer is False
assert len(response.suggestions) == 3
assert "não está disponível" in response.message
```

**Priority**: P1 (MVP - user-visible feature)

**Dependencies**: Depends on US2 (QuestionAnalyzerService)

### Tests for User Story 3 (TDD - Write First)

- [x] T034 [P] [US3] Create unit test file `apps/backend-fastapi/tests/unit/test_suggestion_generator_service.py` with test_generate_smart_response_unanswerable()
- [x] T035 [P] [US3] Add test_suggestions_are_diverse() to test_suggestion_generator_service.py
- [x] T036 [P] [US3] Add test_suggestions_prioritize_important_tables() to test_suggestion_generator_service.py
- [x] T037 [P] [US3] Add test_partial_match_response_includes_both_found_and_not_found() to test_suggestion_generator_service.py

### Implementation for User Story 3

- [x] T038 [US3] Create `SuggestionGeneratorService` class in `apps/backend-fastapi/src/services/suggestion_generator_service.py`
- [x] T039 [US3] Implement generate_message() method to create explanation based on missing entities
- [x] T040 [US3] Implement generate_suggestions() method with templates (COUNT, LIST, STATUS, AGGREGATION) from spec
- [x] T041 [US3] Implement prioritization logic: prefer tables from leitos, atendimentos, especialidades (priority tables from research.md)
- [x] T042 [US3] Implement generate_smart_response() orchestration method that combines message + entities + suggestions
- [x] T043 [US3] Add support for partial match responses (some entities found, others not)
- [x] T044 [US3] Add logging for suggestion generation decisions

**Checkpoint**: Smart responses fully functional - system can provide helpful feedback when questions are unanswerable

---

## Phase 6: User Story 4 - Integration with Chat API (FR7, FR8) 🎯 MVP Complete

**Goal**: Integrate smart detection into existing SQL agent and chat streaming endpoint

**Independent Test**:
```python
response = await client.get("/v1/chat/stream?prompt=Quais protocolos?")
assert "[SMART_RESPONSE]" in response.text
assert "[DONE]" in response.text
```

**Priority**: P1 (MVP integration - connects all pieces)

**Dependencies**: Depends on US1, US2, US3 (all services)

### Tests for User Story 4 (TDD - Write First)

- [x] T045 [P] [US4] Create integration test file `apps/backend-fastapi/tests/integration/test_smart_detection_flow.py` with test_unanswerable_question_returns_smart_response()
- [x] T046 [P] [US4] Add test_answerable_question_proceeds_normally() to test_smart_detection_flow.py
- [x] T047 [P] [US4] Add test_partial_match_shows_warning() to test_smart_detection_flow.py
- [x] T048 [P] [US4] Create contract test file `apps/backend-fastapi/tests/contract/test_chat_api_backward_compat.py` with test_existing_sse_format_still_works()
- [x] T049 [P] [US4] Add test_old_clients_can_ignore_new_markers() to test_chat_api_backward_compat.py

### Implementation for User Story 4

- [x] T050 [US4] Modify `apps/backend-fastapi/src/agents/sql_agent.py`: Add pre-generation analysis call to QuestionAnalyzerService.analyze_question()
- [x] T051 [US4] In sql_agent.py: Add conditional logic - if can_answer is False, skip SQL generation and return smart response marker
- [x] T052 [US4] In sql_agent.py: Add handling for partial matches (log warning, proceed with SQL but note missing entities)
- [x] T053 [US4] Modify `apps/backend-fastapi/src/api/routes/chat.py`: Add import for SuggestionGeneratorService
- [x] T054 [US4] In chat.py generate() function: Detect smart response marker from sql_agent and call SuggestionGeneratorService
- [x] T055 [US4] In chat.py: Implement stream_smart_response() to yield SSE events with [SMART_RESPONSE] marker, message, entities, suggestions
- [x] T056 [US4] In chat.py: Add handling for [PARTIAL_MATCH] marker to show warning before SQL results
- [x] T057 [US4] Add logging to audit_logger for smart response decisions (question_id, entities_found, entities_missing, confidence, decision)

**Checkpoint**: Full integration complete - smart detection works end-to-end in chat API

---

## Phase 7: Schema Info API Endpoint (New Feature - Optional Enhancement)

**Goal**: Provide API endpoint to inspect current cached schema

**Independent Test**:
```python
response = await client.get("/v1/schema/info")
assert response.status_code == 200
assert "tables" in response.json()
```

**Priority**: P2 (Nice to have, not blocking MVP)

**Dependencies**: Depends on US1 (SchemaDetectorService)

- [x] T058 [P] [US5] Create new route file `apps/backend-fastapi/src/api/routes/schema.py`
- [x] T059 [US5] Implement `GET /v1/schema/info` endpoint that returns SchemaInfo from SchemaDetectorService
- [x] T060 [US5] Add X-Cache-Age and X-Schema-Version response headers
- [x] T061 [US5] Handle 503 response when in degraded mode (stale cache)
- [x] T062 [US5] Register schema routes in `apps/backend-fastapi/src/api/main.py`
- [x] T063 [P] [US5] Add integration test for schema endpoint in `apps/backend-fastapi/tests/integration/test_schema_api.py`

**Checkpoint**: Schema inspection API available for debugging and monitoring

---

## Phase 8: Schema Refresh and Adaptation (FR1 Extended)

**Goal**: Automatic schema refresh when database changes are detected

**Independent Test**:
```python
# Add new table
await db.execute("CREATE TABLE test_protocolos (...)")
# Wait for TTL
await asyncio.sleep(ttl + 1)
# Verify detection
schema = await SchemaDetectorService.get_schema()
assert schema.get_table("test_protocolos") is not None
```

**Priority**: P2 (Adaptive behavior, enhances robustness)

**Dependencies**: Depends on US1 (SchemaDetectorService)

- [x] T064 [P] [US6] Create integration test file `apps/backend-fastapi/tests/integration/test_schema_refresh.py` with test_schema_refreshes_after_ttl()
- [x] T065 [P] [US6] Add test_schema_detects_new_table() to test_schema_refresh.py
- [x] T066 [US6] Enhance SchemaDetectorService to log schema version changes on refresh
- [x] T067 [US6] Add metrics for schema_cache_age_seconds and schema_table_count
- [x] T068 [US6] Add alert logic: if schema detection fails > 3 consecutive times, log critical error
- [x] T069 [US6] Document schema refresh behavior in schema_detector_service.py docstrings

**Checkpoint**: Schema automatically adapts to database changes within configured TTL

---

## Phase 9: Performance Benchmarks and Optimization

**Goal**: Validate all performance targets from spec are met

**Independent Test**:
```python
start = time.perf_counter()
schema = await SchemaDetectorService.get_schema()  # cached
duration_ms = (time.perf_counter() - start) * 1000
assert duration_ms < 100  # Target: < 100ms for cached schema
```

**Priority**: P2 (Performance validation)

**Dependencies**: Depends on all previous phases

- [x] T070 [P] [US7] Create performance test file `apps/backend-fastapi/tests/performance/test_benchmarks.py` with test_schema_detection_cached_under_100ms()
- [x] T071 [P] [US7] Add test_schema_detection_fresh_under_500ms() to test_benchmarks.py
- [x] T072 [P] [US7] Add test_question_analysis_under_500ms() to test_benchmarks.py
- [x] T073 [P] [US7] Add test_complete_smart_response_under_1_second() to test_benchmarks.py
- [x] T074 [US7] Run benchmarks and profile slow code paths if any test fails
- [x] T075 [US7] Optimize schema detection query if fresh detection > 500ms (add indexes or query hints)
- [x] T076 [US7] Optimize entity extraction if analysis > 500ms (cache stop words set, optimize string operations)

**Checkpoint**: All performance targets validated and met

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [x] T077 [P] Add comprehensive docstrings to all service methods with examples
- [x] T078 [P] Add type hints to all function signatures (already using Pydantic, ensure consistency)
- [x] T079 [P] Update `apps/backend-fastapi/README.md` with smart detection feature documentation
- [x] T080 [P] Create migration guide documenting new environment variables (CONFIDENCE_THRESHOLD, SCHEMA_CACHE_TTL_SECONDS, etc.)
- [x] T081 Run all tests from quickstart.md and verify 100% pass rate
- [x] T082 Verify backward compatibility: existing chat clients still work without changes
- [x] T083 [P] Add observability metrics to Prometheus/Grafana (smart_response_analysis_duration_ms, schema_cache_hits, unanswerable_questions_count)
- [x] T084 [P] Create runbook for schema detection failures at `docs/runbooks/smart-detection-recovery.md`
- [x] T085 Code review and refactoring for consistency across services
- [x] T086 Final integration test: Run through all 4 user scenarios from spec.md manually

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - MVP Foundation
- **User Story 2 (Phase 4)**: Depends on Foundational + US1 - MVP Core
- **User Story 3 (Phase 5)**: Depends on Foundational + US2 - MVP User-Facing
- **User Story 4 (Phase 6)**: Depends on Foundational + US1 + US2 + US3 - MVP Complete
- **User Story 5 (Phase 7)**: Depends on US1 - Optional Enhancement (can be done in parallel with US2-US4 or after)
- **User Story 6 (Phase 8)**: Depends on US1 - Enhancement (can be done after MVP)
- **User Story 7 (Phase 9)**: Depends on all implementations - Performance validation
- **Polish (Phase 10)**: Depends on all desired features - Final cleanup

### User Story Dependencies

```
Setup → Foundational → US1 (Schema Detection)
                        ├→ US2 (Question Analysis)
                        │   └→ US3 (Smart Response)
                        │       └→ US4 (Integration) ← MVP COMPLETE
                        ├→ US5 (Schema API) [optional]
                        └→ US6 (Schema Refresh) [enhancement]
                                └→ US7 (Performance) [validation]
                                    └→ Polish
```

### Within Each User Story (TDD Pattern)

1. Tests FIRST (write tests that FAIL)
2. Models (domain entities)
3. Services (business logic)
4. Integration (connect to API)
5. Validation (verify story works independently)

### Parallel Opportunities

#### Phase 1 (Setup)
- T001, T002, T003 can run in parallel (different files)

#### Phase 2 (Foundational)
- T004, T005, T006, T007, T008 can run in parallel (different models in same/different files)

#### Phase 3 (US1) - Tests
- T009, T010, T011, T012, T013 can run in parallel (different test methods, same file)

#### Phase 4 (US2) - Tests
- T020, T021, T022, T023, T024, T025, T026 can run in parallel (different test methods)

#### Phase 5 (US3) - Tests
- T034, T035, T036, T037 can run in parallel (different test methods)

#### Phase 6 (US4) - Tests
- T045, T046, T047, T048, T049 can run in parallel (different test files/methods)

#### Phase 7 (US5)
- T058 independent, T063 can start after T062

#### Phase 8 (US6)
- T064, T065 can run in parallel (different test methods)

#### Phase 9 (US7)
- T070, T071, T072, T073 can run in parallel (different test methods)

#### Phase 10 (Polish)
- T077, T078, T079, T080, T083, T084 can run in parallel (different files/docs)

---

## Parallel Example: User Story 1 (Schema Detection)

```bash
# Step 1: Launch all tests in parallel (TDD - fail first)
parallel_tasks=(
  "T009: test_detect_schema_from_database()"
  "T010: test_cache_returns_same_instance_within_ttl()"
  "T011: test_cache_refreshes_after_ttl_expiration()"
  "T012: test_graceful_degradation_on_db_failure()"
  "T013: test_concurrent_cache_refresh_uses_lock()"
)

# Step 2: Implement service sequentially (T014-T019)
# Step 3: Run tests again - should all pass
```

---

## Parallel Example: User Story 4 (Integration)

```bash
# Tests can run in parallel:
parallel_tasks=(
  "T045: test_unanswerable_question_returns_smart_response()"
  "T046: test_answerable_question_proceeds_normally()"
  "T047: test_partial_match_shows_warning()"
  "T048: test_existing_sse_format_still_works()"
  "T049: test_old_clients_can_ignore_new_markers()"
)

# Implementation runs sequentially (T050-T057) due to same file modifications
```

---

## Implementation Strategy

### MVP First (Phases 1-6 Only)

1. ✅ Complete Phase 1: Setup (~30 min)
2. ✅ Complete Phase 2: Foundational (~1 hour)
3. ✅ Complete Phase 3: US1 - Schema Detection (~4 hours)
4. ✅ Complete Phase 4: US2 - Question Analysis (~4 hours)
5. ✅ Complete Phase 5: US3 - Smart Responses (~3 hours)
6. ✅ Complete Phase 6: US4 - Integration (~4 hours)
7. **STOP and VALIDATE**: Test all 4 scenarios from spec.md
8. Deploy MVP (core functionality complete)

**Total MVP Estimate**: ~16-20 hours (2-3 days)

### Incremental Delivery After MVP

1. MVP Complete (US1-US4) → Foundation + Core + Integration working
2. Add Phase 7: US5 - Schema API (~2 hours) → Debugging/monitoring capability
3. Add Phase 8: US6 - Schema Refresh (~2 hours) → Adaptive behavior
4. Add Phase 9: US7 - Performance (~3 hours) → Validation and optimization
5. Add Phase 10: Polish (~4 hours) → Production-ready

**Total with Enhancements**: ~27-31 hours (3-4 days)

### Parallel Team Strategy

With 2 developers after Foundational phase:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. Once Foundational is done:
   - **Developer A**: US1 (Schema Detection) + US3 (Smart Responses)
   - **Developer B**: US2 (Question Analysis) + US4 (Integration)
   - Note: US4 needs US1+US2+US3, so Developer B helps finish US1/US3 first
3. **Both**: US5-US7 in parallel, then Polish together

**Parallel Team Estimate**: ~12-16 hours (1.5-2 days)

---

## Task Count Summary

| Phase | Task Count | Parallelizable | Estimated Time |
|-------|------------|----------------|----------------|
| Phase 1: Setup | 3 | 2 | 30 min |
| Phase 2: Foundational | 5 | 5 | 1 hour |
| Phase 3: US1 - Schema Detection | 11 | 5 (tests) | 4 hours |
| Phase 4: US2 - Question Analysis | 14 | 7 (tests) | 4 hours |
| Phase 5: US3 - Smart Responses | 11 | 4 (tests) | 3 hours |
| Phase 6: US4 - Integration | 13 | 5 (tests) | 4 hours |
| Phase 7: US5 - Schema API | 6 | 2 | 2 hours |
| Phase 8: US6 - Schema Refresh | 6 | 2 | 2 hours |
| Phase 9: US7 - Performance | 7 | 4 (tests) | 3 hours |
| Phase 10: Polish | 10 | 6 | 4 hours |
| **TOTAL** | **86 tasks** | **42 parallelizable** | **27-31 hours** |

---

## Notes

- **[P] tasks**: Different files or independent test methods, no dependencies within phase
- **[Story] labels**: Map tasks to user stories for traceability (US1-US7)
- **TDD approach**: All tests written BEFORE implementation (must fail first)
- **Independent stories**: Each user story (US1-US4) can be tested independently after completion
- **MVP scope**: Phases 1-6 deliver complete core functionality (US1-US4)
- **Incremental value**: Each phase after MVP adds optional enhancements
- **Checkpoint validation**: Test story independently at each checkpoint before proceeding
- **Commit strategy**: Commit after each task or after completing all tests for a story
- **Error handling**: Each service includes error handling and logging as part of implementation tasks
- **Performance**: Phase 9 validates all targets from spec Success Criteria

---

## Success Metrics (from spec.md)

| Metric | Target | Validation Task |
|--------|--------|-----------------|
| Question Detection Accuracy | 90%+ | T022, T023 (high/low confidence tests) |
| Response Time (Analysis) | < 1 second | T073 (complete smart response benchmark) |
| Schema Detection (Cached) | < 100ms | T070 (cached schema benchmark) |
| Schema Detection (Fresh) | < 500ms | T071 (fresh schema benchmark) |
| False Positives | < 5% | T046 (answerable questions proceed normally) |
| Suggestion Relevance | 70%+ | T035, T036 (diverse and prioritized suggestions) |
| System Adaptability | < 60 min | T065 (schema detects new table after TTL) |

---

**Tasks.md Status**: ✅ COMPLETE  
**Total Tasks**: 86  
**MVP Tasks**: 57 (Phases 1-6)  
**Parallelizable**: 42 tasks (~49%)  
**Ready for**: Implementation (`/speckit.implement` or manual execution)

