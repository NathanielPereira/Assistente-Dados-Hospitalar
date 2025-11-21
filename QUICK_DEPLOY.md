# 🚀 Deploy Rápido - Passo a Passo

## 📦 Passo 1: Publicar no GitHub ✅

O código já foi publicado! Repositório: `NathanielPereira/Assistente-Dados-Hospitalar`

---

## 🆓 Passo 2: Deploy Gratuito (Vercel + Render)

### 2.1 Backend no Render (5 minutos)

1. **Acesse**: https://dashboard.render.com
2. **Crie conta** (use GitHub para login rápido)
3. **"New +"** > **"Web Service"**
4. **Conecte repositório**: `NathanielPereira/Assistente-Dados-Hospitalar`
5. **Configure**:
   ```
   Name: hospital-assistant-backend
   Region: Oregon (US West) ou mais próxima
   Branch: main
   Root Directory: apps/backend-fastapi
   Runtime: Python 3
   Build Command: cd apps/backend-fastapi && pip install poetry && poetry install --without dev
   Start Command: poetry run uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
   ```
6. **Environment Variables**:
   ```
   DATABASE_URL=sua-url-neondb
   OPENAI_API_KEY=sua-chave-openai
   ENVIRONMENT=production
   PORT=8000
   ```
7. **"Create Web Service"**
8. **Aguarde** ~5-10 minutos para build
9. **Copie a URL**: `https://hospital-assistant-backend-xxxx.onrender.com`

### 2.2 Frontend no Vercel (3 minutos)

1. **Acesse**: https://vercel.com
2. **Crie conta** (use GitHub para login rápido)
3. **"Add New..."** > **"Project"**
4. **Importe**: `NathanielPereira/Assistente-Dados-Hospitalar`
5. **Configure**:
   ```
   Framework Preset: Next.js (auto-detectado)
   Root Directory: apps/frontend-next
   ```
6. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://hospital-assistant-backend-xxxx.onrender.com
   ```
   (Use a URL do Render que você copiou)
7. **"Deploy"**
8. **Aguarde** ~2-3 minutos
9. **Sua app está no ar!** 🎉

---

## 🗄️ Passo 3: Configurar NeonDB (se ainda não tem)

1. **Acesse**: https://neon.tech
2. **Crie conta gratuita**
3. **"Create Project"**
4. **Copie Connection String**
5. **Cole no Render** (variável `DATABASE_URL`)

---

## ✅ Verificação

### Teste Backend:
```bash
curl https://hospital-assistant-backend-xxxx.onrender.com/health
```

### Teste Frontend:
- Acesse a URL do Vercel
- Teste o chat
- Deve funcionar! 🚀

---

## 🔄 Atualizações Automáticas

Agora, sempre que você fizer push no GitHub:

```bash
git add .
git commit -m "Sua mensagem"
git push origin main
```

O **Vercel** e **Render** fazem deploy automático! ✨

---

## ⚠️ Importante: Render "Dorme"

O Render gratuito "dorme" após 15 minutos de inatividade.

**Solução**: Use [UptimeRobot](https://uptimerobot.com) (gratuito):
1. Crie conta
2. Adicione monitor HTTP
3. URL: `https://hospital-assistant-backend-xxxx.onrender.com/health`
4. Intervalo: 5 minutos
5. Isso mantém o serviço "acordado"!

---

## 📊 Próximo: Migrar para AWS

Depois que estiver funcionando, podemos migrar para AWS para:
- ✅ Sem downtime
- ✅ Melhor performance  
- ✅ Escalabilidade
- ✅ Mais recursos

Mas primeiro, vamos garantir que está funcionando no plano gratuito! 🎯

