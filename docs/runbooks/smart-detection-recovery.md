# Runbook: Smart Detection Recovery

## 📋 Visão Geral

Procedimentos de recuperação para falhas no sistema de Smart Response Detection (Feature 003).

**Última Atualização**: 2024-11-26  
**Responsável**: Equipe de Backend

---

## 🚨 Cenário 1: Schema Detection Falhando

### Sintomas
- Logs mostram: `Schema detection failed`
- Endpoint `/v1/schema/info` retorna 503
- Chat continua funcionando mas com schema stale

### Diagnóstico

```bash
# 1. Verificar logs do servidor
tail -f logs/app.log | grep schema_detector

# 2. Testar conexão com banco
curl http://localhost:8000/health

# 3. Verificar idade do cache
curl -I http://localhost:8000/v1/schema/info | grep X-Cache-Age
```

### Recuperação

#### Opção A: Cache Stale Funciona (Degraded Mode)
```bash
# Sistema continua operando com cache antigo
# Aguardar normalização da conexão com banco
# Ou forçar refresh quando banco voltar:
curl -X POST http://localhost:8000/v1/schema/refresh
```

#### Opção B: Sem Cache Disponível
```bash
# 1. Verificar permissões no PostgreSQL
psql -U user -d dbname -c "SELECT * FROM information_schema.tables LIMIT 1;"

# 2. Verificar variável de ambiente
echo $DATABASE_URL

# 3. Reiniciar servidor após correção
# O cache será populado no primeiro request
```

### Prevenção
- ✅ Monitorar alertas: schema detection failures > 3
- ✅ TTL adequado: não muito curto (1 hora é bom)
- ✅ Health checks regulares

---

## 🚨 Cenário 2: Falsos Positivos (Rejeita Perguntas Válidas)

### Sintomas
- Usuários relatam que perguntas válidas são rejeitadas
- Logs mostram `can_answer=False` para perguntas sobre tabelas existentes
- Taxa de rejeição > 5%

### Diagnóstico

```bash
# 1. Verificar threshold atual
grep CONFIDENCE_THRESHOLD .env

# 2. Analisar logs de decisões
grep "can_answer=False" logs/audit.log | tail -20

# 3. Testar pergunta específica
curl "http://localhost:8000/v1/chat/stream?session_id=test&prompt=Quantos%20leitos?"
```

### Recuperação

#### Ajustar Threshold de Confiança

```env
# Em .env
CONFIDENCE_THRESHOLD=0.60  # Diminuir de 0.70 para 0.60
```

#### Adicionar Sinônimos Faltantes

```json
// config/synonyms.json
{
  "mappings": {
    "camas": "leitos",
    "novo_termo": "tabela_existente"  // Adicionar aqui
  }
}
```

```bash
# Reiniciar servidor para recarregar sinônimos
```

### Prevenção
- ✅ Revisar semanalmente logs de perguntas rejeitadas
- ✅ Manter `synonyms.json` atualizado com feedback dos usuários
- ✅ Monitorar métrica: `unanswerable_questions_count`

---

## 🚨 Cenário 3: Falsos Negativos (Responde Perguntas Inválidas)

### Sintomas
- Sistema tenta gerar SQL para dados inexistentes
- Erros SQL frequentes: "table does not exist"
- Usuários recebem dados irrelevantes

### Diagnóstico

```bash
# Verificar threshold
grep CONFIDENCE_THRESHOLD .env

# Analisar erros SQL
grep "ERROR.*does not exist" logs/app.log | tail -20
```

### Recuperação

```env
# Aumentar threshold em .env
CONFIDENCE_THRESHOLD=0.80  # Era 0.70
```

### Prevenção
- ✅ Monitorar taxa de erros SQL após análise positiva
- ✅ Se taxa > 5%, aumentar threshold
- ✅ Revisar lógica de similarity matching

---

## 🚨 Cenário 4: Performance Degradada

### Sintomas
- Requests lentos (> 2 segundos)
- Logs mostram análise > 1 segundo
- Usuários relatam lentidão

### Diagnóstico

```bash
# Executar performance tests
cd apps/backend-fastapi
poetry run pytest tests/performance/test_benchmarks.py -v

# Verificar idade do cache
curl http://localhost:8000/v1/schema/stats
```

### Recuperação

#### Cache Não Está Funcionando

```python
# Verificar em logs:
# - "Schema cache hit" deve aparecer na maioria dos requests
# - Se sempre aparece "Refreshing schema cache", cache não está persistindo

# Possível causa: TTL muito curto
```

```env
# Aumentar TTL em .env
SCHEMA_CACHE_TTL_SECONDS=7200  # 2 horas em vez de 1
```

#### Query de Schema Muito Lenta

```sql
-- Verificar performance da query
EXPLAIN ANALYZE 
SELECT t.table_name, c.column_name, c.data_type, c.is_nullable
FROM information_schema.tables t
JOIN information_schema.columns c 
    ON t.table_name = c.table_name
WHERE t.table_schema = 'public';
```

### Prevenção
- ✅ Monitorar p95 latency de análise
- ✅ Alertar se > 1 segundo
- ✅ Cache hit rate > 95%

---

## 🚨 Cenário 5: Memory Leak (Cache Crescendo)

### Sintomas
- Memória do processo aumentando continuamente
- OOM (Out of Memory) após dias de execução

### Diagnóstico

```bash
# Verificar tamanho do schema
curl http://localhost:8000/v1/schema/stats | jq '.total_columns'

# Monitorar memória do processo
ps aux | grep uvicorn
```

### Recuperação

Se schema é muito grande (> 100 tabelas):

```python
# Implementar limite de cache ou LRU eviction
# (não implementado no MVP, mas pode ser adicionado)
```

### Prevenção
- ✅ Validar em staging com schema real
- ✅ Se schema > 100 tabelas, considerar filtrar tabelas irrelevantes
- ✅ Monitorar memória em produção

---

## 📞 Contatos de Suporte

**Equipe de Backend**: backend-team@hospital.com  
**On-call**: +55 11 9999-9999  
**Documentação**: https://docs.hospital.com/smart-detection

---

## ✅ Checklist de Recovery

Ao resolver um incidente:

- [ ] Identificar sintoma principal
- [ ] Consultar seção relevante deste runbook
- [ ] Executar passos de diagnóstico
- [ ] Aplicar solução de recuperação
- [ ] Validar que sistema voltou ao normal
- [ ] Documentar incidente em post-mortem
- [ ] Implementar prevenção se necessário
- [ ] Atualizar runbook com aprendizados

