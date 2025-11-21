# 🆓 Opções de Cloud Sempre Gratuitas

Comparação de serviços cloud com planos **sempre gratuitos** (não apenas free tier temporário).

---

## 🏆 Melhores Opções para Este Projeto

### 1. 🟢 Railway (Recomendado) ⭐

**Plano Gratuito:**
- ✅ **$5 créditos/mês** grátis (suficiente para projeto pequeno)
- ✅ Sem "dormir" (não desliga após inatividade)
- ✅ Deploy automático do GitHub
- ✅ SSL automático
- ✅ Suporta Docker e buildpacks
- ✅ Logs em tempo real

**Limites:**
- 500 horas/mês de uso
- $5 créditos/mês (renovam mensalmente)
- Backend + Frontend podem rodar com os créditos

**Custo Real:** $0/mês se uso < $5

**Como usar:**
1. Acesse: https://railway.app
2. Conecte GitHub
3. Deploy automático!

---

### 2. 🟢 Fly.io

**Plano Gratuito:**
- ✅ **3 VMs compartilhadas** grátis
- ✅ 3GB de storage
- ✅ 160GB de transferência/mês
- ✅ Sem "dormir"
- ✅ Deploy automático

**Limites:**
- 3 VMs compartilhadas (suficiente para backend + frontend)
- Storage limitado

**Custo Real:** $0/mês se dentro dos limites

**Como usar:**
1. Acesse: https://fly.io
2. Instale CLI: `iwr https://fly.io/install.ps1 -useb | iex`
3. `fly launch` no projeto

---

### 3. 🟡 Render (Atual - Mas Dorme)

**Plano Gratuito:**
- ✅ 750 horas/mês
- ⚠️ **Dorme após 15 minutos** de inatividade
- ⚠️ Primeira requisição após dormir leva 30-60s

**Solução:** Use UptimeRobot para manter ativo (gratuito)

**Custo Real:** $0/mês

---

### 4. 🟡 Vercel (Frontend) + Render (Backend)

**Vercel:**
- ✅ **Ilimitado** para projetos pessoais
- ✅ Deploy automático
- ✅ CDN global
- ✅ SSL automático

**Render:**
- ✅ Backend gratuito (com limitação de dormir)

**Custo Real:** $0/mês (sua configuração atual)

---

### 5. 🟢 Oracle Cloud (Sempre Free)

**Plano Gratuito:**
- ✅ **2 VMs sempre grátis** (AMD, 1GB RAM cada)
- ✅ 200GB storage
- ✅ 10TB transferência/mês
- ✅ **Nunca expira** (diferente do AWS free tier)

**Limites:**
- 2 VMs AMD (1GB RAM, 1 vCPU cada)
- Ou 4 VMs ARM (24GB RAM total)

**Custo Real:** $0/mês **PARA SEMPRE**

**Como usar:**
1. Acesse: https://www.oracle.com/cloud/free
2. Crie conta
3. Crie instâncias VM
4. Instale Docker e rode seus containers

---

### 6. 🟢 Google Cloud Run

**Plano Gratuito:**
- ✅ **2 milhões de requisições/mês** grátis
- ✅ 360,000 GB-segundos de CPU
- ✅ 180,000 GB-segundos de memória
- ✅ Sem "dormir" (mas pode escalar para zero)

**Limites:**
- Requisições limitadas
- CPU/Memória limitados

**Custo Real:** $0/mês se dentro dos limites

---

## 📊 Comparação Rápida

| Serviço | Sempre Grátis? | Dorme? | Deploy GitHub | Melhor Para |
|---------|----------------|--------|---------------|-------------|
| **Railway** | ✅ ($5/mês créditos) | ❌ Não | ✅ Sim | ⭐ Recomendado |
| **Fly.io** | ✅ (3 VMs) | ❌ Não | ✅ Sim | ⭐ Recomendado |
| **Oracle Cloud** | ✅ **PARA SEMPRE** | ❌ Não | ⚠️ Manual | VMs completas |
| **Render** | ✅ | ⚠️ Sim (15min) | ✅ Sim | Atual |
| **Vercel** | ✅ (frontend) | ❌ Não | ✅ Sim | Frontend |
| **Google Cloud Run** | ✅ (limites) | ⚠️ Escala zero | ✅ Sim | Serverless |

---

## 🎯 Recomendação para Seu Projeto

### Opção 1: Railway (Mais Fácil) ⭐

**Por quê:**
- ✅ Mais fácil de usar
- ✅ Deploy automático do GitHub
- ✅ Não dorme
- ✅ $5 créditos/mês (suficiente)
- ✅ Suporta Docker

**Como migrar:**
1. Acesse: https://railway.app
2. Conecte GitHub
3. Selecione repositório
4. Railway detecta automaticamente e faz deploy!

**Custo:** $0/mês (dentro dos $5 créditos)

---

### Opção 2: Fly.io (Mais Controle)

**Por quê:**
- ✅ Sempre grátis (3 VMs)
- ✅ Não dorme
- ✅ Mais controle sobre infraestrutura
- ✅ Deploy automático

**Como migrar:**
1. Instale CLI: `iwr https://fly.io/install.ps1 -useb | iex`
2. `fly auth login`
3. `fly launch` no projeto
4. Configure variáveis de ambiente

**Custo:** $0/mês

---

### Opção 3: Oracle Cloud (Mais Poderoso)

**Por quê:**
- ✅ **Sempre grátis PARA SEMPRE**
- ✅ 2 VMs completas
- ✅ Controle total
- ✅ Nunca expira

**Desvantagens:**
- ⚠️ Mais complexo (precisa configurar VMs manualmente)
- ⚠️ Não tem deploy automático do GitHub (precisa configurar)

**Como migrar:**
1. Crie conta: https://www.oracle.com/cloud/free
2. Crie 2 VMs (backend + frontend)
3. Instale Docker nas VMs
4. Configure deploy manual ou CI/CD

**Custo:** $0/mês **PARA SEMPRE**

---

## 🚀 Guia Rápido: Migrar para Railway

### Passo 1: Criar Conta

1. Acesse: https://railway.app
2. Clique em **"Start a New Project"**
3. Conecte com GitHub
4. Selecione: **"Deploy from GitHub repo"**

### Passo 2: Deploy Backend

1. Selecione repositório: `NathanielPereira/Assistente-Dados-Hospitalar`
2. Railway detecta automaticamente
3. Configure:
   - **Root Directory**: `apps/backend-fastapi`
   - **Build Command**: `pip install poetry && poetry install --without dev`
   - **Start Command**: `poetry run uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

### Passo 3: Variáveis de Ambiente

No Railway, adicione:
```
DATABASE_URL=postgresql://neondb_owner:npg_15HewNKxEdgB@ep-gentle-morning-aci29uzb-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
OPENAI_API_KEY=sua-chave-openai
ENVIRONMENT=production
PORT=8000
```

### Passo 4: Deploy Frontend

1. Crie novo serviço no mesmo projeto
2. Configure:
   - **Root Directory**: `apps/frontend-next`
   - Railway detecta Next.js automaticamente
3. Variáveis:
   ```
   NEXT_PUBLIC_API_URL=https://backend-url.railway.app
   ```

### Passo 5: Pronto!

Railway gera URLs automaticamente:
- Backend: `https://backend-xxxx.up.railway.app`
- Frontend: `https://frontend-xxxx.up.railway.app`

**Custo:** $0/mês (dentro dos $5 créditos grátis)

---

## 💡 Comparação: Railway vs Render vs AWS

| Recurso | Railway | Render | AWS |
|---------|---------|--------|-----|
| **Custo** | $0 ($5 créditos) | $0 | ~$50/mês |
| **Dorme?** | ❌ Não | ⚠️ Sim (15min) | ❌ Não |
| **Deploy** | ✅ Auto GitHub | ✅ Auto GitHub | ⚠️ Manual |
| **Facilidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Escalabilidade** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Sempre Grátis** | ✅ Sim | ✅ Sim | ❌ Não |

---

## 🎯 Minha Recomendação

Para seu projeto, recomendo **Railway**:

1. ✅ **Mais fácil** que AWS
2. ✅ **Não dorme** (diferente do Render)
3. ✅ **Deploy automático** do GitHub
4. ✅ **$5 créditos/mês** (suficiente para projeto pequeno)
5. ✅ **SSL automático**
6. ✅ **Logs em tempo real**

**Custo:** $0/mês (dentro dos créditos grátis)

---

## 📚 Próximos Passos

Quer que eu crie um guia detalhado para migrar para Railway? É mais fácil que AWS e resolve o problema do Render "dormir"! 🚀

