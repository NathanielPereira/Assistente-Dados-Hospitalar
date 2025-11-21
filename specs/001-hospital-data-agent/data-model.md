# Data Model — Assistente de Dados Hospitalar IA

## QuerySession
- **Descrição**: Registro agregador de cada interação (chat, SQL assistido).
- **Campos**:
  - `id` (UUID) — chave primária.
  - `user_id` (UUID) — referência ao usuário autenticado.
  - `role` (enum: CONSULTOR, ANALISTA, COMPLIANCE).
  - `question` (text) — prompt original.
  - `sql_text` (text, nullable) — consulta aprovada.
  - `rag_sources` (jsonb) — lista de documentos citados com hashes.
  - `response_stream` (jsonb) — chunks streamados + timestamps.
  - `status` (enum: PENDING, RUNNING, COMPLETED, DEGRADED, BLOCKED).
  - `mode` (enum: CHAT, SQL_ASSIST, AUDIT_EXPORT).
  - `created_at`, `completed_at`.
  - `slo_latency_ms` (int) — medição registrada.
- **Regras/Validações**:
  - `sql_text` obrigatório em modo SQL_ASSIST.
  - `response_stream` precisa citar pelo menos um documento ou métrica.
- **Relacionamentos**:
  - 1:N com `AuditEntry` (cada sessão gera ≥1 evento).
  - 1:N com `ComplianceFinding`.

## AuditEntry
- **Descrição**: Evento imutável que armazena trilhas de auditoria.
- **Campos**:
  - `id` (UUID), `query_session_id` (FK).
  - `event_type` (enum: PROMPT, SQL_EXECUTED, RAG_FETCH, ALERT, EXPORT).
  - `input_hash`, `output_hash` (SHA-256).
  - `legal_basis` (enum fictício: CONSENT_DEMO, LEGIT_INTEREST_DEMO).
  - `export_uri` (text) — local do CSV/JSON.
  - `immutable_storage_pointer` (URI S3 versionada).
  - `created_at`.
- **Regras**:
  - Inserções apenas append-only.
  - `legal_basis` obrigatório em todos os eventos.

## DocumentCorpus
- **Descrição**: Conjunto de documentos fictícios usados pelo RAG.
- **Campos**:
  - `id`, `title`, `category` (PROTOCOLO, LAUDO, REGULAMENTO).
  - `confidentiality` (enum: PÚBLICO, INTERNO, RESTRITO_DEMO).
  - `source_hash`, `ingested_at`, `version`.
  - `storage_uri` (S3/MinIO).
  - `embedding_vector` (externo, referenciar índice).
- **Regras**:
  - `confidentiality` controla quem pode ver trechos.
  - Alterações criam nova `version`, mantendo histórico.

## DataConnectivityProfile
- **Descrição**: Configura como o backend acessa NeonDB.
- **Campos**:
  - `id`, `name`, `connection_string`, `allowed_schemas`, `masking_rules`.
  - `max_rows`, `timeout_ms`, `read_only` (bool), `feature_flags`.
  - `created_by`, `approved_by`.
- **Regras**:
  - Perfis devem ser read-only por padrão.
  - `masking_rules` definem colunas sensíveis obrigatórias.

## ComplianceFinding
- **Descrição**: Resultados de verificações LGPD/HIPAA e observabilidade.
- **Campos**:
  - `id`, `query_session_id`, `severity` (LOW/MEDIUM/HIGH), `description`.
  - `resolved` (bool), `playbook_step` (texto curto), `created_at`, `resolved_at`.
- **Regras**:
  - Criada automaticamente em falhas de política (ex.: tentativa de identificar paciente).
  - Deve referenciar `playbook_step` aprovado.

## Relationships (Resumo)
- `QuerySession` 1..* `AuditEntry`
- `QuerySession` 1..* `ComplianceFinding`
- `AuditEntry` n..1 `DataConnectivityProfile`
- `QuerySession` n..* `DocumentCorpus` (via tabela de junção `query_session_documents`)


