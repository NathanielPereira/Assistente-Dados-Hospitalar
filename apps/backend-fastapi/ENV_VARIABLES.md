# 🔑 Variáveis de Ambiente Necessárias

Este documento lista todas as variáveis de ambiente que precisam ser configuradas no **Render** para o sistema funcionar corretamente.

## ⚠️ IMPORTANTE: Configure no Render

No painel do Render, vá em **Environment** e adicione as variáveis abaixo. **Não** adicione no arquivo `.env` do código (ele não é commitado no Git).

## 📋 Variáveis Obrigatórias

### Banco de Dados
```env
DATABASE_URL=postgresql://user:password@host/database
```

### Ambiente
```env
ENVIRONMENT=production
```

## 🤖 Provedores LLM (Configure pelo menos 2 para fallback)

### Google Gemini (Recomendado - Gratuito)
```env
GOOGLE_API_KEY=sua-chave-aqui
```
- **Onde obter**: https://makersuite.google.com/app/apikey
- **Limite gratuito**: ~15 RPM (requests per minute)
- **Recomendado**: Configure primeiro para reduzir custos

### OpenAI (Opcional - Requer créditos)
```env
OPENAI_API_KEY=sk-sua-chave-aqui
```
- **Onde obter**: https://platform.openai.com/api-keys
- **Limite**: Baseado em créditos da conta

### Anthropic Claude (Opcional)
```env
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
```
- **Onde obter**: https://console.anthropic.com/
- **Limite**: Baseado em créditos mensais gratuitos

### Hugging Face (Opcional)
```env
HUGGINGFACE_API_KEY=hf_sua-chave-aqui
```
- **Onde obter**: https://huggingface.co/settings/tokens
- **Limite**: 30.000 caracteres/mês (gratuito)

### OpenRouter (Opcional)
```env
OPENROUTER_API_KEY=sk-or-sua-chave-aqui
```
- **Onde obter**: https://openrouter.ai/keys
- **Limite**: 50 requests/dia (gratuito) ou 1000/dia com $10 mínimo

## ⚙️ Configuração de Provedores

### Prioridade dos Provedores
```env
LLM_PROVIDER_PRIORITY=google,openai,openrouter,huggingface
```
- **Ordem**: O sistema tentará usar nesta ordem
- **Recomendado**: Coloque Google primeiro (gratuito) para reduzir custos

### Estratégia de Rotação
```env
LLM_ROTATION_STRATEGY=priority
```
- **`priority`**: Sempre usa o primeiro disponível (recomendado)
- **`round_robin`**: Alterna entre provedores

## 🎯 Smart Detection (Feature 003)

```env
ENABLE_SMART_DETECTION=true
CONFIDENCE_THRESHOLD=0.70
SIMILARITY_THRESHOLD=0.70
SCHEMA_CACHE_TTL_SECONDS=3600
```

## 📝 Exemplo Completo para Render

```env
# Banco de Dados
DATABASE_URL=postgresql://user:password@host/database

# Provedores LLM (configure pelo menos 2)
GOOGLE_API_KEY=sua-chave-google
OPENAI_API_KEY=sk-sua-chave-openai
OPENROUTER_API_KEY=sk-or-sua-chave-openrouter
HUGGINGFACE_API_KEY=hf_sua-chave-huggingface

# Configuração
ENVIRONMENT=production
LLM_PROVIDER_PRIORITY=google,openai,openrouter,huggingface
LLM_ROTATION_STRATEGY=priority

# Smart Detection
ENABLE_SMART_DETECTION=true
CONFIDENCE_THRESHOLD=0.70
SIMILARITY_THRESHOLD=0.70
SCHEMA_CACHE_TTL_SECONDS=3600
```

## ✅ Como Verificar se Está Configurado

Após configurar as variáveis no Render e fazer deploy, verifique os logs:

1. **Logs esperados** (com múltiplos provedores):
   ```
   [OK] LLM inicializado (4/4 provedores disponíveis)
   ```

2. **Logs de aviso** (apenas 1 provedor):
   ```
   ⚠️ Apenas 1 provedor LLM configurado. Configure mais provedores para fallback automático.
   ```

3. **Logs de erro** (nenhum provedor):
   ```
   ❌ Nenhum provedor LLM disponível! Configure pelo menos uma API key.
   ⚠️ Provedores não configurados (faltam API keys): GOOGLE_API_KEY, OPENROUTER_API_KEY, HUGGINGFACE_API_KEY
   ```

## 🔍 Troubleshooting

### Problema: Apenas 1 provedor sendo reconhecido

**Solução**: Verifique se todas as API keys estão configuradas no Render:
1. Acesse o painel do Render
2. Vá em **Environment**
3. Verifique se todas as variáveis `*_API_KEY` estão presentes
4. Faça um novo deploy após adicionar as variáveis

### Problema: Provedores não inicializam

**Solução**: 
1. Verifique se as chaves de API são válidas
2. Verifique os logs do Render para mensagens de erro específicas
3. Certifique-se de que as variáveis estão escritas corretamente (sem espaços extras)

