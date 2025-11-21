# 🏥 Hospital Data Assistant - AI-Powered Healthcare Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1.0-orange.svg)](https://www.langchain.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-black.svg)](https://vercel.com/)
[![Render](https://img.shields.io/badge/Render-Deployed-46e3b7.svg)](https://render.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

> **Intelligent hospital data assistant system** that combines **LangChain SQLAgent** and **RAG (Retrieval Augmented Generation)** to answer clinical and operational questions in natural language, with **LGPD/HIPAA compliance**, **complete auditing**, and **real-time observability**.

**🌐 Live Application:**
- **Frontend**: [https://assistente-dados-hospitalar.vercel.app](https://assistente-dados-hospitalar.vercel.app)
- **Backend API**: [https://assistente-dados-hospitalar.onrender.com](https://assistente-dados-hospitalar.onrender.com)
- **FastAPI Documentation**: [https://assistente-dados-hospitalar.onrender.com/docs](https://assistente-dados-hospitalar.onrender.com/docs)

---

## 🎯 Project Overview

This project demonstrates a **modern AI architecture applied to healthcare**, integrating:

- **🤖 Artificial Intelligence**: LangChain SQLAgent for automatic SQL query generation
- **📚 RAG (Retrieval Augmented Generation)**: Semantic search in hospital documents
- **🌐 Real-Time Streaming**: Server-Sent Events (SSE) for instant responses
- **🔒 Compliance**: LGPD/HIPAA with complete auditing and immutable trails
- **📊 Observability**: SLO metrics, alerts, and monitoring dashboard
- **☁️ Cloud-Native**: Deployed on Vercel (frontend) and Render (backend)

> **💡 Developed with Speckit**: This project was developed with the help of **Speckit**, a powerful AI-assisted development tool that significantly accelerated the development process, from initial architecture to complex feature implementation.

---

## 🚀 Technologies & Skills Demonstrated

### Backend & AI
- **Python 3.11** with **FastAPI** (async REST APIs)
- **LangChain 1.0** (SQLAgent, RAG, Chain Orchestration)
- **OpenAI GPT** (LLM integration)
- **PostgreSQL** (NeonDB) with multi-layer schemas (bronze/silver/gold)
- **psycopg3** (async database driver)
- **Poetry** (dependency management)
- **FastAPI Docs** (automatic Swagger/OpenAPI at `/docs`)

### Frontend & UX
- **Next.js 14** (App Router, Server Components)
- **React 18** (hooks, context, streaming)
- **TypeScript** (type safety)
- **Tailwind CSS** (responsive design system)
- **Server-Sent Events** (real-time data streaming)

### DevOps & Cloud
- **Docker** (containerization)
- **Vercel** (automatic frontend deployment via GitHub)
- **Render** (automatic backend deployment via GitHub)
- **NeonDB** (serverless PostgreSQL)
- **GitHub Actions** (CI/CD)

### Quality & Compliance
- **pytest** (unit and integration tests)
- **Playwright** (E2E tests)
- **Great Expectations** (data validation)
- **LGPD/HIPAA Auditing** (immutable trails, export)
- **Circuit Breaker Pattern** (resilience)

---

## 📋 Key Features

### 1. 💬 Unified Clinical Query
- **Natural language chat** with real-time streaming
- Responses combining **structured data (SQL)** + **documents (RAG)**
- **Visual cards** for aggregated metrics (occupancy, revenue, counts)
- Automatic intent detection and intelligent aggregation
- Responses formatted in single cards with final values

### 2. 🔧 AI-Assisted SQL Workbench
- Automatic SQL generation with **LangChain SQLAgent**
- Contextual suggestions based on database schema
- Mandatory approval before execution
- Automatic textual summaries of results

### 3. 📊 Compliance & Observability
- **Compliance Panel**: LGPD/HIPAA audit trails
- **Observability Dashboard**: SLO metrics (p95 latency, uptime)
- **Degraded Mode**: Automatic read-only on failures
- **Export**: CSV/JSON audit trail export

---

## 🏗️ Architecture

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
┌───▼───┐ ┌──▼───┐ ┌───▼───┐ ┌───▼───┐
│NeonDB │ │  S3  │ │Redis  │ │OpenAI │
│(PG)   │ │Docs  │ │Cache  │ │  API  │
└───────┘ └──────┘ └───────┘ └───────┘
```

### Data Layers
- **Bronze**: Raw data
- **Silver**: Cleaned and validated data
- **Gold**: Aggregated and masked data (compliance)

---

## 📚 API Documentation

Interactive FastAPI documentation is available at:

- **Swagger UI**: [https://assistente-dados-hospitalar.onrender.com/docs](https://assistente-dados-hospitalar.onrender.com/docs)
- **ReDoc**: [https://assistente-dados-hospitalar.onrender.com/redoc](https://assistente-dados-hospitalar.onrender.com/redoc)

### Main Endpoints

#### Chat
- `POST /v1/chat/sessions` - Create new chat session
- `POST /v1/chat/stream` - Chat response stream (SSE)

#### SQL Workbench
- `POST /v1/sql/assist` - Generate SQL suggestion with AI
- `POST /v1/sql/execute` - Execute approved SQL query

#### Compliance
- `GET /v1/audit/exports` - Export audit trails (CSV/JSON)
- `GET /v1/observability/health` - Health check and SLO metrics

---

## 🛠️ Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)
- PostgreSQL (NeonDB or local)

### Installation

```bash
# Clone repository
git clone https://github.com/NathanielPereira/Assistente-Dados-Hospitalar.git
cd Assistente-Dados-Hospitalar

# Backend
cd apps/backend-fastapi
poetry install
cp .env.example .env  # Configure your variables
poetry run uvicorn src.api.main:app --reload

# Frontend
cd apps/frontend-next
npm install
cp .env.example .env.local  # Configure your variables
npm run dev
```

### Environment Variables

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

## 🐳 Docker Deploy

```bash
# Build and run with docker-compose
docker-compose up --build

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## ☁️ Production Deployment

### Frontend (Vercel)

1. Connect your GitHub repository to Vercel
2. Configure environment variables:
   - `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`
3. Automatic deployment on every push!

### Backend (Render)

1. Connect your GitHub repository to Render
2. Configure as **Web Service**
3. Configure environment variables:
   - `DATABASE_URL=postgresql://...`
   - `OPENAI_API_KEY=sk-...`
   - `ENVIRONMENT=production`
4. Automatic deployment on every push!

**Configuration files:**
- `render.yaml` - Render configuration
- `vercel.json` - Vercel configuration

---

## 🧪 Testing

```bash
# Backend (pytest)
cd apps/backend-fastapi
poetry run pytest

# Frontend E2E (Playwright)
cd apps/frontend-next
npm run test:e2e

# Data validation (Great Expectations)
great_expectations checkpoint run
```

---

## 📈 Metrics & Observability

- **p95 Latency**: < 2s for SQL queries
- **Uptime**: > 99.5%
- **Throughput**: Supports multiple simultaneous sessions
- **Auditing**: 100% of queries logged

---

## 🔒 LGPD/HIPAA Compliance

- ✅ **Encryption**: Sensitive data encrypted at rest
- ✅ **Masking**: PII data masked in "gold" layer
- ✅ **Auditing**: Immutable trails with SHA-256 hashes
- ✅ **Legal Basis**: Legal basis documentation for each access
- ✅ **Retention**: Configurable retention policies
- ✅ **Export**: CSV/JSON trail export

---

## 🎓 Skills Demonstrated

This project demonstrates proficiency in:

### Software Engineering
- Microservices architecture
- Async REST APIs
- Data streaming (SSE)
- Design patterns (Singleton, Factory, Circuit Breaker)

### Artificial Intelligence
- LangChain (SQLAgent, RAG, Chains)
- Prompt Engineering
- LLM Integration (OpenAI)
- Natural Language Processing
- Intelligent SQL generation from natural language

### DevOps & Cloud
- Containerization (Docker)
- Automatic deployment (Vercel + Render)
- CI/CD with GitHub Actions
- Environment variable management

### Quality & Security
- Automated testing (unit, integration, E2E)
- Data validation
- Compliance (LGPD/HIPAA)
- Auditing and observability

### Modern Frontend
- Next.js 14 (App Router)
- TypeScript
- Responsive Design
- Real-time Updates (SSE)

---

## 🤝 Contributing

This is a demonstration project. For improvements or suggestions, open an issue or pull request.

---

## 📝 License

This project is a **technical demonstration** with fictional data, created for educational and portfolio purposes.

---

## 👤 Author

**Nathaniel Pereira**
- GitHub: [@NathanielPereira](https://github.com/NathanielPereira)
- Repository: [Assistente-Dados-Hospitalar](https://github.com/NathanielPereira/Assistente-Dados-Hospitalar)

---

## 🌟 Project Highlights

- ✅ **100% Functional**: Complete and operational system in production
- ✅ **Production-Ready**: Deployed on Vercel and Render
- ✅ **Well Documented**: Clean code and complete documentation (including FastAPI Docs)
- ✅ **Tested**: Adequate test coverage
- ✅ **Scalable**: Architecture prepared for growth
- ✅ **Secure**: LGPD/HIPAA compliance implemented
- ✅ **Intelligent**: AI capable of understanding natural language questions and generating accurate SQL

---

## 🛠️ Tools Used

- **Speckit**: AI-assisted development that significantly accelerated the development process
- **Vercel**: Automatic deployment of Next.js frontend
- **Render**: Automatic deployment of FastAPI backend
- **NeonDB**: Serverless PostgreSQL database
- **OpenAI**: LLM API for LangChain
- **GitHub**: Version control and CI/CD

---

**⭐ If this project was helpful, consider giving it a star on GitHub!**
