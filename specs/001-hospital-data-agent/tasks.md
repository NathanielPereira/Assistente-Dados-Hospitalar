---

description: "Task list para o Assistente de Dados Hospitalar IA"
---

# Tasks: Assistente de Dados Hospitalar IA

**Input**: Design documents de `/specs/001-hospital-data-agent/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/http.yaml, quickstart.md  
**Tests**: Inclusos quando necessários para validar fluxos críticos (chat streaming, SQL assistido, auditoria).  
**Organização**: Tarefas agrupadas por história de usuário para permitir implementação e testes independentes.

## Verificações Constitucionais (preencher antes de distribuir tarefas)

- [ ] Dados clínicos protegidos: confirmar que T004, T006, T007, T009 e T030 cobrem criptografia, mascaramento e revisões de privacidade.
- [ ] Auditoria: garantir que T005, T015, T020, T026 e T028 criem eventos imutáveis e exportações rastreáveis.
- [ ] Evidências/Testes: assegurar que T012, T013, T021 e T022 tenham datasets e suites definidos antes da implementação.
- [ ] Interoperabilidade: validar que T006, T016, T023 e T028 versionam contratos (REST, exportos, conectores).
- [ ] Observabilidade/Resiliência: confirmar que T010, T019, T025, T029 e T031 entregam métricas, alertas, flags e playbooks.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicializar estrutura multi-app, ferramentas e governança.

- [x] T001 Criar estrutura multi-app (`apps/frontend-next`, `apps/backend-fastapi`, `infra/`, `shared/`) alinhada ao plano em `apps/` e `infra/`.
- [x] T002 Configurar workspace PNPM (root `package.json`, `pnpm-workspace.yaml`) incluindo app `apps/frontend-next`.
- [x] T003 Inicializar projeto Python com Poetry em `apps/backend-fastapi/pyproject.toml` e dependências básicas (FastAPI, LangChain, pydantic).
- [x] T004 Definir políticas de segurança/privacidade em `docs/runbooks/policies.md` incluindo bases legais fictícias e controles de criptografia.
- [x] T005 Configurar pipeline de auditoria base (`shared/docs/audit/README.md`, `apps/backend-fastapi/src/observability/audit_logger.py`) descrevendo formato de hashes e exportos.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura e camadas compartilhadas indispensáveis antes das histórias.

- [x] T006 Provisionar infraestrutura IaC em `infra/terraform/*` para Vercel, Render, NeonDB (dev/homolog/demo), Upstash Redis e bucket S3 compatível.
- [x] T007 Construir scripts de seed/anonimização em `infra/scripts/seed_neondb.py` e `infra/scripts/load_documents.py` com datasets fictícios versionados.
- [x] T008 Configurar Great Expectations em `shared/datasets/great_expectations/` com checkpoints para bronze/prata/ouro.
- [x] T008a Criar estruturas físicas das camadas bronze/prata/ouro em NeonDB (`infra/scripts/schema_layers.sql`) e aplicar criptografia/chaves dedicadas documentadas em `infra/terraform/neondb.tf`.
- [x] T008b Automatizar validação de mascaramento/linhagem por camada em `shared/datasets/great_expectations/checkpoints/masking.json` e CI correspondente.
- [x] T009 Implementar middleware de compliance em `apps/backend-fastapi/src/domain/privacy_guard.py` (bloqueio PII, justificativas LGPD/HIPAA).
- [x] T010 Montar observabilidade base (`infra/monitoring/grafana_dashboards/agent.json`, `apps/backend-fastapi/src/observability/metrics.py`) com SLO e alertas.
- [x] T011 Configurar feature flags e circuit breakers em `apps/backend-fastapi/src/observability/feature_flags.py` e `apps/frontend-next/src/lib/config/featureFlags.ts`.

---

## Phase 3: User Story 1 - Consulta Clínica Unificada (Priority: P1) 🎯 MVP

**Goal**: Entregar chat em linguagem natural com respostas streamadas, citando SQL e documentos RAG, garantindo rastreabilidade.  
**Independent Test**: Executar cenário “UTI pediátrica” validando streaming em ≤8 s, SQL exibido e links para protocolos citados.

### Tests para US1 (obrigatórios)

- [X] T012 [P] [US1] Escrever teste Playwright `apps/frontend-next/tests/playwright/chat-streaming.spec.ts` validando streaming e citações.
- [X] T013 [P] [US1] Criar testes de contrato `apps/backend-fastapi/tests/api/test_chat_endpoints.py` cobrindo `/v1/chat/sessions` e `/stream`.

### Implementação US1

- [X] T014 [US1] Modelar `QuerySession` + repositório em `apps/backend-fastapi/src/domain/query_session.py` com estados e métricas.
- [X] T015 [US1] Construir pipeline LangChain RAG em `apps/backend-fastapi/src/agents/chat_pipeline.py` combinando SQLAgent + retriever de documentos.
- [X] T016 [US1] Implementar endpoints REST `/v1/chat/sessions` e `/stream` em `apps/backend-fastapi/src/api/routes/chat.py` com validações de política.
- [X] T017 [P] [US1] Desenvolver conector de documentos e citações em `apps/backend-fastapi/src/connectors/rag_document_store.py` usando S3 + metadados.
- [X] T018 [US1] Criar UI de chat com streaming SSE em `apps/frontend-next/src/app/chat/page.tsx` e `src/components/ChatStream.tsx`.
- [X] T019 [P] [US1] Instrumentar métricas/alertas do chat em `apps/backend-fastapi/src/observability/chat_metrics.py` e dashboards correspondentes.
- [X] T020 [US1] Implementar exportação de auditoria por sessão em `apps/backend-fastapi/src/services/audit_exporter.py` e expor download no frontend (`src/services/audit-download.ts`).
- [X] T020a [US1] Catalogar DocumentCorpus com metadados obrigatórios em `apps/backend-fastapi/src/domain/document_catalog.py` (origem, versão, sigilo, proprietário) e sincronizar políticas de acesso em `shared/docs/runbooks/catalog-governance.md`.

---

## Phase 4: User Story 2 - Analista SQL com Assistência Inteligente (Priority: P2)

**Goal**: Fornecer workbench SQL com sugestões LangChain, aprovação humana e resumos textuais mantendo trilha auditável.  
**Independent Test**: Solicitar relatório financeiro, revisar SQL sugerido, aprovar, executar e receber resumo textual + registro de auditoria.

### Tests para US2

- [X] T021 [P] [US2] Escrever testes de serviço `apps/backend-fastapi/tests/agents/test_sql_agent.py` cobrindo sugestão, validação e fallback manual.
- [X] T022 [P] [US2] Criar teste de integração `apps/backend-fastapi/tests/api/test_sql_workbench.py` garantindo aprovação obrigatória antes de execução.

### Implementação US2

- [X] T023 [US2] Implementar introspecção/schema registry em `apps/backend-fastapi/src/connectors/neondb_schema_service.py` com masking rules.
- [X] T024 [US2] Construir endpoint `/v1/sql/assist` em `apps/backend-fastapi/src/api/routes/sql.py` com geração de SQL comentado.
- [X] T025 [US2] Desenvolver UI “SQL Workbench” com editor e difs em `apps/frontend-next/src/app/sql-workbench/page.tsx`.
- [X] T026 [US2] Persistir execuções/aprovações em `apps/backend-fastapi/src/domain/sql_session.py` e registrar AuditEntry correspondente.
- [X] T027 [P] [US2] Criar serviço de resumo/explicação de resultados em `apps/backend-fastapi/src/services/sql_result_summarizer.py` exibido no frontend (`src/components/ResultInsights.tsx`).
- [X] T027a [US2] Medir baseline vs. pós-automação do tempo para relatórios em `infra/scripts/sql_benchmark.py` e registrar métricas em `shared/docs/demo-assets/perf-summary.md` (cumprir SC-002).

---

## Phase 5: User Story 3 - Oficial de Compliance e Operações Confiáveis (Priority: P3)

**Goal**: Disponibilizar painel de conformidade, exportos LGPD/HIPAA e modos de degradação observáveis.  
**Independent Test**: Solicitar histórico de 7 dias, gerar exporto CSV/JSON e simular incidente para verificar alertas e playbook.

### Tests para US3

- [X] T028 [P] [US3] Escrever testes para exportação/auditoria em `apps/backend-fastapi/tests/api/test_audit_exports.py` (CSV/JSON + filtros).
- [X] T029 [P] [US3] Criar teste de modo degradado em `apps/backend-fastapi/tests/observability/test_failover.py` validando feature flags e alertas.

### Implementação US3

- [X] T030 [US3] Implementar job de retenção e anonimização contínua em `apps/backend-fastapi/src/services/data_retention_job.py`.
- [X] T031 [US3] Desenvolver painel de conformidade em `apps/frontend-next/src/app/compliance/page.tsx` exibindo logs, legal basis e filtros.
- [X] T032 [US3] Implementar endpoint `/v1/audit/exports` e `/v1/observability/health` em `apps/backend-fastapi/src/api/routes/compliance.py`.
- [X] T033 [US3] Configurar playbooks/alertas automatizados em `infra/monitoring/alert_rules.yaml` e documentar gatilhos em `docs/runbooks/incident-response.md`.
- [X] T033a [US3] Construir painel “Observability Control Room” em `apps/frontend-next/src/app/observability/page.tsx` com gráficos de uptime, latência p95, taxa de sucesso por integração e status de modo degradado (consumindo `/v1/observability/health`).
- [X] T033b [US3] Criar suíte Playwright `apps/frontend-next/tests/playwright/observability-panel.spec.ts` verificando exibição correta de métricas e alertas.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Garantir prontidão operacional, desempenho e documentação.

- [X] T034 Atualizar `quickstart.md`, `README.md` e `docs/runbooks/*` com instruções finais (deploy, auditoria, drills).
- [X] T035 Conduzir testes de carga/alinhamento (`infra/scripts/load_test.sql`, `apps/backend-fastapi/tests/perf/test_latency.py`) para validar SLOs.
- [X] T036 Executar simulações de falha/recuperação (chaos scripts em `infra/scripts/chaos_mode.py`) e registrar resultados.
- [X] T037 Preparar demonstração final gerando dataset de auditoria e dashboards exportáveis (`shared/docs/demo-assets/`).

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Sem dependências.
- **Foundational (Phase 2)**: Depende da conclusão do Setup; bloqueia todas as histórias.
- **US1 (Phase 3)**: Depende de Foundational; entrega MVP e deve concluir antes das demais histórias.
- **US2 (Phase 4)**: Depende de US1 apenas para reutilizar QuerySession/AuditEntry; funcionalmente independente após isso.
- **US3 (Phase 5)**: Depende de US1 (dados de auditoria) e Foundational (observabilidade); pode rodar em paralelo a US2 após US1.
- **Polish**: Depende das histórias desejadas concluídas.

### User Story Dependencies
- **US1 (P1)**: Nenhuma dependência além de Foundational.
- **US2 (P2)**: Reutiliza QuerySession/AuditEntry de US1 mas pode implementar em paralelo depois da base pronta.
- **US3 (P3)**: Consome auditorias e métricas de US1/US2; requer endpoints prontos para exporto.

### Parallel Opportunities
- T002/T003/T004 podem rodar em paralelo após T001.
- T006–T011 possuem subcomponentes independentes; tarefas marcadas [P] sinalizam execução paralela segura.
- Dentro de cada história:
  - US1: T012 e T013 em paralelo; T017/T019 podem avançar enquanto T014–T016 estão em desenvolvimento.
  - US2: T021 e T022 em paralelo; T023/T024 podem correr com T025/T027 após dependências mínimas.
  - US3: T028 e T029 em paralelo; T030–T033 podem dividir responsabilidades (backend vs infra vs frontend).

---

## Parallel Example: User Story 1

```bash
# Testes em paralelo após fundação:
pnpm playwright test chat-streaming.spec.ts
poetry run pytest apps/backend-fastapi/tests/api/test_chat_endpoints.py

# Implementação simultânea:
python -m uvicorn ... &  # backend local
pnpm dev                 # frontend streaming
```

## Parallel Example: User Story 2

```bash
# Em paralelo:
poetry run pytest apps/backend-fastapi/tests/agents/test_sql_agent.py
pnpm dev --filter apps/frontend-next --filter sql-workbench
```

## Implementation Strategy

1. Finalizar Setup + Foundational garantindo verificação constitucional cumprida.
2. Implementar **US1** integralmente (chat streaming + auditoria) → validar MVP.
3. Adicionar **US2** (SQL assistido) mantendo independência e reutilizando auditoria.
4. Construir **US3** para compliance/observabilidade e executar simulações de incidentes.
5. Concluir fase de Polish com documentação, testes de carga e drills, preparando demonstração pública.


