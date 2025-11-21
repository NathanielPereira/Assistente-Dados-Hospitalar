# Drills de Auditoria

## Objetivo
Validar que trilhas de auditoria estão sendo geradas corretamente e podem ser exportadas para auditorias externas.

## Procedimento

### 1. Geração de Trilhas
Execute operações no sistema e verifique que cada uma gera AuditEntry:
- Chat session (US1)
- SQL execution (US2)
- Export de auditoria (US3)

### 2. Validação de Hashes
`ash
python scripts/validate_audit_hashes.py --session-id <id>
`
Verifica que hashes de entrada/saída são consistentes.

### 3. Exportação
- Exporte CSV: /v1/audit/exports?format=csv&days=7
- Exporte JSON: /v1/audit/exports?format=json&days=7
- Valide estrutura conforme contrato OpenAPI

### 4. Retenção
Execute job de retenção:
`ash
python apps/backend-fastapi/src/services/data_retention_job.py
`
Verifique que dados antigos são anonimizados ou removidos conforme política.

## Critérios de Sucesso
- 100% das interações geram AuditEntry
- Hashes são verificáveis
- Exportos são completos e legíveis
- Retenção segue política de 2 anos
