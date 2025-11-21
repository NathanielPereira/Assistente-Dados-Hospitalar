# Quickstart — Assistente de Dados Hospitalar IA

## 1. Pré-requisitos
- Node.js 20+, PNPM 9
- Python 3.11 + Poetry
- Docker Desktop (para testes locais)
- Acesso a Vercel CLI, Render CLI e NeonDB (API key)
- Credenciais fictícias armazenadas no `.env` via 1Password/Secret Manager

## 2. Clonar e instalar
```bash
git clone <repo>
cd Assistente-de-Dados
pnpm install --filter apps/frontend-next...
poetry install --with dev
```

## 3. Provisionar infraestrutura (demo)
```bash
cd infra/terraform
terraform init
terraform apply -var-file=demo.tfvars
```
- Cria NeonDB (dev/homolog/demo), bucket S3 compatível, Upstash Redis e secrets Render/Vercel.

## 4. Popular dados fictícios
```bash
python infra/scripts/seed_neondb.py --env demo
python infra/scripts/load_documents.py --source datasets/docs --bucket s3://hospital-demo
```

## 5. Rodar localmente
```bash
# Backend
cd apps/backend-fastapi
poetry run uvicorn src.api.main:app --reload

# Frontend
cd apps/frontend-next
pnpm dev
```
- Configure `.env.local` com URLs do backend, chave LLM (modo sandbox) e feature flags.

## 6. Testes
```bash
poetry run pytest
pnpm test:e2e
great_expectations checkpoint run data_quality.chat_responses
```

## 7. Deploy demo
```bash
vercel deploy apps/frontend-next --prod
render services update apps/backend-fastapi --image latest
```
- Atualize secrets com `render env:set` e `vercel env pull`.

## 8. Observabilidade
- Grafana/Prometheus disponibilizados via `infra/monitoring`.
- Execute `scripts/generate_audit_report.py --last 24h` para validar exportações.
- Acesse painel de observabilidade em `/observability` para métricas em tempo real.

## 9. Auditoria e Compliance
- Exporte trilhas de auditoria via `/compliance` (CSV/JSON).
- Execute job de retenção: `python apps/backend-fastapi/src/services/data_retention_job.py`.
- Valide conformidade LGPD/HIPAA conforme `shared/docs/runbooks/policies.md`.

## 10. Drills de Incidente
- Execute simulações de falha: `python infra/scripts/chaos_mode.py --scenario db_failure`.
- Valide playbooks de recuperação conforme `docs/runbooks/incident-response.md`.
- Verifique alertas e modo degradado via painel de observabilidade.


