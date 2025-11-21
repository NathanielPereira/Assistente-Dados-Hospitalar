# ⚙️ Configuração Correta no Render

## 🔴 Problema Comum

Se você configurou **Root Directory: `apps/backend-fastapi`**, o Render **já está dentro desse diretório** quando executa os comandos.

**❌ ERRADO:**
```bash
Build Command: cd apps/backend-fastapi && pip install poetry && poetry install --without dev
```
Isso causa erro: `bash: line 1: cd: apps/backend-fastapi: No such file or directory`

**✅ CORRETO:**
```bash
Build Command: pip install poetry && poetry install --without dev
```

## 📋 Configuração Completa no Render

### Settings do Serviço:

1. **Name**: `hospital-assistant-backend`
2. **Region**: Escolha mais próxima (ex: `Oregon (US West)`)
3. **Branch**: `main`
4. **Root Directory**: `apps/backend-fastapi` ⚠️ **Configure isso primeiro!**
5. **Runtime**: `Python 3`
6. **Build Command**: 
   ```bash
   pip install poetry && poetry install --without dev
   ```
   ⚠️ **SEM `cd apps/backend-fastapi`** - o Root Directory já faz isso!
7. **Start Command**: 
   ```bash
   poetry run uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
   ```

### Environment Variables:

```
DATABASE_URL=postgresql://neondb_owner:npg_15HewNKxEdgB@ep-gentle-morning-aci29uzb-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
OPENAI_API_KEY=sua-chave-openai-aqui
ENVIRONMENT=production
PORT=8000
```

### Health Check:

- **Path**: `/health`

## 🔄 Como Aplicar a Correção

1. No Render Dashboard, vá em seu serviço
2. Clique em **"Settings"**
3. Role até **"Build & Deploy"**
4. Atualize o **Build Command** para:
   ```bash
   pip install poetry && poetry install --without dev
   ```
5. Clique em **"Save Changes"**
6. Vá em **"Manual Deploy"** > **"Deploy latest commit"**

## ✅ Verificação

Após o deploy, verifique os logs. Você deve ver:
- ✅ Poetry instalado
- ✅ Dependências instaladas
- ✅ Servidor iniciando na porta 8000

Se ainda houver erro, envie os logs completos! 🚀

