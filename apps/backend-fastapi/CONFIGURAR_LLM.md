# 🤖 Configurar LangChain/OpenAI

## Status Atual

✅ **Banco de dados conectado** - NeonDB funcionando  
✅ **SQLAgent implementado** - Pode gerar SQL automaticamente  
⚠️ **LLM não configurado** - Precisa de API Key da OpenAI

## Como Funciona

O sistema tem **dois modos de operação**:

### 1. **Modo com LangChain (Recomendado)**
- Requer: `OPENAI_API_KEY` configurada
- Usa: GPT-3.5-turbo para gerar SQL inteligente
- Vantagem: SQL mais preciso e contextualizado

### 2. **Modo Fallback (Funciona sem API Key)**
- Não requer: API Key
- Usa: SQL simples baseado em palavras-chave
- Vantagem: Funciona imediatamente, mas SQL é mais básico

## Como Configurar OpenAI

### Passo 1: Obter API Key

1. Acesse: https://platform.openai.com/api-keys
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave (ela só aparece uma vez!)

### Passo 2: Adicionar no .env

Edite o arquivo `apps/backend-fastapi/.env` e adicione:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
```

### Passo 3: Reiniciar o Servidor

O servidor detectará automaticamente a API Key e inicializará o LLM.

## Testar

Após configurar, teste fazendo uma pergunta no chat:

- **Com LLM**: "Qual a taxa de ocupação da UTI pediátrica?"
  - Gera SQL inteligente usando LangChain
  
- **Sem LLM**: Mesma pergunta
  - Gera SQL simples baseado em palavras-chave

## Custos

- **GPT-3.5-turbo**: ~$0.0015 por 1K tokens (muito barato)
- **Uso típico**: ~100-500 tokens por pergunta
- **Custo estimado**: ~$0.0001-0.0005 por pergunta

A OpenAI oferece créditos gratuitos para novos usuários.

## Próximos Passos

Depois de configurar o LLM, você pode:

1. ✅ Testar perguntas complexas
2. ✅ Ver SQL gerado automaticamente
3. ✅ Integrar RAG (busca em documentos)
4. ✅ Melhorar respostas com contexto


