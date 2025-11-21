# Pipeline de Auditoria — Assistente de Dados Hospitalar IA

## Formato de Eventos
- `event_id`: UUID v4
- `query_session_id`: UUID referenciando QuerySession
- `event_type`: PROMPT | SQL_EXECUTED | RAG_FETCH | ALERT | EXPORT
- `actor`: usuário ou serviço com papel (CONSULTOR/ANALISTA/COMPLIANCE/SYSTEM)
- `input_hash` / `output_hash`: SHA-256 base64
- `legal_basis`: CONSENT_DEMO | LEGIT_INTEREST_DEMO
- `storage_pointer`: URI imutável (S3 versionado)
- `created_at`: ISO8601 UTC

## Fluxo
1. Backend gera `AuditEntry` ao iniciar/encerrar QuerySession.
2. Evento é persistido em NeonDB (tabela append-only).
3. Copia-se JSON do evento para bucket S3 com versionamento habilitado.
4. Exportos CSV/JSON são gerados por `AuditExporter` e disponibilizados via URL temporária.

## Retenção e Controles
- Retenção mínima: 2 anos (stack demo).
- Storage S3 em modo WORM (Write Once Read Many).
- Alterações exigem nova versão do arquivo; exclusão só mediante processo de compliance.

## Integração com Observabilidade
- Eventos críticos (ALERT, EXPORT) geram métricas Prometheus (`audit_events_total`, `audit_export_latency_ms`).
- Painel Observability Control Room consome `/v1/observability/health` e apresenta status das filas de auditoria.

