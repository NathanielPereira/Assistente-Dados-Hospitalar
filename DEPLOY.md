# 🚀 Guia de Deploy

Este documento descreve como fazer deploy do projeto Assistente de Dados Hospitalar.

## 📋 Pré-requisitos

- Conta no [GitHub](https://github.com)
- Conta no [Vercel](https://vercel.com) (para frontend)
- Conta no [Render](https://render.com) (para backend)
- Conta no [NeonDB](https://neon.tech) (para banco de dados PostgreSQL)
- Chaves de API dos LLMs (OpenAI, Google Gemini, Anthropic Claude)

## 🔧 Configuração Inicial

### 1. Preparar o Repositório GitHub

```bash
# Clone o repositório
git clone https://github.com/NathanielPereira/Assistente-Dados-Hospitalar.git
cd Assistente-Dados-Hospitalar

# Verifique se todos os arquivos estão commitados
git status

# Faça push para o GitHub
git push origin main
```

### 2. Configurar Variáveis de Ambiente

#### Backend (Render)

⚠️ **IMPORTANTE**: Configure as variáveis de ambiente no painel do Render (Environment → Environment Variables), **não** no arquivo `.env` do código.

No painel do Render, configure as seguintes variáveis de ambiente:

```env
# Banco de Dados (OBRIGATÓRIO)
DATABASE_URL=postgresql://user:password@host/database

# Provedores LLM (Configure pelo menos 2 para fallback automático)
# Google Gemini (Recomendado - gratuito): https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=sua-chave-google

# OpenAI (Opcional): https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-sua-chave-openai

# OpenRouter (Opcional): https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-sua-chave-openrouter

# Hugging Face (Opcional): https://huggingface.co/settings/tokens
HUGGINGFACE_API_KEY=hf_sua-chave-huggingface

# Anthropic Claude (Opcional): https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-sua-chave-anthropic

# Configuração
ENVIRONMENT=production

# Prioridade dos Provedores (ordem de tentativa)
LLM_PROVIDER_PRIORITY=google,openai,openrouter,huggingface

# Estratégia de Rotação
LLM_ROTATION_STRATEGY=priority

# Smart Detection
ENABLE_SMART_DETECTION=true
CONFIDENCE_THRESHOLD=0.70
SIMILARITY_THRESHOLD=0.70
SCHEMA_CACHE_TTL_SECONDS=3600
```

📖 **Documentação completa**: Veja `apps/backend-fastapi/ENV_VARIABLES.md` para detalhes sobre cada variável.

✅ **Verificação**: Após o deploy, verifique os logs. Você deve ver:
- `[OK] LLM inicializado (X/X provedores disponíveis)` - onde X é o número de provedores configurados
- Se aparecer `⚠️ Apenas 1 provedor LLM configurado`, adicione mais API keys no Render

#### Frontend (Vercel)

No painel do Vercel, configure:

```env
NEXT_PUBLIC_API_URL=https://assistente-dados-hospitalar.onrender.com
```

## 🌐 Deploy do Backend (Render)

### Passo 1: Conectar Repositório

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em "New" → "Web Service"
3. Conecte seu repositório GitHub
4. Selecione o repositório `Assistente-Dados-Hospitalar`

### Passo 2: Configurar Serviço

- **Name**: `assistente-dados-hospitalar`
- **Region**: Escolha a região mais próxima (ex: `São Paulo` ou `US East`)
- **Branch**: `main`
- **Root Directory**: `apps/backend-fastapi`
- **Runtime**: `Python 3`
- **Build Command**: `poetry install && poetry run pip install -e .`
- **Start Command**: `poetry run uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

### Passo 3: Configurar Variáveis de Ambiente

Adicione todas as variáveis listadas na seção "Backend (Render)" acima.

### Passo 4: Deploy

1. Clique em "Create Web Service"
2. Aguarde o build e deploy (pode levar 5-10 minutos)
3. Anote a URL gerada (ex: `https://assistente-dados-hospitalar.onrender.com`)

### Passo 5: Verificar Deploy

```bash
# Teste o health check
curl https://assistente-dados-hospitalar.onrender.com/health

# Teste a documentação
# Abra no navegador: https://assistente-dados-hospitalar.onrender.com/docs
```

## 🎨 Deploy do Frontend (Vercel)

### Passo 1: Conectar Repositório

1. Acesse [Vercel Dashboard](https://vercel.com/dashboard)
2. Clique em "Add New..." → "Project"
3. Importe o repositório GitHub
4. Selecione o repositório `Assistente-Dados-Hospitalar`

### Passo 2: Configurar Projeto

- **Framework Preset**: Next.js
- **Root Directory**: `apps/frontend-next`
- **Build Command**: `npm run build` (ou deixe padrão)
- **Output Directory**: `.next` (ou deixe padrão)

### Passo 3: Configurar Variáveis de Ambiente

Adicione a variável:
- `NEXT_PUBLIC_API_URL`: URL do backend no Render

### Passo 4: Deploy

1. Clique em "Deploy"
2. Aguarde o build e deploy (geralmente 2-3 minutos)
3. Anote a URL gerada (ex: `https://assistente-dados-hospitalar.vercel.app`)

### Passo 5: Verificar Deploy

1. Acesse a URL do frontend
2. Teste as funcionalidades principais:
   - Chat
   - SQL Workbench
   - Compliance
   - Observability

## 🗄️ Configurar Banco de Dados (NeonDB)

### Passo 1: Criar Projeto

1. Acesse [NeonDB Dashboard](https://console.neon.tech)
2. Crie um novo projeto
3. Anote a connection string

### Passo 2: Executar Migrações

```bash
# Conecte ao banco via psql ou interface web do NeonDB
# Execute os scripts SQL em infra/scripts/schema_layers.sql
```

### Passo 3: Configurar Connection String

Adicione a connection string do NeonDB na variável `DATABASE_URL` do Render.

## ✅ Verificação Pós-Deploy

### Checklist

- [ ] Backend responde em `/health`
- [ ] Documentação da API acessível em `/docs`
- [ ] Frontend carrega corretamente
- [ ] Chat funciona e gera SQL
- [ ] SQL Workbench funciona
- [ ] Compliance mostra trilhas de auditoria
- [ ] Observability mostra métricas
- [ ] Smart Detection funciona (teste com pergunta não respondível)

### Testes Automatizados

```bash
# Teste do backend
curl https://assistente-dados-hospitalar.onrender.com/health

# Teste do frontend
curl https://assistente-dados-hospitalar.vercel.app
```

## 🔄 Deploy Contínuo

Ambos Vercel e Render fazem deploy automático a cada push para a branch `main`:

1. Faça alterações no código
2. Commit e push:
   ```bash
   git add .
   git commit -m "Descrição das mudanças"
   git push origin main
   ```
3. Aguarde o deploy automático (2-5 minutos)

## 🐛 Troubleshooting

### Backend não inicia

- Verifique os logs no Render Dashboard
- Confirme que todas as variáveis de ambiente estão configuradas
- Verifique se o `DATABASE_URL` está correto

### Frontend não conecta ao backend

- Verifique se `NEXT_PUBLIC_API_URL` está correto
- Verifique CORS no backend (já configurado por padrão)
- Verifique se o backend está online

### Erro de conexão com banco

- Verifique se o `DATABASE_URL` está correto
- Verifique se o NeonDB permite conexões externas
- Verifique firewall/security groups

## 📚 Recursos Adicionais

- [Documentação do Render](https://render.com/docs)
- [Documentação do Vercel](https://vercel.com/docs)
- [Documentação do NeonDB](https://neon.tech/docs)

---

**Última atualização**: 2024-11-26



