# Dataset de Auditoria para Demonstração

## Sessões de Exemplo

### Sessão 1 - Consulta Clínica (US1)
- **Session ID**: 550e8400-e29b-41d4-a716-446655440000
- **Usuário**: consultor-clinico-001
- **Prompt**: "Qual taxa de ocupação da UTI pediátrica e qual protocolo aplicar?"
- **SQL Executado**: SELECT COUNT(*) as ocupados, COUNT(*) FILTER (WHERE disponivel = true) as disponiveis FROM leitos WHERE setor = 'UTI_PEDIATRICA'
- **Documentos Citados**: protocolo-uti-pediatrica-v2.1.pdf
- **Base Legal**: Consentimento para demonstração (fictício)
- **Timestamp**: 2025-11-20T10:00:00Z

### Sessão 2 - SQL Assistido (US2)
- **Session ID**: 550e8400-e29b-41d4-a716-446655440001
- **Usuário**: nalista-dados-001
- **Prompt Original**: "calcular receita média por especialidade"
- **SQL Sugerido**: SELECT e.nome, AVG(a.valor) as receita_media FROM especialidades e JOIN atendimentos a ON a.especialidade_id = e.id GROUP BY e.id, e.nome
- **SQL Aprovado**: [mesmo, com comentários adicionais]
- **Resultados**: 15 especialidades, receita média R$ 1.234,56
- **Base Legal**: Análise operacional (fictício)
- **Timestamp**: 2025-11-20T10:15:00Z

### Sessão 3 - Compliance (US3)
- **Session ID**: 550e8400-e29b-41d4-a716-446655440002
- **Usuário**: oficial-compliance-001
- **Ação**: Exporto de auditoria (últimos 7 dias)
- **Formato**: JSON
- **Registros**: 42 sessões, 3 usuários
- **Base Legal**: Auditoria interna (fictício)
- **Timestamp**: 2025-11-20T11:00:00Z

## Métricas de Demonstração

- **Total de Sessões**: 42
- **Usuários Únicos**: 3
- **Taxa de Sucesso**: 100%
- **Latência p95**: 1.8s
- **Uptime**: 99.7%
- **Modo Degradado**: Nunca ativado (ambiente demo)

## Dashboards Exportáveis

- Grafana: infra/monitoring/grafana_dashboards/agent.json
- Observability Control Room: /observability (frontend)
- Compliance Panel: /compliance (frontend)
