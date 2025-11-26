# Migration Guide: Smart Response Detection (Feature 003)

## 📋 Visão Geral

Este guia documenta as mudanças necessárias para usar a Feature 003 (Smart Response Detection) em ambientes existentes.

**Data de Release**: 2024-11-26  
**Breaking Changes**: ❌ Nenhum (100% backward compatible)  
**Action Required**: ✅ Configuração opcional recomendada

---

## ✅ Backward Compatibility

**Importante**: Esta feature é **100% backward compatible**. Sistemas existentes continuarão funcionando sem modificações.

### O que funciona sem mudanças:
- ✅ Todos os endpoints existentes
- ✅ Formato SSE das respostas
- ✅ Clientes antigos ignoram novos marcadores (`[SMART_RESPONSE]`, `[PARTIAL_MATCH]`)
- ✅ Fluxo de SQL generation normal

---

## 🆕 O Que Mudou

### Novos Arquivos

```
apps/backend-fastapi/
├── config/
│   └── synonyms.json                    # ✨ NOVO: Mapeamento de sinônimos
├── src/
│   ├── domain/
│   │   ├── schema_info.py              # ✨ NOVO: Modelos de schema
│   │   └── question_analysis.py        # ✨ NOVO: Modelos de análise
│   ├── services/
│   │   ├── schema_detector_service.py  # ✨ NOVO: Detecção de schema
│   │   ├── question_analyzer_service.py # ✨ NOVO: Análise de perguntas
│   │   └── suggestion_generator_service.py # ✨ NOVO: Geração de sugestões
│   └── api/routes/
│       └── schema.py                   # ✨ NOVO: Endpoints de schema
├── tests/
│   ├── unit/
│   │   ├── test_schema_detector_service.py    # 5 testes
│   │   ├── test_question_analyzer_service.py  # 8 testes
│   │   └── test_suggestion_generator_service.py # 4 testes
│   ├── integration/
│   │   ├── test_smart_detection_flow.py       # 3 testes
│   │   ├── test_schema_api.py                 # 3 testes
│   │   └── test_schema_refresh.py             # 2 testes
│   ├── contract/
│   │   └── test_chat_api_backward_compat.py   # 2 testes
│   └── performance/
│       └── test_benchmarks.py                 # 4 testes
└── docs/
    ├── SMART_DETECTION.md              # ✨ NOVO: Documentação completa
    └── runbooks/
        └── smart-detection-recovery.md # ✨ NOVO: Runbook de recovery
```

### Arquivos Modificados

```
src/agents/sql_agent.py         # Integração com QuestionAnalyzerService
src/api/routes/chat.py          # Stream de smart responses
src/api/main.py                 # Registro de schema router
src/config.py                   # Novas variáveis de configuração
```

---

## 🔧 Configuração

### Variáveis de Ambiente (Opcionais)

Adicione ao seu `.env`:

```env
# ========================================
# Feature 003: Smart Response Detection
# ========================================

# Feature flag (default: true)
ENABLE_SMART_DETECTION=true

# Confidence threshold (0.0 a 1.0, default: 0.70)
# Quanto maior, mais conservador (rejeita mais perguntas)
CONFIDENCE_THRESHOLD=0.70

# Similarity threshold (0.0 a 1.0, default: 0.70)
# Para matching de strings similares (ex: "leito" → "leitos")
SIMILARITY_THRESHOLD=0.70

# Schema cache TTL em segundos (default: 3600 = 1 hora)
SCHEMA_CACHE_TTL_SECONDS=3600

# Path para arquivo de sinônimos (default: config/synonyms.json)
SYNONYMS_FILE_PATH=apps/backend-fastapi/config/synonyms.json
```

### Arquivo de Sinônimos

Crie `apps/backend-fastapi/config/synonyms.json`:

```json
{
  "version": "1.0.0",
  "updated": "2024-11-26",
  "mappings": {
    "camas": "leitos",
    "cama": "leitos",
    "quartos": "leitos",
    "consultas": "atendimentos",
    "consulta": "atendimentos",
    "paciente": "pacientes",
    "medico": "medicos",
    "enfermeiro": "enfermeiros",
    "hospital": "hospitais",
    "clinica": "clinicas"
  }
}
```

**Customize** de acordo com seu domínio!

---

## 📊 Novos Endpoints

### GET /v1/schema/info
Retorna informações do schema atual (útil para debugging).

**Exemplo:**
```bash
curl http://localhost:8000/v1/schema/info
```

**Response:**
```json
{
  "tables": [...],
  "last_updated": "2024-11-26T14:30:00Z",
  "version": "1.0.0"
}
```

### GET /v1/schema/stats
Estatísticas sobre o schema.

### POST /v1/schema/refresh
Força atualização do cache de schema.

**Exemplo:**
```bash
curl -X POST http://localhost:8000/v1/schema/refresh
```

---

## 🔄 Migração Step-by-Step

### Ambiente de Desenvolvimento

```bash
# 1. Pull das mudanças
git pull origin main

# 2. Instalar dependências (nenhuma nova!)
cd apps/backend-fastapi
poetry install

# 3. Criar arquivo de sinônimos
cp config/synonyms.example.json config/synonyms.json
# Edite config/synonyms.json conforme necessário

# 4. (Opcional) Adicionar variáveis ao .env
echo "ENABLE_SMART_DETECTION=true" >> .env
echo "CONFIDENCE_THRESHOLD=0.70" >> .env
echo "SIMILARITY_THRESHOLD=0.70" >> .env
echo "SCHEMA_CACHE_TTL_SECONDS=3600" >> .env

# 5. Executar testes
poetry run pytest tests/ -v

# 6. Iniciar servidor
poetry run uvicorn src.api.main:app --reload
```

### Ambiente de Produção

#### Opção A: Deploy Direto (Recomendado)

```bash
# 1. Deploy normalmente via CI/CD
# Sistema usa defaults seguros se variáveis não forem definidas

# 2. Verificar funcionamento
curl https://seu-dominio.com/v1/schema/info

# 3. Monitorar logs
tail -f logs/app.log | grep smart_detection
```

#### Opção B: Deploy Gradual com Feature Flag

```bash
# 1. Deploy com feature desabilitada
export ENABLE_SMART_DETECTION=false
# Deploy...

# 2. Após validação, habilitar feature
export ENABLE_SMART_DETECTION=true
# Redeploy ou restart

# 3. Monitorar métricas por 24h
# - Taxa de rejeição de perguntas
# - Latência de análise
# - Cache hit rate
```

---

## 🧪 Validação

### Teste Básico

```bash
# 1. Pergunta respondível (deve funcionar normalmente)
curl "http://localhost:8000/v1/chat/stream?session_id=test&prompt=Quantos%20leitos?"
# Espera: SQL normal, resultados

# 2. Pergunta não respondível (deve ativar smart response)
curl "http://localhost:8000/v1/chat/stream?session_id=test&prompt=Quais%20protocolos?"
# Espera: [SMART_RESPONSE], explicação, sugestões

# 3. Pergunta com sinônimo (deve mapear)
curl "http://localhost:8000/v1/chat/stream?session_id=test&prompt=Quantas%20camas?"
# Espera: "camas" → "leitos", SQL normal
```

### Testes Automatizados

```bash
cd apps/backend-fastapi

# Todos os testes
poetry run pytest tests/ -v

# Apenas smart detection
poetry run pytest tests/unit/test_schema_detector_service.py -v
poetry run pytest tests/unit/test_question_analyzer_service.py -v
poetry run pytest tests/unit/test_suggestion_generator_service.py -v
poetry run pytest tests/integration/test_smart_detection_flow.py -v

# Performance benchmarks
poetry run pytest tests/performance/test_benchmarks.py -v

# Backward compatibility
poetry run pytest tests/contract/test_chat_api_backward_compat.py -v
```

---

## 📊 Monitoramento

### Métricas a Monitorar

1. **Taxa de Rejeição**: 
   - `unanswerable_questions_count / total_questions`
   - **Target**: < 5%

2. **Latência de Análise**:
   - `smart_response_analysis_duration_ms` (p95)
   - **Target**: < 500ms

3. **Cache Hit Rate**:
   - `schema_cache_hits / schema_cache_requests`
   - **Target**: > 95%

4. **Falsos Positivos**:
   - Perguntas válidas rejeitadas
   - **Target**: < 2%

### Alertas Recomendados

```yaml
# Prometheus alerts (exemplo)
groups:
  - name: smart_detection
    rules:
      - alert: HighRejectionRate
        expr: rate(unanswerable_questions_count[5m]) > 0.1
        for: 5m
        annotations:
          summary: "Taxa de rejeição alta (>10%)"
          
      - alert: SchemaDetectionFailure
        expr: schema_detection_errors > 3
        for: 1m
        annotations:
          summary: "Schema detection falhando consecutivamente"
          
      - alert: SlowAnalysis
        expr: histogram_quantile(0.95, smart_response_analysis_duration_ms) > 1000
        for: 5m
        annotations:
          summary: "Análise lenta (p95 > 1s)"
```

---

## 🐛 Troubleshooting

### Problema: Feature não está ativando

**Verificar:**
```bash
# 1. Variável de ambiente
echo $ENABLE_SMART_DETECTION

# 2. Logs de inicialização
grep "Smart detection" logs/app.log

# 3. Testar endpoint de schema
curl http://localhost:8000/v1/schema/info
```

### Problema: Cache não está funcionando

**Verificar:**
```bash
# Cache age deve ser < TTL
curl -I http://localhost:8000/v1/schema/info | grep X-Cache-Age

# Forçar refresh
curl -X POST http://localhost:8000/v1/schema/refresh
```

### Problema: Muitas rejeições

**Solução:**
```env
# Diminuir threshold em .env
CONFIDENCE_THRESHOLD=0.60  # Era 0.70

# Adicionar sinônimos em config/synonyms.json
```

Ver **runbook completo**: `docs/runbooks/smart-detection-recovery.md`

---

## 📚 Documentação Adicional

- **Feature Completa**: `apps/backend-fastapi/docs/SMART_DETECTION.md`
- **Runbook de Recovery**: `docs/runbooks/smart-detection-recovery.md`
- **Especificação Original**: `specs/003-smart-response-detection/spec.md`
- **Plano de Implementação**: `specs/003-smart-response-detection/plan.md`
- **Tarefas**: `specs/003-smart-response-detection/tasks.md`

---

## ✅ Checklist de Migração

### Pre-deployment
- [ ] Pull das mudanças do repositório
- [ ] Executar testes localmente (`pytest tests/ -v`)
- [ ] Criar `config/synonyms.json` customizado
- [ ] (Opcional) Adicionar variáveis ao `.env`
- [ ] Validar localmente com curl/Postman

### Deployment
- [ ] Deploy para staging
- [ ] Executar smoke tests em staging
- [ ] Monitorar logs por 1 hora
- [ ] Deploy para produção
- [ ] Verificar `/v1/schema/info` responde 200

### Post-deployment
- [ ] Monitorar métricas por 24h
- [ ] Ajustar thresholds se necessário
- [ ] Adicionar sinônimos conforme feedback
- [ ] Documentar learnings no runbook

---

## 🎓 Training para o Time

**Vídeo de Overview**: [Link para vídeo interno]  
**Documentação**: `docs/SMART_DETECTION.md`  
**Runbook**: `docs/runbooks/smart-detection-recovery.md`

**Próximos Passos**:
1. Ler documentação completa
2. Executar testes localmente
3. Fazer deploy em dev/staging
4. Validar backward compatibility
5. Deploy em produção com monitoramento

---

## 📞 Suporte

**Dúvidas**: backend-team@hospital.com  
**Incidentes**: Use runbook `docs/runbooks/smart-detection-recovery.md`  
**Feature Requests**: Abra issue no GitHub com label `feature-003`

