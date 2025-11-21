#!/bin/bash
# Script para executar todos os testes do projeto

set -e

echo "=== Executando Suite Completa de Testes ==="
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Testes Backend
echo -e "[1/6] Testes Backend (Unitários + Contrato)"
cd apps/backend-fastapi
if poetry run pytest tests/ -v; then
    echo -e "✓ Backend tests passed"
else
    echo -e "✗ Backend tests failed"
    exit 1
fi
cd ../..

# 2. Testes de Performance
echo -e "[2/6] Testes de Performance"
cd apps/backend-fastapi
if poetry run pytest tests/perf/ -v; then
    echo -e "✓ Performance tests passed"
else
    echo -e "✗ Performance tests failed"
    exit 1
fi
cd ../..

# 3. Testes E2E Frontend
echo -e "[3/6] Testes E2E Frontend"
cd apps/frontend-next
if pnpm test:e2e; then
    echo -e "✓ E2E tests passed"
else
    echo -e "✗ E2E tests failed"
    exit 1
fi
cd ../..

# 4. Validação Great Expectations
echo -e "[4/6] Validação de Dados (Great Expectations)"
cd shared/datasets
if great_expectations checkpoint run masking_per_layer; then
    echo -e "✓ Data validation passed"
else
    echo -e "⚠ Data validation warnings (continuando...)"
fi
cd ../..

# 5. Testes de Observabilidade
echo -e "[5/6] Testes de Observabilidade"
cd apps/backend-fastapi
if poetry run pytest tests/observability/ -v; then
    echo -e "✓ Observability tests passed"
else
    echo -e "✗ Observability tests failed"
    exit 1
fi
cd ../..

# 6. Resumo
echo ""
echo -e "=== Todos os Testes Concluídos ==="
echo ""
echo "Próximos passos:"
echo "  - Executar simulações de falha: python infra/scripts/chaos_mode.py --scenario all"
echo "  - Validar exportos de auditoria manualmente"
echo "  - Revisar cobertura de testes"
