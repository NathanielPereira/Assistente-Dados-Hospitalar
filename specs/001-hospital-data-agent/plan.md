# Implementation Plan: Assistente de Dados Hospitalar IA

**Branch**: `001-hospital-data-agent` | **Date**: 2025-11-20 | **Spec**: [specs/001-hospital-data-agent/spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-hospital-data-agent/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Construir um assistente de dados hospitalares que combina LangChain SQLAgent e RAG sobre documentos fictícios para responder perguntas clínicas e operacionais com streaming web (Next.js) e backend FastAPI, garantindo compliance LGPD/HIPAA, auditoria completa e observabilidade. Entrega um MVP híbrido Node + Python hospedado em Vercel (frontend), Render (APIs) e NeonDB, demonstrando SQL avançado, trilhas imutáveis, painel dedicado de observabilidade (uptime/latência/status de integrações) e governança das camadas de dados (bronze/prata/ouro) com catalogação completa de DocumentCorpus.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 (backend FastAPI + LangChain), Node.js 20 / Next.js 14 (frontend)  
**Primary Dependencies**: LangChain SQLAgent, OpenAI-compatible LLM provider, FastAPI, Next.js App Router, NeonDB/PostgreSQL client, Redis-compatible cache (Upstash) para sessão, Great Expectations para validação de dados, Grafana/Prometheus para painel de observabilidade  
**Storage**: NeonDB (camadas bronze/prata/ouro com chaves AES dedicadas), blob S3 compatível (AWS free tier) para documentos fictícios (inclui catálogo de metadados), Redis para cache curto de sessões e rate limiting  
**Testing**: pytest + pytest-asyncio, Playwright para frontend, contract tests via schemathesis/OpenAPI, great_expectations checkpoints  
**Target Platform**: Frontend em Vercel Edge/Node 20; Backend FastAPI em Render Standard (Docker); NeonDB (cloud), S3/MinIO para documentos; scripts locais em Windows dev  
**Project Type**: Arquitetura híbrida web (frontend Next.js) + backend Python + infra compartilhada  
**Performance Goals**: Streaming inicial ≤2s, respostas completas ≤8s; consultas SQL até 10k linhas concluídas ≤5s; auditoria exportável ≤30s; disponibilidade ≥99% demonstrativa  
**Constraints**: Sem dados reais; todo tráfego criptografado (TLS 1.3); logs imutáveis; modo degradado read-only obrigatório; limites de free tier (Render/Vercel) exigem orquestração leve e cold-start < 3s; painel de observabilidade deve permanecer acessível mesmo em degradação  
**Scale/Scope**: MVP para 10 usuários concorrentes (consultor, analista, compliance); até 50 documentos fictícios (~200 páginas) e 5 schemas principais no NeonDB; 3 ambientes (dev/homolog/demo)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Proteção Integral de Dados Clínicos**: Dados fictícios permanecem criptografados (AES-256 em repouso, TLS 1.3 em trânsito), camadas bronze/prata/ouro segregadas, mascaramento validado por Great Expectations e base legal documentada por fluxo. ✅
- **Auditoria Automatizada e Rastreamento**: Cada QuerySession gera AuditEntry com hashes, SQL, documentos citados, exportação CSV/JSON e armazenamento imutável (S3 com versionamento + NeonDB append-only). ✅
- **Evidências e Testes Dirigindo Entregas**: Dataset sintético versionado + cenários Great Expectations definidos, testes de regressão de precisão e suites Playwright/pytest planejados antes da implementação. ✅
- **Interoperabilidade Modular**: Contratos REST e eventos descritos, conectores RAG e SQL isolados com versionamento sem acoplamento; plano de breaking change com períodos de convivência na demo. ✅
- **Observabilidade e Resiliência**: SLOs, dashboards (Grafana/Edge Config) mais painel Next.js “Observability Control Room”, alertas Render/Vercel + feature flags e circuit breakers detalhados; modo degradado read-only + playbooks. ✅

## Project Structure

### Documentation (this feature)

```text
specs/001-hospital-data-agent/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
apps/
├── frontend-next/
│   ├── src/app/                         # Páginas/streaming UI
│   ├── src/components/
│   ├── src/lib/langchain-client/
│   ├── src/services/audit-export/
│   └── tests/playwright/
├── backend-fastapi/
│   ├── src/api/                         # Endpoints REST
│   ├── src/agents/                      # LangChain pipelines (SQLAgent/RAG)
│   ├── src/connectors/                  # NeonDB, documentos S3
│   ├── src/domain/                      # QuerySession, AuditEntry, policies
│   ├── src/observability/               # métricas, feature flags, circuit breakers
│   └── tests/
└── infra/
    ├── terraform/                       # Vercel, Render, Neon, S3, Upstash
    ├── scripts/                         # seed de dados fictícios
    └── monitoring/                      # Dashboards, alert rules

shared/
├── contracts/
├── datasets/                            # CSV/Parquet sintéticos
└── docs/runbooks/
```

**Structure Decision**: Arquitetura multi-app separando frontend Next.js (streaming e UX), backend FastAPI (agentes, conectores, compliance) e pasta `infra/` para IaC e observabilidade. `shared/` reúne contratos RAG/SQL e datasets versionados; garante isolamento para deploys independentes (Vercel vs Render) e facilita auditoria.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
