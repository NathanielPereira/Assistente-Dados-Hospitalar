# 🆓 Guia de Deploy Gratuito - Hospital Data Assistant

Este guia mostra como fazer deploy **100% gratuito** usando:
- **Frontend**: Vercel (gratuito)
- **Backend**: Render (gratuito)
- **Banco de Dados**: NeonDB (gratuito)

---

## 📋 Pré-requisitos

1. Conta no [GitHub](https://github.com)
2. Conta no [Vercel](https://vercel.com) (conecte com GitHub)
3. Conta no [Render](https://render.com) (conecte com GitHub)
4. Conta no [NeonDB](https://neon.tech) (gratuito)

---

## 🗄️ Passo 1: Configurar Banco de Dados (NeonDB)

1. Acesse [NeonDB](https://neon.tech)
2. Crie uma conta gratuita
3. Crie um novo projeto
4. Copie a **Connection String** (será usada depois)
   - Formato: `postgresql://user:password@host/database?sslmode=require`

---

## 🚀 Passo 2: Deploy do Backend (Render)

### 2.1 Criar Serviço no Render

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em **"New +"** > **"Web Service"**
3. Conecte seu repositório GitHub: `NathanielPereira/Assistente-Dados-Hospitalar`
4. Configure:
   - **Name**: `hospital-assistant-backend`
   - **Region**: Escolha mais próxima (ex: `Oregon (US West)`)
   - **Branch**: `main`
   - **Root Directory**: `apps/backend-fastapi` ⚠️ **IMPORTANTE**: Configure isso primeiro!
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install poetry && poetry install --without dev
     ```
     ⚠️ **NÃO inclua `cd apps/backend-fastapi`** - o Root Directory já faz isso!
   - **Start Command**: 
     ```bash
     poetry run uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
     ```

### 2.2 Configurar Variáveis de Ambiente

Na seção **"Environment Variables"**, adicione:

```
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
OPENAI_API_KEY=sk-sua-chave-openai
ENVIRONMENT=production
PORT=8000
```

### 2.3 Deploy

1. Clique em **"Create Web Service"**
2. Aguarde o build (pode levar 5-10 minutos)
3. Anote a URL gerada: `https://hospital-assistant-backend.onrender.com`

---

## 🌐 Passo 3: Deploy do Frontend (Vercel)

### 3.1 Conectar Repositório

1. Acesse [Vercel Dashboard](https://vercel.com/dashboard)
2. Clique em **"Add New..."** > **"Project"**
3. Importe o repositório: `NathanielPereira/Assistente-Dados-Hospitalar`

### 3.2 Configurar Projeto

1. **Framework Preset**: Next.js (detectado automaticamente)
2. **Root Directory**: `apps/frontend-next`
3. **Build Command**: `npm run build` (padrão)
4. **Output Directory**: `.next` (padrão)

### 3.3 Configurar Variáveis de Ambiente

Na seção **"Environment Variables"**, adicione:

```
NEXT_PUBLIC_API_URL=https://hospital-assistant-backend.onrender.com
```

### 3.4 Deploy

1. Clique em **"Deploy"**
2. Aguarde o build (2-3 minutos)
3. Sua aplicação estará disponível em: `https://seu-projeto.vercel.app`

---

## ✅ Passo 4: Verificar Deploy

### Backend
```bash
# Teste o health check
curl https://hospital-assistant-backend.onrender.com/health
```

### Frontend
- Acesse a URL do Vercel
- Teste o chat
- Verifique se está conectando com o backend

---

## 🔄 Passo 5: Atualizações Automáticas

Ambas as plataformas fazem **deploy automático** quando você faz push no GitHub:

```bash
git add .
git commit -m "Atualização"
git push origin main
```

O Vercel e Render detectam automaticamente e fazem novo deploy!

---

## 🐛 Troubleshooting

### Backend não inicia
- Verifique os logs no Render Dashboard
- Confirme que `DATABASE_URL` está correto
- Verifique se `OPENAI_API_KEY` está configurada

### Frontend não conecta ao backend
- Verifique `NEXT_PUBLIC_API_URL` no Vercel
- Confirme que o backend está rodando (teste a URL diretamente)
- Verifique CORS no backend (já configurado para `*.vercel.app`)

### Erro de CORS
O backend já está configurado para aceitar requisições do Vercel. Se ainda houver erro:
- Verifique `apps/backend-fastapi/src/api/main.py` - CORS deve incluir `*.vercel.app`

---

## 💰 Limites do Plano Gratuito

### Vercel (Frontend)
- ✅ Ilimitado para projetos pessoais
- ✅ 100GB bandwidth/mês
- ✅ Deploy automático

### Render (Backend)
- ⚠️ **15 minutos de inatividade** = serviço "dorme"
- ⚠️ Primeira requisição após dormir pode levar 30-60s para "acordar"
- ✅ 750 horas/mês grátis
- ✅ Deploy automático

**Dica**: Para evitar que o backend "durma", você pode usar um serviço como [UptimeRobot](https://uptimerobot.com) para fazer ping a cada 5 minutos.

---

## 📊 Monitoramento

### Render
- Logs em tempo real no Dashboard
- Métricas básicas de uso

### Vercel
- Analytics no Dashboard
- Logs de build e runtime

---

## 🎯 Próximos Passos

Depois que estiver funcionando no plano gratuito, podemos migrar para AWS para:
- ✅ Sem downtime (sem "dormir")
- ✅ Melhor performance
- ✅ Escalabilidade
- ✅ Mais recursos

---

**🎉 Parabéns! Seu projeto está no ar de graça!**

