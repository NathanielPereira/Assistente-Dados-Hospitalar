# 🏥 Hospital Data Assistant - AI-Powered Healthcare Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1.0-orange.svg)](https://www.langchain.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![AWS](https://img.shields.io/badge/AWS-ECS-orange.svg)](https://aws.amazon.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

> **Intelligent hospital data assistant system** that combines **LangChain SQLAgent** and **RAG (Retrieval Augmented Generation)** to answer clinical and operational questions in natural language, with **LGPD/HIPAA compliance**, **complete auditing**, and **real-time observability**.

---

## 🎯 Project Overview

This project demonstrates a **modern AI architecture applied to healthcare**, integrating:

- **🤖 Artificial Intelligence**: LangChain SQLAgent for automatic SQL query generation
- **📚 RAG (Retrieval Augmented Generation)**: Semantic search in hospital documents
- **🌐 Real-Time Streaming**: Server-Sent Events (SSE) for instant responses
- **🔒 Compliance**: LGPD/HIPAA with complete auditing and immutable trails
- **📊 Observability**: SLO metrics, alerts, and monitoring dashboard
- **☁️ Cloud-Native**: AWS deployment with ECS Fargate, ECR, and Terraform

---

## 🚀 Technologies & Skills Demonstrated

### Backend & AI
- **Python 3.11** with **FastAPI** (async REST APIs)
- **LangChain 1.0** (SQLAgent, RAG, Chain Orchestration)
- **OpenAI GPT** (LLM integration)
- **PostgreSQL** (NeonDB) with multi-layer schemas (bronze/silver/gold)
- **psycopg3** (async database driver)
- **Poetry** (dependency management)

### Frontend & UX
- **Next.js 14** (App Router, Server Components)
- **React 18** (hooks, context, streaming)
- **TypeScript** (type safety)
- **Tailwind CSS** (responsive design system)
- **Server-Sent Events** (real-time data streaming)

### DevOps & Cloud
- **Docker** (containerization)
- **AWS ECS Fargate** (container orchestration)
- **AWS ECR** (image registry)
- **Terraform** (Infrastructure as Code)
- **CloudWatch** (logs and metrics)
- **VPC, Security Groups, ALB** (networking and security)

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
│   Next.js 14    │  Frontend (Vercel/AWS)
│   (React/TS)    │
└────────┬────────┘
         │ SSE Streaming
         │ REST API
┌────────▼────────┐
│   FastAPI        │  Backend (AWS ECS Fargate)
│   + LangChain    │
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

## 🛠️ Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)
- PostgreSQL (NeonDB or local)

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/hospital-data-assistant.git
cd hospital-data-assistant

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

---

## 🐳 Docker Deploy

```bash
# Build and run with docker-compose
docker-compose up --build

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

## ☁️ AWS Deployment

### Prerequisites
- AWS CLI configured
- Terraform installed
- Docker installed
- AWS credentials with appropriate permissions

### Steps

1. **Configure Terraform variables**:
```bash
cd infra/terraform
terraform init
```

2. **Set variables**:
```bash
export TF_VAR_database_url="postgresql://..."
export TF_VAR_openai_api_key="sk-..."
export AWS_REGION="us-east-1"
```

3. **Run deploy script**:
```bash
chmod +x infra/aws/deploy.sh
./infra/aws/deploy.sh
```

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

### DevOps & Cloud
- Containerization (Docker)
- Infrastructure as Code (Terraform)
- AWS Services (ECS, ECR, VPC, ALB, CloudWatch)
- CI/CD pipelines

### Quality & Security
- Automated testing (unit, integration, E2E)
- Data validation
- Compliance (LGPD/HIPAA)
- Auditing and observability

### Modern Frontend
- Next.js 14 (App Router)
- TypeScript
- Responsive Design
- Real-time Updates

---

## 📝 License

This project is a **technical demonstration** with fictional data, created for educational and portfolio purposes.

---

## 👤 Author

**Your Name**
- LinkedIn: [your-profile](https://linkedin.com/in/your-profile)
- GitHub: [@your-username](https://github.com/your-username)
- Email: your.email@example.com

---

**⭐ If this project was helpful, consider giving it a star on GitHub!**

