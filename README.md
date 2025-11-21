# 🏥 Hospital Data Assistant - AI-Powered Healthcare Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1.0-orange.svg)](https://www.langchain.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![AWS](https://img.shields.io/badge/AWS-ECS-orange.svg)](https://aws.amazon.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

> **Sistema inteligente de assistência a dados hospitalares** que combina **LangChain SQLAgent** e **RAG (Retrieval Augmented Generation)** para responder perguntas clínicas e operacionais em linguagem natural, com **compliance LGPD/HIPAA**, **auditoria completa** e **observabilidade em tempo real**.

---

## 🎯 Visão Geral do Projeto

Este projeto demonstra uma **arquitetura moderna de IA aplicada à saúde**, integrando:

- **🤖 Inteligência Artificial**: LangChain SQLAgent para geração automática de queries SQL
- **📚 RAG (Retrieval Augmented Generation)**: Busca semântica em documentos hospitalares
- **🌐 Streaming em Tempo Real**: Server-Sent Events (SSE) para respostas instantâneas
- **🔒 Compliance**: LGPD/HIPAA com auditoria completa e trilhas imutáveis
- **📊 Observabilidade**: Métricas SLO, alertas e painel de monitoramento
- **☁️ Cloud-Native**: Deploy na AWS com ECS Fargate, ECR e Terraform

---

## 🚀 Tecnologias e Habilidades Demonstradas

### Backend & IA
- **Python 3.11** com **FastAPI** (APIs REST assíncronas)
- **LangChain 1.0** (SQLAgent, RAG, Chain Orchestration)
- **OpenAI GPT** (integração com LLMs)
- **PostgreSQL** (NeonDB) com schemas multi-camada (bronze/prata/ouro)
- **psycopg3** (async database driver)
- **Poetry** (gerenciamento de dependências)

### Frontend & UX
- **Next.js 14** (App Router, Server Components)
- **React 18** (hooks, context, streaming)
- **TypeScript** (type safety)
- **Tailwind CSS** (design system responsivo)
- **Server-Sent Events** (streaming de dados em tempo real)

### DevOps & Cloud
- **Docker** (containerização)
- **AWS ECS Fargate** (orquestração de containers)
- **AWS ECR** (registry de imagens)
- **Terraform** (Infrastructure as Code)
- **CloudWatch** (logs e métricas)
- **VPC, Security Groups, ALB** (networking e segurança)

### Qualidade & Compliance
- **pytest** (testes unitários e de integração)
- **Playwright** (testes E2E)
- **Great Expectations** (validação de dados)
- **Auditoria LGPD/HIPAA** (trilhas imutáveis, exportação)
- **Circuit Breaker Pattern** (resiliência)

---

## 📋 Funcionalidades Principais

### 1. 💬 Consulta Clínica Unificada
- Chat em **linguagem natural** com streaming em tempo real
- Respostas combinando **dados estruturados (SQL)** + **documentos (RAG)**
- **Cards visuais** para métricas agregadas (ocupação, receita, contagens)
- Detecção automática de intenção e agregação inteligente

### 2. 🔧 SQL Workbench Assistido por IA
- Geração automática de SQL com **LangChain SQLAgent**
- Sugestões contextuais baseadas no schema do banco
- Aprovação obrigatória antes de execução
- Resumos textuais automáticos dos resultados

### 3. 📊 Compliance & Observabilidade
- **Painel de Compliance**: Trilhas de auditoria LGPD/HIPAA
- **Observability Dashboard**: Métricas SLO (p95 latency, uptime)
- **Modo Degradado**: Read-only automático em caso de falhas
- **Exportação**: CSV/JSON de trilhas de auditoria

---

## 🏗️ Arquitetura

```
┌─────────────────┐
│   Next.js 14    │  Frontend (Vercel/AWS)
│   (React/TS)    │
└────────┬────────┘
         │ SSE Streaming
         │ REST API
┌────────▼────────┐
│   FastAPI       │  Backend (AWS ECS Fargate)
│   + LangChain   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
┌───▼───┐ ┌──▼───┐ ┌───▼───┐ ┌───▼───┐
│NeonDB │ │  S3  │ │Redis  │ │OpenAI │
│(PG)   │ │Docs  │ │Cache  │ │  API  │
└───────┘ └──────┘ └───────┘ └───────┘
```

### Camadas de Dados
- **Bronze**: Dados brutos (raw)
- **Prata**: Dados limpos e validados
- **Ouro**: Dados agregados e mascarados (compliance)

---

## 🛠️ Setup Local

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- Docker (opcional)
- PostgreSQL (NeonDB ou local)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/hospital-data-assistant.git
cd hospital-data-assistant

# Backend
cd apps/backend-fastapi
poetry install
cp .env.example .env  # Configure suas variáveis
poetry run uvicorn src.api.main:app --reload

# Frontend
cd apps/frontend-next
npm install
cp .env.example .env.local  # Configure suas variáveis
npm run dev
```

### Variáveis de Ambiente

**Backend** (`.env`):
```env
DATABASE_URL=postgresql://user:pass@host/db
OPENAI_API_KEY=sk-...
ENVIRONMENT=development
```

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🐳 Deploy com Docker

```bash
# Build e run com docker-compose
docker-compose up --build

# Acesse:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

## ☁️ Deploy na AWS

### Pré-requisitos
- AWS CLI configurado
- Terraform instalado
- Docker instalado
- Credenciais AWS com permissões adequadas

### Passos

1. **Configure variáveis do Terraform**:
```bash
cd infra/terraform
terraform init
```

2. **Configure variáveis**:
```bash
export TF_VAR_database_url="postgresql://..."
export TF_VAR_openai_api_key="sk-..."
export AWS_REGION="us-east-1"
```

3. **Execute o script de deploy**:
```bash
chmod +x infra/aws/deploy.sh
./infra/aws/deploy.sh
```

O script irá:
- Criar repositórios ECR
- Build e push das imagens Docker
- Deploy da infraestrutura com Terraform
- Criar ECS services, ALB, VPC, Security Groups

---

## 🧪 Testes

```bash
# Backend (pytest)
cd apps/backend-fastapi
poetry run pytest

# Frontend E2E (Playwright)
cd apps/frontend-next
npm run test:e2e

# Validação de dados (Great Expectations)
great_expectations checkpoint run
```

---

## 📈 Métricas e Observabilidade

- **Latência p95**: < 2s para queries SQL
- **Uptime**: > 99.5%
- **Throughput**: Suporta múltiplas sessões simultâneas
- **Auditoria**: 100% das queries registradas

---

## 🔒 Compliance LGPD/HIPAA

- ✅ **Criptografia**: Dados sensíveis criptografados em repouso
- ✅ **Mascaramento**: Dados PII mascarados na camada "ouro"
- ✅ **Auditoria**: Trilhas imutáveis com hashes SHA-256
- ✅ **Base Legal**: Documentação de base legal para cada acesso
- ✅ **Retenção**: Políticas de retenção configuráveis
- ✅ **Exportação**: Exportação de trilhas em CSV/JSON

---

## 📚 Documentação Adicional

- [Especificação Completa](specs/001-hospital-data-agent/spec.md)
- [Plano de Implementação](specs/001-hospital-data-agent/plan.md)
- [Guia de Setup](SETUP.md)
- [Guia de Testes](TESTING.md)
- [Runbooks Operacionais](docs/runbooks/)

---

## 🎓 Habilidades Demonstradas

Este projeto demonstra proficiência em:

### Engenharia de Software
- Arquitetura de microserviços
- APIs REST assíncronas
- Streaming de dados (SSE)
- Padrões de design (Singleton, Factory, Circuit Breaker)

### Inteligência Artificial
- LangChain (SQLAgent, RAG, Chains)
- Prompt Engineering
- LLM Integration (OpenAI)
- Natural Language Processing

### DevOps & Cloud
- Containerização (Docker)
- Infrastructure as Code (Terraform)
- AWS Services (ECS, ECR, VPC, ALB, CloudWatch)
- CI/CD pipelines

### Qualidade & Segurança
- Testes automatizados (unit, integration, E2E)
- Validação de dados
- Compliance (LGPD/HIPAA)
- Auditoria e observabilidade

### Frontend Moderno
- Next.js 14 (App Router)
- TypeScript
- Responsive Design
- Real-time Updates

---

## 🤝 Contribuindo

Este é um projeto demonstrativo. Para melhorias ou sugestões, abra uma issue ou pull request.

---

## 📝 Licença

Este projeto é um **demonstrativo técnico** com dados fictícios, criado para fins educacionais e de portfólio.

---

## 👤 Autor

**Seu Nome**
- LinkedIn: [seu-perfil](https://linkedin.com/in/seu-perfil)
- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- Email: seu.email@example.com

---

## 🌟 Destaques do Projeto

- ✅ **100% Funcional**: Sistema completo e operacional
- ✅ **Production-Ready**: Pronto para deploy em produção
- ✅ **Bem Documentado**: Código limpo e documentação completa
- ✅ **Testado**: Cobertura de testes adequada
- ✅ **Escalável**: Arquitetura preparada para crescimento
- ✅ **Seguro**: Compliance LGPD/HIPAA implementado

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**
