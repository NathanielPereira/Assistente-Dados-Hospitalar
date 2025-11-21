# Playbook de Resposta a Incidentes

## Gatilhos de Alertas

### HIGH_LATENCY
- **Gatilho**: Latência p95 > 2s
- **Ação**: Verificar carga do banco, cache, e otimizar queries
- **Escalação**: Se persistir > 5min, ativar modo degradado

### DEGRADED_MODE_ACTIVATED
- **Gatilho**: Sistema entra em modo read-only
- **Ação**: 
  1. Verificar logs de integrações (NeonDB, S3, RAG)
  2. Ativar circuit breakers
  3. Notificar equipe SRE
- **Recuperação**: Após resolução, desativar modo degradado manualmente

### INTEGRATION_FAILURE
- **Gatilho**: Integração externa falha
- **Ação**:
  1. Verificar status do serviço externo
  2. Ativar fallback (cache/knowledge base)
  3. Registrar incidente
- **Escalação**: Se falha persistir > 15min, ativar modo degradado

### LOW_UPTIME
- **Gatilho**: Uptime < 99%
- **Ação**: Investigar causas raiz (deploy, infra, dependências)
- **Escalação**: Se < 95%, comunicar stakeholders

## Procedimentos de Recuperação

1. **Identificar causa raiz** via logs e métricas
2. **Isolar problema** (circuit breakers, feature flags)
3. **Aplicar correção** ou workaround
4. **Validar recuperação** (health check, testes)
5. **Documentar incidente** e atualizar playbook se necessário

## Contatos de Escalação

- **SRE**: [definir]
- **Compliance**: [definir]
- **Desenvolvimento**: [definir]
