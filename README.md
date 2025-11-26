# 🏥 Assistente de Dados Hospitalar - Plataforma de Analytics com IA

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1.0-orange.svg)](https://www.langchain.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-black.svg)](https://vercel.com/)
[![Render](https://img.shields.io/badge/Render-Deployed-46e3b7.svg)](https://render.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

> **Sistema inteligente de assistência a dados hospitalares** que combina **LangChain SQLAgent** para responder perguntas clínicas e operacionais em linguagem natural, com **auditoria completa** e **observabilidade em tempo real**.

**🌐 Aplicação em Produção:**
- **Frontend**: [https://assistente-dados-hospitalar.vercel.app](https://assistente-dados-hospitalar.vercel.app) (Vercel)
- **Backend API**: [https://assistente-dados-hospitalar.onrender.com](https://assistente-dados-hospitalar.onrender.com) (Render)
- **Documentação FastAPI**: [https://assistente-dados-hospitalar.onrender.com/docs](https://assistente-dados-hospitalar.onrender.com/docs)

---

## 🎯 Visão Geral do Projeto

Este projeto demonstra uma **arquitetura moderna de IA aplicada à saúde**, integrando:

- **🤖 Inteligência Artificial**: LangChain SQLAgent para geração automática de queries SQL
- **🌐 Streaming em Tempo Real**: Server-Sent Events (SSE) para respostas instantâneas
- **📊 Observabilidade**: Métricas SLO, status de integrações e painel de monitoramento
- **☁️ Cloud-Native**: Deploy na Vercel (frontend) e Render (backend)
- **🔄 Em Desenvolvimento**: RAG completo, cache Redis, autenticação de usuários

> **💡 Desenvolvido com Speckit**: Este projeto foi desenvolvido com a ajuda do **Speckit**, uma ferramenta poderosa de desenvolvimento assistido por IA que acelerou significativamente o processo de desenvolvimento, desde a arquitetura inicial até a implementação de funcionalidades complexas.

---

## 🚀 Tecnologias e Habilidades Demonstradas

### Backend & IA
- **Python 3.11** com **FastAPI** (APIs REST assíncronas)
- **LangChain 1.0** (SQLAgent, RAG, Chain Orchestration)
- **OpenAI GPT** (integração com LLMs)
- **PostgreSQL** (NeonDB) com schemas multi-camada (bronze/prata/ouro)
- **psycopg3** (async database driver)
- **Poetry** (gerenciamento de dependências)
- **FastAPI Docs** (Swagger/OpenAPI automático em `/docs`)

### Frontend & UX
- **Next.js 14** (App Router, Server Components)
- **React 18** (hooks, context, streaming)
- **TypeScript** (type safety)
- **Tailwind CSS** (design system responsivo)
- **Server-Sent Events** (streaming de dados em tempo real)

### DevOps & Cloud
- **Vercel** (deploy automático do frontend via GitHub) ✅
- **Render** (deploy automático do backend via GitHub) ✅
- **NeonDB** (PostgreSQL serverless) ✅
- **Docker** (containerização - configurado, não usado em produção)
- **GitHub Actions** (CI/CD - planejado)

### Qualidade & Compliance
- **pytest** (testes unitários e de integração) ✅
- **Auditoria** (trilhas de auditoria, exportação CSV/JSON) ✅
- **Circuit Breaker Pattern** (resiliência para LLMs) ✅
- **Playwright** (testes E2E - planejado)
- **Great Expectations** (validação de dados - planejado)

---

## 📋 Funcionalidades Principais

### ✅ Implementado

#### 1. 💬 Consulta Clínica Unificada
- Chat em **linguagem natural** com streaming em tempo real (SSE)
- Geração automática de SQL com **LangChain SQLAgent**
- **Cards visuais** para métricas agregadas (ocupação, receita, contagens)
- Detecção automática de intenção e agregação inteligente
- Respostas formatadas em cards únicos com valores finais
- **✨ Smart Response Detection**: Detecta automaticamente perguntas não respondíveis, explica por que, e sugere alternativas relevantes
- Cache de perguntas frequentes (in-memory)

#### 2. 🔧 SQL Workbench Assistido por IA
- Geração automática de SQL com **LangChain SQLAgent**
- Sugestões contextuais baseadas no schema do banco
- Aprovação obrigatória antes de execução
- Validação de SQL antes de executar
- Resumos textuais automáticos dos resultados

#### 3. 📊 Compliance & Observabilidade
- **Painel de Compliance**: Visualização de trilhas de auditoria
- **Exportação**: CSV/JSON de trilhas de auditoria
- **Observability Dashboard**: Métricas SLO (p95 latency, uptime)
- **Status de Integrações**: Banco de dados e LLM providers
- **Modo Degradado**: Read-only automático em caso de falhas

#### 4. 🧠 Smart Response Detection (Feature 003)
- **Detecção Automática de Schema**: Cacheia metadados do PostgreSQL (1 hora TTL)
- **Análise de Perguntas**: Extrai entidades, mapeia sinônimos, calcula confiança (70% threshold)
- **Respostas Inteligentes**: Explica por que não pode responder + 3 sugestões relevantes
- **Adaptação Automática**: Schema atualiza automaticamente sem código
- **Zero Breaking Changes**: 100% backward compatible com clientes existentes
- **Performance**: < 1s para análise completa, < 100ms para cache hits

### 🔄 Em Desenvolvimento

- **RAG Completo**: Integração com documentos S3 para busca semântica
- **Cache Redis**: Cache distribuído para otimização de performance
- **Autenticação**: Sistema de autenticação e autorização de usuários
- **Mascaramento de PII**: Proteção de dados sensíveis
- **Criptografia**: Criptografia ponta a ponta para dados sensíveis
- **Alertas Automáticos**: Sistema de notificações para eventos críticos
- **Bases Legais Detalhadas**: Documentação completa de bases legais LGPD/HIPAA

---

## 🏗️ Arquitetura

```
┌─────────────────┐
│   Next.js 14    │  Frontend (Vercel)
│   (React/TS)    │  https://assistente-dados-hospitalar.vercel.app
└────────┬────────┘
         │ SSE Streaming
         │ REST API
┌────────▼────────┐
│   FastAPI       │  Backend (Render)
│   + LangChain   │  https://assistente-dados-hospitalar.onrender.com
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│NeonDB │ │Cache  │ │LLMs   │
│(PG)   │ │(local)│ │(Multi)│
└───────┘ └───────┘ └───────┘
```

**Status das Integrações:**
- ✅ **NeonDB (PostgreSQL)**: Conectado e operacional
- ✅ **LLM Providers**: OpenAI, Google Gemini, Anthropic Claude (com fallback automático)
- ✅ **Cache**: In-memory (local)
- 🔄 **S3 (RAG)**: Planejado
- 🔄 **Redis**: Planejado

---

## 📚 Documentação da API

A documentação interativa do FastAPI está disponível em:

- **Swagger UI**: [https://assistente-dados-hospitalar.onrender.com/docs](https://assistente-dados-hospitalar.onrender.com/docs)
- **ReDoc**: [https://assistente-dados-hospitalar.onrender.com/redoc](https://assistente-dados-hospitalar.onrender.com/redoc)

### Principais Endpoints

#### Chat
- `POST /v1/chat/sessions` - Criar nova sessão de chat
- `POST /v1/chat/stream` - Stream de respostas do chat (SSE)

#### SQL Workbench
- `POST /v1/sql/assist` - Gerar sugestão de SQL com IA
- `POST /v1/sql/execute` - Executar query SQL aprovada

#### Compliance
- `GET /v1/audit/exports` - Exportar trilhas de auditoria (CSV/JSON)
- `GET /v1/observability/health` - Health check e métricas SLO

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
git clone https://github.com/NathanielPereira/Assistente-Dados-Hospitalar.git
cd Assistente-Dados-Hospitalar

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
# Docs: http://localhost:8000/docs
```

---

## ☁️ Deploy em Produção

### Frontend (Vercel)

1. Conecte seu repositório GitHub ao Vercel
2. Configure variáveis de ambiente:
   - `NEXT_PUBLIC_API_URL=https://seu-backend.onrender.com`
3. Deploy automático a cada push!

### Backend (Render)

1. Conecte seu repositório GitHub ao Render
2. Configure como **Web Service**
3. Configure variáveis de ambiente:
   - `DATABASE_URL=postgresql://...`
   - `OPENAI_API_KEY=sk-...`
   - `ENVIRONMENT=production`
4. Deploy automático a cada push!

**Arquivos de configuração:**
- `render.yaml` - Configuração do Render
- `vercel.json` - Configuração do Vercel

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

## 🔒 Compliance e Segurança

### ✅ Implementado
- **Auditoria**: Trilhas de auditoria completas para todas as interações
- **Exportação**: Exportação de trilhas em CSV/JSON
- **Rastreamento**: Rastreamento completo de queries SQL e prompts
- **Modo Degradado**: Proteção automática em caso de falhas

### 🔄 Planejado
- **Criptografia**: Dados sensíveis criptografados em repouso
- **Mascaramento**: Dados PII mascarados automaticamente
- **Base Legal**: Documentação detalhada de base legal para cada acesso
- **Retenção**: Políticas de retenção configuráveis
- **Autenticação**: Sistema de autenticação e autorização

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
- Geração inteligente de SQL a partir de linguagem natural

### DevOps & Cloud
- Containerização (Docker)
- Deploy automático (Vercel + Render)
- CI/CD com GitHub Actions
- Gerenciamento de variáveis de ambiente

### Qualidade & Segurança
- Testes automatizados (unit, integration, E2E)
- Validação de dados
- Compliance (LGPD/HIPAA)
- Auditoria e observabilidade

### Frontend Moderno
- Next.js 14 (App Router)
- TypeScript
- Responsive Design
- Real-time Updates (SSE)

---

## 🤝 Contribuindo

Este é um projeto demonstrativo. Para melhorias ou sugestões, abra uma issue ou pull request.

---

## 📝 Licença

Este projeto é um **demonstrativo técnico** com dados fictícios, criado para fins educacionais e de portfólio.

---

## 👤 Autor

**Nathaniel Pereira**
- GitHub: [@NathanielPereira](https://github.com/NathanielPereira)
- Repositório: [Assistente-Dados-Hospitalar](https://github.com/NathanielPereira/Assistente-Dados-Hospitalar)

---

## 🌟 Status do Projeto

### ✅ Funcionalidades Principais
- **Sistema Operacional**: Deployado e funcionando em produção (Vercel + Render)
- **Chat Inteligente**: Geração automática de SQL a partir de linguagem natural
- **Smart Detection**: Detecta perguntas não respondíveis e sugere alternativas
- **Observabilidade**: Monitoramento em tempo real do sistema
- **Compliance**: Trilhas de auditoria e exportação de dados

### 🔄 Próximos Passos
- Integração completa com RAG (documentos S3)
- Cache distribuído com Redis
- Sistema de autenticação e autorização
- Melhorias de segurança (criptografia, mascaramento de PII)
- Alertas automáticos e notificações

---

## 🛠️ Ferramentas Utilizadas

- **Speckit**: Desenvolvimento assistido por IA que acelerou significativamente o processo de desenvolvimento
- **Vercel**: Deploy automático do frontend Next.js
- **Render**: Deploy automático do backend FastAPI
- **NeonDB**: Banco de dados PostgreSQL serverless
- **OpenAI**: API de LLM para LangChain
- **GitHub**: Controle de versão e CI/CD

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**
