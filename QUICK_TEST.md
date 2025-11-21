# Testes Rápidos - Guia Resumido

## Setup Inicial

`powershell
# 1. Instalar dependências
pnpm install
poetry install --with dev

# 2. Configurar ambiente
# Criar .env com variáveis necessárias (veja .env.example)
`

## Testes Essenciais (5 minutos)

`powershell
# Backend - Testes unitários e contrato
cd apps\backend-fastapi
poetry run pytest tests\ -v

# Frontend - Testes E2E
cd ..\frontend-next
pnpm test:e2e
`

## Testes Completos (15 minutos)

`powershell
# Executar suite completa
.\scripts\run-all-tests.ps1
`

## Testes Manuais (UI)

1. **Iniciar servidores:**
   `powershell
   # Terminal 1 - Backend
   cd apps\backend-fastapi
   poetry run uvicorn src.api.main:app --reload

   # Terminal 2 - Frontend
   cd apps\frontend-next
   pnpm dev
   `

2. **Testar funcionalidades:**
   - Chat: http://localhost:3000/chat
   - SQL Workbench: http://localhost:3000/sql-workbench
   - Compliance: http://localhost:3000/compliance
   - Observability: http://localhost:3000/observability

## Validação de Compliance

`powershell
# Exportar auditoria
curl "http://localhost:8000/v1/audit/exports?format=json&days=7"

# Verificar health
curl http://localhost:8000/v1/observability/health
`

## Simulações de Falha

`powershell
python infra\scripts\chaos_mode.py --scenario all
`

## Documentação Completa

Veja TESTING.md para guia detalhado.
