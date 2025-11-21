# Guia de Testes - Assistente de Dados Hospitalar

## Pré-requisitos

`ash
# Instalar dependências
pnpm install
poetry install --with dev

# Configurar variáveis de ambiente
cp .env.example .env.local  # Frontend
cp .env.example .env        # Backend
`

## 1. Testes Unitários (Backend)

`ash
cd apps/backend-fastapi
poetry run pytest tests/ -v
`

**Cobertura esperada:**
- Domain models (QuerySession, SQLSession, DocumentCatalog)
- Services (AuditExporter, SQLResultSummarizer, DataRetentionJob)
- Observability (metrics, feature flags, circuit breakers)

## 2. Testes de Contrato (API)

`ash
cd apps/backend-fastapi
poetry run pytest tests/api/ -v
`

**Endpoints testados:**
- /v1/chat/sessions - Criação de sessão
- /v1/chat/stream - Streaming de respostas
- /v1/sql/assist - Sugestão de SQL
- /v1/sql/execute - Execução de SQL (com aprovação)
- /v1/audit/exports - Exportação de auditoria
- /v1/observability/health - Health check

## 3. Testes E2E (Frontend)

`ash
cd apps/frontend-next
pnpm install
pnpm test:e2e  # ou npx playwright test
`

**Cenários testados:**
- Chat streaming com citações (US1)
- SQL Workbench com aprovação (US2)
- Painel de observabilidade (US3)

## 4. Testes de Performance

`ash
cd apps/backend-fastapi
poetry run pytest tests/perf/ -v
`

**Métricas validadas:**
- Streaming inicia em ≤2s (SC-001)
- SQL executa em ≤5s (até 10k linhas)
- Exporto de auditoria em ≤30s (SC-003)
- Latência p95 < 2s (SC-004)

## 5. Testes de Carga (SQL)

`ash
# Conectar ao NeonDB e executar
psql  -f infra/scripts/load_test.sql
`

Valida que consultas complexas completam dentro dos SLOs.

## 6. Validação de Dados (Great Expectations)

`ash
cd shared/datasets
great_expectations checkpoint run masking_per_layer
`

Valida mascaramento e qualidade de dados nas camadas bronze/prata/ouro.

## 7. Simulações de Falha (Chaos Engineering)

`ash
cd infra/scripts
python chaos_mode.py --scenario db_failure --duration 60
python chaos_mode.py --scenario s3_failure
python chaos_mode.py --scenario high_latency
python chaos_mode.py --scenario all
`

**Valida:**
- Modo degradado ativa corretamente
- Alertas são gerados
- Sistema se recupera automaticamente

## 8. Testes de Compliance

### 8.1 Exportação de Auditoria

`ash
# Via API
curl "http://localhost:8000/v1/audit/exports?format=json&days=7" > audit.json
curl "http://localhost:8000/v1/audit/exports?format=csv&days=7" > audit.csv

# Validar estrutura
python -m json.tool audit.json
`

### 8.2 Validação de Hashes

`ash
python scripts/validate_audit_hashes.py --session-id <id>
`

### 8.3 Retenção de Dados

`ash
python apps/backend-fastapi/src/services/data_retention_job.py
`

## 9. Testes de Integração Completa

### 9.1 Fluxo US1 (Chat Clínico)

`ash
# 1. Criar sessão
curl -X POST http://localhost:8000/v1/chat/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user"}'

# 2. Enviar pergunta (streaming)
curl -X POST http://localhost:8000/v1/chat/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"session_id": "<session-id>", "prompt": "Qual taxa de ocupação da UTI?"}'

# 3. Exportar auditoria
curl "http://localhost:8000/v1/audit/exports?session_id=<session-id>&format=json"
`

### 9.2 Fluxo US2 (SQL Assistido)

`ash
# 1. Solicitar sugestão
curl -X POST http://localhost:8000/v1/sql/assist \
  -H "Content-Type: application/json" \
  -d '{"prompt": "receita por especialidade", "tables": ["especialidades", "atendimentos"]}'

# 2. Aprovar e executar
curl -X POST http://localhost:8000/v1/sql/execute \
  -H "Content-Type: application/json" \
  -d '{"sql": "<sql-sugerido>", "approved": true}'
`

### 9.3 Fluxo US3 (Compliance)

`ash
# 1. Verificar health
curl http://localhost:8000/v1/observability/health

# 2. Exportar auditoria com filtros
curl "http://localhost:8000/v1/audit/exports?user_id=test-user&format=json&days=30"
`

## 10. Testes de UI (Manual)

### 10.1 Chat Clínico
1. Acesse http://localhost:3000/chat
2. Envie pergunta: "Qual taxa de ocupação da UTI pediátrica?"
3. Verifique:
   - Streaming funciona
   - SQL é exibido
   - Citações de documentos aparecem

### 10.2 SQL Workbench
1. Acesse http://localhost:3000/sql-workbench
2. Digite: "calcular receita média por especialidade"
3. Clique em "Sugerir SQL"
4. Edite o SQL sugerido
5. Clique em "Executar SQL Aprovado"
6. Verifique resumo dos resultados

### 10.3 Painel de Compliance
1. Acesse http://localhost:3000/compliance
2. Filtre por usuário e período
3. Exporte CSV/JSON
4. Verifique estrutura dos dados

### 10.4 Observability Control Room
1. Acesse http://localhost:3000/observability
2. Verifique métricas em tempo real:
   - Uptime %
   - Latência p95
   - Status das integrações
3. Simule falha e verifique modo degradado

## 11. Suite Completa de Testes

`ash
# Executar todos os testes em sequência
./scripts/run-all-tests.sh
`

Ou manualmente:

`ash
# Backend
cd apps/backend-fastapi
poetry run pytest

# Frontend
cd apps/frontend-next
pnpm test:e2e

# Performance
poetry run pytest tests/perf/

# Chaos
python infra/scripts/chaos_mode.py --scenario all

# Validação de dados
great_expectations checkpoint run
`

## 12. Validação de Conformidade Constitucional

Verifique que todos os princípios estão atendidos:

- ✅ **Proteção de Dados**: Criptografia, mascaramento, base legal
- ✅ **Auditoria**: Trilhas imutáveis, exportos, hashes
- ✅ **Evidências/Testes**: Datasets, métricas, testes antes de código
- ✅ **Interoperabilidade**: Contratos versionados, adaptadores
- ✅ **Observabilidade**: SLOs, alertas, playbooks

## Troubleshooting

### Erros comuns:

1. **Backend não inicia**: Verifique .env e dependências Python
2. **Frontend não conecta**: Verifique NEXT_PUBLIC_API_URL em .env.local
3. **Testes falham**: Execute poetry install --with dev novamente
4. **Playwright não encontra browser**: Execute pnpm exec playwright install

## Próximos Passos

Após todos os testes passarem:
1. Revisar cobertura de testes (meta: >80%)
2. Executar drills de auditoria
3. Validar SLOs em ambiente de homologação
4. Preparar deploy para produção
