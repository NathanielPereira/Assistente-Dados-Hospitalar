# Quick Start: Sistema de Fallback e Cache de Respostas para LLM

**Feature**: 002-llm-fallback-cache  
**Date**: 2025-01-21

## Visão Geral

Este guia mostra como configurar e usar o sistema de fallback de APIs de LLM **gratuitas** e cache de respostas. O sistema permite que o assistente continue funcionando mesmo quando APIs principais estão indisponíveis e **maximiza o número de perguntas por mês** usando múltiplos provedores gratuitos.

## Pré-requisitos

- Python 3.11+
- Backend FastAPI rodando
- Contas gratuitas em pelo menos uma das APIs: Google Gemini, Anthropic Claude, Hugging Face, ou OpenRouter

## Configuração Inicial

### 1. Obter Chaves de API Gratuitas

**Google Gemini** (Recomendado - melhor limite):
1. Acesse: https://makersuite.google.com/app/apikey
2. Crie uma chave gratuita
3. Limite: ~15 RPM (requests per minute)

**Anthropic Claude**:
1. Acesse: https://console.anthropic.com/
2. Crie conta e obtenha chave API
3. Limite: Baseado em créditos mensais gratuitos

**Hugging Face**:
1. Acesse: https://huggingface.co/settings/tokens
2. Crie um token de acesso
3. Limite: 30.000 caracteres/mês

**OpenRouter** (Opcional):
1. Acesse: https://openrouter.ai/keys
2. Crie uma chave
3. Limite: 50 requests/dia (gratuito) ou 1000/dia com $10 mínimo

### 2. Instalar Dependências

```bash
cd apps/backend-fastapi
poetry add langchain-google-genai langchain-anthropic langchain-huggingface langchain-openai
# Ou para correspondência avançada (opcional):
poetry add sentence-transformers
```

### 3. Configurar Variáveis de Ambiente

Adicione ao `.env`:

```env
# OpenAI (existente - opcional se sem créditos)
OPENAI_API_KEY=sk-...

# Google Gemini (fallback 1 - PRIORIDADE: melhor limite gratuito)
GOOGLE_API_KEY=...

# Anthropic Claude (fallback 2)
ANTHROPIC_API_KEY=sk-ant-...

# Hugging Face (fallback 3)
HUGGINGFACE_API_KEY=hf_...

# OpenRouter (fallback 4 - opcional)
OPENROUTER_API_KEY=sk-or-...

# Ordem de prioridade (separado por vírgula)
# Sistema rotaciona entre provedores para maximizar limites gratuitos
LLM_PROVIDER_PRIORITY=google,anthropic,huggingface,openrouter

# Estratégia de rotação (round_robin, least_used, priority)
LLM_ROTATION_STRATEGY=round_robin
```

### 3. Criar Arquivo de Cache Inicial

Crie `apps/backend-fastapi/data/response_cache.json`:

```json
{
  "version": "1.0",
  "last_updated": "2025-01-21T10:00:00Z",
  "entries": [
    {
      "entry_id": "550e8400-e29b-41d4-a716-446655440000",
      "question": "Qual a taxa de ocupação da UTI pediátrica?",
      "variations": [
        "taxa de ocupação UTI pediátrica",
        "ocupação UTI pediátrica",
        "quantos leitos ocupados UTI pediátrica"
      ],
      "keywords": ["uti", "pediatrica", "ocupacao", "taxa"],
      "sql": "SELECT COUNT(*) FILTER (WHERE status = 'ocupado') as ocupados, COUNT(*) as total, ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'ocupado') / COUNT(*), 2) as taxa_ocupacao FROM leitos WHERE setor = 'UTI_PEDIATRICA';",
      "response_template": "A UTI pediátrica está com {taxa_ocupacao}% de ocupação ({ocupados} de {total} leitos ocupados).",
      "requires_realtime": true,
      "metadata": {
        "created_at": "2025-01-21T10:00:00Z",
        "last_used": null,
        "usage_count": 0,
        "confidence": 0.95,
        "validated": true,
        "provider_used": "openai"
      }
    }
  ]
}
```

## Uso Básico

### Testar Fallback de API

1. **Configure pelo menos uma API gratuita** (Google Gemini recomendado):
   ```bash
   # No .env, adicione:
   GOOGLE_API_KEY=sua-chave-aqui
   ```

2. **Faça uma pergunta no chat**:
   ```
   "Qual a taxa de ocupação da UTI pediátrica?"
   ```

3. **Sistema deve**:
   - Tentar Google Gemini primeiro (se configurado)
   - Se Google Gemini falhar ou atingir limite, tentar Anthropic
   - Se Anthropic falhar, tentar Hugging Face
   - Se todos falharem, tentar OpenRouter (se configurado)
   - Se todos falharem, usar cache se disponível
   - Sistema rotaciona entre provedores para distribuir carga

### Verificar Status dos Provedores

```bash
curl http://localhost:8000/v1/llm/providers
```

Resposta esperada:
```json
{
  "providers": [
    {
      "provider_id": "google",
      "status": "AVAILABLE",
      "circuit_breaker_open": false,
      "requests_today": 45,
      "limit_reached": false
    },
    {
      "provider_id": "anthropic",
      "status": "AVAILABLE",
      "circuit_breaker_open": false,
      "requests_today": 12
    },
    {
      "provider_id": "huggingface",
      "status": "AVAILABLE",
      "circuit_breaker_open": false,
      "characters_used": 15000,
      "characters_limit": 30000
    }
  ],
  "active_provider": "google",
  "rotation_strategy": "round_robin"
}
```

### Adicionar Entrada Manual ao Cache

```bash
curl -X POST http://localhost:8000/v1/cache/entries \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quantos leitos disponíveis temos?",
    "keywords": ["leitos", "disponiveis"],
    "sql": "SELECT COUNT(*) as total FROM leitos WHERE status = '\''disponivel'\'';",
    "response_template": "Temos {total} leitos disponíveis no momento.",
    "requires_realtime": true
  }'
```

### Buscar Correspondência no Cache

```bash
curl -X POST http://localhost:8000/v1/cache/match \
  -H "Content-Type: application/json" \
  -d '{
    "question": "qual ocupação uti pediátrica?"
  }'
```

Resposta esperada:
```json
{
  "matched": true,
  "entry": {
    "entry_id": "550e8400-e29b-41d4-a716-446655440000",
    "question": "Qual a taxa de ocupação da UTI pediátrica?",
    ...
  },
  "confidence": 0.85
}
```

## Geração Automática de Cache

O sistema gera automaticamente novas entradas de cache quando:

1. LLM está disponível e gera resposta válida
2. SQL é executado com sucesso
3. Validação passa (SQL válido, resultados não vazios, resposta formatada)

**Exemplo de fluxo**:
```
Usuário: "Qual a receita média por especialidade?"
  → LLM gera SQL
  → SQL executado com sucesso
  → Validação passa
  → CacheEntry criada automaticamente
  → Próxima vez que pergunta similar for feita, usa cache
```

## Monitoramento

### Estatísticas do Cache

```bash
curl http://localhost:8000/v1/cache/stats
```

Resposta esperada:
```json
{
  "total_entries": 15,
  "cache_hit_rate": 0.75,
  "total_requests": 100,
  "cache_size_bytes": 245760
}
```

### Logs

O sistema registra:
- Tentativas de fallback entre provedores
- Criação de novas entradas de cache
- Falhas de validação
- Abertura/fechamento de circuit breakers

Exemplo de log:
```
[INFO] LLM Provider 'openai' failed, trying 'anthropic'
[INFO] Cache hit for question: "qual ocupação uti pediátrica?"
[INFO] New cache entry created: entry_id=550e8400-...
[WARN] Validation failed for cache entry: SQL returned empty results
```

## Troubleshooting

### Cache não está sendo usado

1. Verifique se arquivo existe: `data/response_cache.json`
2. Verifique logs para erros de carregamento
3. Teste correspondência manual: `POST /v1/cache/match`

### Fallback não está funcionando

1. Verifique variáveis de ambiente (chaves de API)
2. Verifique status dos provedores: `GET /v1/llm/providers`
3. Verifique circuit breakers (podem estar abertos)

### Validação sempre falha

1. Verifique SQL gerado (deve ser válido)
2. Verifique se banco de dados está acessível
3. Verifique logs de validação para detalhes

## Maximizando Perguntas por Mês

### Estratégia Recomendada

1. **Configure todas as APIs gratuitas disponíveis**:
   - Google Gemini: ~15 RPM = ~21.600 perguntas/mês (se usado continuamente)
   - Anthropic Claude: Varia conforme créditos mensais
   - Hugging Face: 30.000 caracteres/mês (depende do tamanho das perguntas)
   - OpenRouter: 50/dia = ~1.500/mês (gratuito) ou 30.000/mês ($10)

2. **Use rotação round-robin**:
   - Distribui requisições entre todos os provedores
   - Evita esgotar limites de um único provedor
   - Maximiza uso total combinado

3. **Priorize cache**:
   - Perguntas frequentes devem estar no cache
   - Cache reduz uso de APIs para perguntas repetidas
   - Permite mais perguntas novas com APIs disponíveis

4. **Monitor uso**:
   - Verifique `/v1/llm/providers` regularmente
   - Ajuste prioridades se um provedor estiver próximo do limite
   - Adicione mais perguntas ao cache quando possível

### Estimativa de Capacidade

Com todas as APIs configuradas e rotação ativa:
- **Estimativa conservadora**: ~2.000-3.000 perguntas/mês
- **Estimativa otimista**: ~5.000-10.000 perguntas/mês (com cache eficiente)

## Próximos Passos

- Adicionar mais perguntas ao cache inicial (reduz uso de APIs)
- Monitorar taxa de acerto do cache e ajustar correspondência
- Configurar alertas quando limites estão próximos de esgotar
- Migrar cache para PostgreSQL se crescer muito (>100 entradas)
- Implementar estratégia de "cache-first" para perguntas conhecidas

