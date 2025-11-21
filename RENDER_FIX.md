# 🔧 Correção do Deploy no Render

## Problema Identificado

O Poetry 2.x não suporta mais a flag `--no-dev`. O erro era:
```
The option "--no-dev" does not exist
```

## ✅ Solução Aplicada

Atualizei todos os arquivos para usar `--without dev` em vez de `--no-dev`:

1. ✅ `render.yaml` - Atualizado
2. ✅ `QUICK_DEPLOY.md` - Atualizado  
3. ✅ `DEPLOY_FREE.md` - Atualizado
4. ✅ `apps/backend-fastapi/Dockerfile` - Atualizado

## 📋 Configuração Correta no Render

### Build Command:
```bash
cd apps/backend-fastapi && pip install poetry && poetry install --without dev
```

### Start Command:
```bash
cd apps/backend-fastapi && poetry run uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

### Variáveis de Ambiente:
```
DATABASE_URL=postgresql://neondb_owner:npg_15HewNKxEdgB@ep-gentle-morning-aci29uzb-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
OPENAI_API_KEY=sua-chave-openai
ENVIRONMENT=production
PORT=8000
```

## 🚀 Próximos Passos

1. **No Render Dashboard**, vá em seu serviço
2. Clique em **"Manual Deploy"** > **"Deploy latest commit"**
3. Ou aguarde o deploy automático (já foi feito push da correção)

O deploy deve funcionar agora! ✅

