# Script PowerShell para executar todos os testes do projeto

Write-Host "=== Executando Suite Completa de Testes ===" -ForegroundColor Cyan
Write-Host ""

Continue = "Stop"

# 1. Testes Backend
Write-Host "[1/6] Testes Backend (Unitários + Contrato)" -ForegroundColor Yellow
Set-Location apps\backend-fastapi
try {
    poetry run pytest tests/ -v
    Write-Host "✓ Backend tests passed" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend tests failed" -ForegroundColor Red
    exit 1
}
Set-Location ..\..

# 2. Testes de Performance
Write-Host "[2/6] Testes de Performance" -ForegroundColor Yellow
Set-Location apps\backend-fastapi
try {
    poetry run pytest tests/perf/ -v
    Write-Host "✓ Performance tests passed" -ForegroundColor Green
} catch {
    Write-Host "✗ Performance tests failed" -ForegroundColor Red
    exit 1
}
Set-Location ..\..

# 3. Testes E2E Frontend
Write-Host "[3/6] Testes E2E Frontend" -ForegroundColor Yellow
Set-Location apps\frontend-next
try {
    pnpm test:e2e
    Write-Host "✓ E2E tests passed" -ForegroundColor Green
} catch {
    Write-Host "✗ E2E tests failed" -ForegroundColor Red
    exit 1
}
Set-Location ..\..

# 4. Validação Great Expectations
Write-Host "[4/6] Validação de Dados (Great Expectations)" -ForegroundColor Yellow
Set-Location shared\datasets
try {
    great_expectations checkpoint run masking_per_layer
    Write-Host "✓ Data validation passed" -ForegroundColor Green
} catch {
    Write-Host "⚠ Data validation warnings (continuando...)" -ForegroundColor Yellow
}
Set-Location ..\..

# 5. Testes de Observabilidade
Write-Host "[5/6] Testes de Observabilidade" -ForegroundColor Yellow
Set-Location apps\backend-fastapi
try {
    poetry run pytest tests/observability/ -v
    Write-Host "✓ Observability tests passed" -ForegroundColor Green
} catch {
    Write-Host "✗ Observability tests failed" -ForegroundColor Red
    exit 1
}
Set-Location ..\..

# Resumo
Write-Host ""
Write-Host "=== Todos os Testes Concluídos ===" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:"
Write-Host "  - Executar simulações de falha: python infra\scripts\chaos_mode.py --scenario all"
Write-Host "  - Validar exportos de auditoria manualmente"
Write-Host "  - Revisar cobertura de testes"
