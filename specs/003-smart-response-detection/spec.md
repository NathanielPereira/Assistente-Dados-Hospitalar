# Feature Specification: Smart Response Detection

## Overview

**Feature Name**: Smart Response Detection  
**Short Name**: smart-response-detection  
**Feature Number**: 003  
**Created**: 2024-11-26  
**Status**: Draft

## Clarifications

### Session 2024-11-26

- Q: When schema detection fails (database offline, permission error), what should be the system behavior? → A: System uses last valid schema in cache and continues operating in degraded mode
- Q: When no tables in schema relate to the original question context, how should the 3 suggestions be prioritized? → A: Show suggestions from most consulted/important tables (leitos, atendimentos, ocupação UTI)
- Q: When some entities are found but others are not (e.g., 1 of 2 entities in question), what should be the behavior? → A: Respond with available data and inform which entities were not found

### Purpose

Enable the hospital data assistant to intelligently detect when user questions cannot be answered with available database data, provide clear explanations, and suggest relevant alternative questions based on the current database schema.

### Problem Statement

Currently, when users ask questions about data that doesn't exist in the database (e.g., "What protocol should I apply for isolation?"), the system:
- Returns irrelevant data from random tables
- Provides generic error messages without context
- Does not help users understand what information IS available
- Does not suggest alternative questions that can be answered

This creates a poor user experience and wastes time as users don't know what questions they CAN ask.

### Success Criteria

1. **Question Detection Accuracy**: System correctly identifies 90%+ of questions that cannot be answered within 500ms
2. **User Understanding**: 85%+ of users understand why their question cannot be answered from the explanation provided
3. **Suggestion Relevance**: 70%+ of suggested alternative questions are relevant to user's original intent
4. **System Adaptability**: System automatically detects and adapts to schema changes within 60 minutes without code changes
5. **Response Time**: Complete analysis and suggestion generation completes in under 1 second
6. **False Positives**: Less than 5% of answerable questions are incorrectly rejected

## User Scenarios & Testing

### Scenario 1: Question About Non-Existent Data

**Actor**: Hospital administrator  
**Context**: User wants to know about clinical protocols which are not in the database

**User Flow**:
1. User asks: "What protocol should I apply for isolation?"
2. System analyzes question and detects entities: "protocol", "isolation"
3. System compares entities against current database schema
4. System finds no matching tables or columns
5. System responds with:
   - Clear message: "Information about 'clinical protocols' is not available in the system"
   - List of available data categories: "Available information: beds, appointments, specialties, procedures"
   - 3 relevant suggestions:
     - "How many beds are available?"
     - "What is the ICU occupancy rate?"
     - "Which specialties are registered?"

**Acceptance Criteria**:
- System responds within 1 second
- Message clearly states what is NOT available
- At least 2 available data categories are listed
- Exactly 3 alternative questions are suggested
- Suggestions are based on actual database schema

### Scenario 2: Question Using Different Terminology

**Actor**: Nurse  
**Context**: User uses colloquial term "camas" (beds) instead of database term "leitos"

**User Flow**:
1. User asks: "How many camas do we have?"
2. System recognizes "camas" as similar to "leitos" (confidence: 85%)
3. System determines question CAN be answered
4. System provides clarification: "I interpreted your question as referring to 'leitos'"
5. System generates and executes SQL query
6. System returns results with clarification

**Acceptance Criteria**:
- System maps common synonyms to database entities
- Confidence score is calculated and logged
- Clarification is shown when synonym mapping is used
- Question is answered correctly

### Scenario 3: Database Schema Changes

**Actor**: System administrator  
**Context**: New table "protocolos_clinicos" (clinical protocols) is added to database

**User Flow**:
1. Administrator adds new table to database
2. System's schema cache expires (within 1 hour)
3. System automatically detects new table on next request
4. User asks: "What clinical protocols are available?"
5. System now CAN answer this question (previously couldn't)
6. System generates SQL query for new table

**Acceptance Criteria**:
- Schema cache refreshes automatically within 1 hour
- No code changes required to detect new table
- Previously unanswerable questions become answerable
- System logs schema updates

### Scenario 4: Ambiguous Question

**Actor**: Doctor  
**Context**: User asks vague question without specific entities

**User Flow**:
1. User asks: "What information do you have?"
2. System cannot extract specific entities (confidence: 40%)
3. System responds with:
   - Message: "I need more specific information. Please ask about a specific topic."
   - List of all available data categories
   - Examples of well-formed questions for each category

**Acceptance Criteria**:
- System detects low confidence (< 70%)
- Provides helpful guidance for reformulation
- Lists all major data categories
- Provides at least 1 example question per category

## Functional Requirements

### FR1: Automatic Schema Detection

**Description**: System must automatically detect and cache the current PostgreSQL database schema.

**Details**:
- Query `information_schema.tables` and `information_schema.columns` on startup
- Extract: table names, column names, data types, relationships
- Store in memory cache with configurable TTL (default: 1 hour)
- Provide API endpoint to view current schema: `GET /v1/schema/info`
- Log schema updates when cache refreshes

**Acceptance Criteria**:
- Schema detection completes in < 100ms (with cache)
- All public schema tables are discovered
- Column metadata includes: name, type, nullable status
- Cache auto-refreshes after TTL expiration
- Schema changes are detected within 1 hour maximum
- If schema detection fails, system uses last valid cached schema and continues operating in degraded mode
- System logs schema detection failures but does not stop accepting questions

### FR2: Question Entity Extraction

**Description**: System must extract entities (nouns/subjects) mentioned in user's natural language question.

**Details**:
- Parse question text and identify key terms
- Remove common stop words (qual, quantos, o, a, de, para, etc.)
- Extract remaining meaningful terms as potential entities
- Map common synonyms to database terms (e.g., "camas" → "leitos")
- Return list of extracted entities with confidence scores

**Acceptance Criteria**:
- Extracts at least 1 entity from 90%+ of questions
- Correctly maps common synonyms
- Handles singular/plural variations
- Processing completes in < 200ms
- Returns empty list if no entities found (not an error)

### FR3: Entity-to-Schema Mapping

**Description**: System must compare extracted entities against current database schema to determine if question can be answered.

**Details**:
- For each extracted entity:
  - Check for exact match with table names
  - Check for partial match (entity contained in table name or vice versa)
  - Calculate similarity score using string comparison
- Categorize entities as:
  - Found (exists in schema)
  - Not found (does not exist in schema)
  - Similar (high similarity but not exact match)

**Acceptance Criteria**:
- Finds exact matches with 100% accuracy
- Detects partial matches with 85%+ accuracy
- Similarity threshold is configurable (default: 70%)
- Returns categorized entity lists
- Processing completes in < 100ms

### FR4: Confidence Scoring

**Description**: System must calculate confidence score indicating likelihood that question can be answered.

**Details**:
- Base score: ratio of found entities to total extracted entities
- Boost score: add similarity scores for near-matches
- Final confidence: weighted combination (70% base + 30% similarity)
- Confidence threshold: 70% (configurable via environment variable)
- Decision: question CAN be answered if confidence >= threshold AND at least 1 entity found

**Acceptance Criteria**:
- Confidence score is between 0.0 and 1.0
- Score calculation is deterministic (same input = same output)
- Threshold is configurable via `CONFIDENCE_THRESHOLD` env var
- Decision logic correctly implements threshold
- When some entities found but others not, system proceeds with partial answer if confidence >= threshold
- System includes note about which entities were not found in partial answers
- Processing completes in < 50ms

### FR5: Intelligent Response Generation

**Description**: When question cannot be answered, system must generate helpful response with context and suggestions.

**Details**:
Response must include:
1. **Clear explanation**: Why question cannot be answered (specific entities not found)
2. **Available entities**: List of data categories that ARE in the database
3. **Suggestions**: 3 alternative questions that can be answered

Format:
```
✗ "Information about '[entities not found]' is not available in the system"

✓ Available information: [list of table names in user-friendly format]

✓ Suggestions:
  • [Question 1]
  • [Question 2]
  • [Question 3]
```

For partial matches (some entities found, others not):
```
⚠️ "Showing results for '[entities found]'. Information about '[entities not found]' is not available."

[SQL results for available entities]
```

**Acceptance Criteria**:
- Response clearly states what is NOT available
- Lists at least 3 available data categories
- Provides exactly 3 suggestions
- Response is in Portuguese
- Uses user-friendly terminology (not database jargon)
- Generation completes in < 300ms

### FR6: Suggestion Generation

**Description**: System must generate relevant alternative questions based on current database schema.

**Details**:
- Use question templates for each table type:
  - Count: "Quantos {entity} estão cadastrados?"
  - List: "Quais {entity} estão disponíveis?"
  - Status: "Qual a ocupação de {entity}?" (if status column exists)
  - Aggregation: "Qual a média de {field} por {entity}?" (if numeric columns exist)
- Select 3 most relevant suggestions based on:
  - User's original question intent (when related tables exist)
  - Most commonly queried tables (priority fallback: leitos, atendimentos, ocupação UTI)
  - Diversity of suggestion types
- When no tables relate to original context, prioritize suggestions from most important/consulted tables
- Suggestions must be valid questions that system CAN answer

**Acceptance Criteria**:
- Generates exactly 3 suggestions
- Suggestions are based on real database tables
- Suggestions use appropriate templates
- Suggestions are diverse (not all same type)
- At least 1 suggestion relates to user's original intent (when possible)
- Generation completes in < 300ms

### FR7: Integration with SQL Agent

**Description**: System must integrate with existing SQL generation pipeline to intercept questions before SQL is generated.

**Details**:
- Modify `src/agents/sql_agent.py`:
  - Add question analysis step before SQL generation
  - If analysis indicates question cannot be answered (confidence < threshold):
    - Skip SQL generation
    - Return smart response instead
  - If question CAN be answered:
    - Proceed with normal SQL generation
    - Include clarifications if synonym mapping was used

**Acceptance Criteria**:
- Analysis completes before SQL generation
- Low-confidence questions are intercepted
- High-confidence questions proceed normally
- No breaking changes to existing API
- Performance impact < 100ms per request

### FR8: Streaming Response Integration

**Description**: System must integrate with chat streaming endpoint to deliver smart responses.

**Details**:
- Modify `src/api/routes/chat.py`:
  - Stream smart response components sequentially:
    1. Explanation message
    2. Available entities list
    3. Suggestions (one at a time)
  - Use same SSE format as existing responses
  - Include `[DONE]` marker at end

**Acceptance Criteria**:
- Smart responses are streamed (not returned all at once)
- SSE format matches existing implementation
- Client can parse and display responses correctly
- No breaking changes to frontend contract
- Complete response streams in < 2 seconds

## Key Entities

### SchemaInfo

**Purpose**: Represents complete database schema metadata

**Attributes**:
- `tables`: List[TableInfo] - All database tables
- `last_updated`: datetime - When schema was last refreshed
- `version`: str - Schema version identifier

**Methods**:
- `get_table(name: str) -> TableInfo` - Find table by name
- `get_all_entities() -> List[str]` - Get all table names
- `get_all_columns() -> List[str]` - Get all column names (table.column format)

### TableInfo

**Purpose**: Represents metadata for a single database table

**Attributes**:
- `name`: str - Table name
- `columns`: List[ColumnInfo] - Table columns
- `description`: Optional[str] - Table description (from PostgreSQL comments)
- `row_count`: Optional[int] - Number of rows (cached)

### ColumnInfo

**Purpose**: Represents metadata for a single database column

**Attributes**:
- `name`: str - Column name
- `type`: str - PostgreSQL data type
- `nullable`: bool - Whether column allows NULL
- `description`: Optional[str] - Column description (from PostgreSQL comments)

### QuestionAnalysis

**Purpose**: Result of analyzing a user question

**Attributes**:
- `question`: str - Original question text
- `entities_mentioned`: List[str] - Entities extracted from question
- `entities_found_in_schema`: List[str] - Entities that exist in database
- `entities_not_found`: List[str] - Entities that do NOT exist in database
- `confidence_score`: float - Confidence that question can be answered (0.0 to 1.0)
- `intent`: QuestionIntent - Detected intent (aggregation, listing, filtering, etc.)
- `can_answer`: bool - Whether question can be answered
- `reason`: Optional[str] - Why question cannot be answered (if applicable)
- `similar_entities`: Dict[str, float] - Near-match entities with similarity scores

### SmartResponse

**Purpose**: Response for questions that cannot be answered

**Attributes**:
- `can_answer`: bool - Always False for smart responses
- `message`: str - Explanation of why question cannot be answered
- `available_entities`: List[str] - Data categories that ARE available
- `suggestions`: List[str] - Alternative questions that can be answered

## Dependencies & Assumptions

### Dependencies

1. **PostgreSQL Database**: 
   - Must support `information_schema` queries
   - Schema must be relatively stable (not changing every minute)
   
2. **Existing Services**:
   - `src/database.py` - Database connection must support async queries
   - `src/agents/sql_agent.py` - SQL generation service
   - `src/api/routes/chat.py` - Chat streaming endpoint

### Assumptions

1. **Database Schema**:
   - All relevant tables are in `public` schema
   - Table and column names are in Portuguese
   - Tables have reasonable row counts (< 10M rows per table)

2. **Performance**:
   - Schema queries complete in < 100ms
   - Database supports concurrent reads during schema detection
   - Cache memory footprint is acceptable (< 10MB for schema data)

3. **Question Format**:
   - Questions are in Portuguese
   - Questions are well-formed (not complete gibberish)
   - Questions contain at least some identifiable nouns

4. **User Expectations**:
   - Users will read and understand the explanations provided
   - Users find suggestions helpful even if not perfect matches
   - Users accept 1-hour delay for schema change detection

5. **System Context**:
   - Single PostgreSQL database (not multiple databases)
   - Schema changes are infrequent (not real-time)
   - No complex multi-tenant schema isolation required

## Out of Scope

The following are explicitly NOT included in this feature:

1. **Advanced NLP**: No machine learning models, no word embeddings, no semantic similarity beyond simple string matching
2. **Multi-Database Support**: Only single PostgreSQL database, no MySQL/SQLite/etc.
3. **Real-Time Schema Updates**: Schema changes detected within 1 hour, not instantly
4. **Question History**: No tracking of which questions were asked or couldn't be answered
5. **User Feedback Loop**: No mechanism for users to rate suggestion quality
6. **Personalized Suggestions**: Suggestions are same for all users, no personalization
7. **Complex Synonym Dictionary**: Only hardcoded common synonyms, no extensible dictionary
8. **Natural Language Generation**: Response templates are static, not dynamically generated
9. **Multi-Language Support**: Portuguese only, no English/Spanish/etc.
10. **Schema Diff Tracking**: No comparison of schema versions or change notifications

## Notes

### Design Decisions

1. **Cache-First Architecture**: Schema is cached in memory rather than queried on every request to minimize database load and improve performance.

2. **Simple String Matching**: Using basic string comparison (not ML/embeddings) for entity matching to keep system simple, maintainable, and fast.

3. **Configurable Thresholds**: Confidence threshold and cache TTL are environment variables to allow tuning without code changes.

4. **Fail-Open Approach**: When in doubt (medium confidence 60-70%), system attempts to answer rather than reject. This minimizes false negatives at cost of some false positives.

5. **Template-Based Suggestions**: Using predefined question templates rather than NLG to ensure suggestions are always valid and answerable.

### Future Enhancements

Potential improvements for future iterations:

1. **Semantic Similarity**: Use sentence embeddings (e.g., sentence-transformers) for better entity matching
2. **Learning System**: Track which suggestions users actually ask to improve relevance
3. **Schema Documentation**: Allow admins to add descriptions/tags to tables for better suggestions
4. **Multi-Database**: Support analyzing multiple databases or schemas
5. **Real-Time Updates**: WebSocket notifications when schema changes
6. **Synonym Management**: UI for admins to manage custom synonym mappings
7. **Analytics Dashboard**: View metrics on unanswerable questions and suggestion effectiveness

### Technical Considerations

1. **Thread Safety**: Schema cache must be thread-safe for concurrent requests
2. **Memory Management**: Consider cache size limits if schema becomes very large (100+ tables)
3. **Logging**: All analysis decisions should be logged for debugging and improvement
4. **Error Handling**: Schema detection failures should not break existing functionality
5. **Testing**: Need comprehensive test cases for edge cases (empty schema, all entities not found, etc.)

