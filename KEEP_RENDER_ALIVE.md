# 🔄 Como Manter o Render Ativo (Sem Dormir)

O Render no plano gratuito "dorme" após **15 minutos de inatividade**. Quando isso acontece, a primeira requisição pode levar 30-60 segundos para "acordar" o serviço.

## ✅ Solução: UptimeRobot (Gratuito)

### Passo 1: Criar Conta no UptimeRobot

1. Acesse: https://uptimerobot.com
2. Clique em **"Sign Up"** (gratuito)
3. Crie sua conta

### Passo 2: Adicionar Monitor

1. No Dashboard, clique em **"+ Add New Monitor"**
2. Configure:
   - **Monitor Type**: `HTTP(s)`
   - **Friendly Name**: `Hospital Assistant Backend`
   - **URL**: `https://hospital-assistant-backend-xxxx.onrender.com/health`
     (Substitua `xxxx` pela URL real do seu Render)
   - **Monitoring Interval**: `5 minutes` (máximo no plano gratuito)
   - **Alert Contacts**: Seu email (opcional)
3. Clique em **"Create Monitor"**

### Passo 3: Verificar

- O UptimeRobot vai fazer ping a cada 5 minutos
- Isso mantém o Render "acordado" 24/7
- ✅ **100% gratuito** e funciona perfeitamente!

## 🔧 Alternativa: Render Cron Job (Avançado)

Se preferir usar o próprio Render, você pode criar um **Cron Job**:

1. No Render Dashboard, vá em **"New +"** > **"Cron Job"**
2. Configure:
   - **Schedule**: `*/5 * * * *` (a cada 5 minutos)
   - **Command**: `curl https://hospital-assistant-backend-xxxx.onrender.com/health`
3. Isso também mantém o serviço ativo

## ⚠️ Importante

- O plano gratuito do Render tem limite de **750 horas/mês**
- Com UptimeRobot pingando a cada 5 minutos, você usa ~216 horas/mês
- Ainda sobra bastante para uso real! ✅

## 🚀 Depois de Configurar

1. Aguarde alguns minutos após configurar o UptimeRobot
2. Teste o frontend novamente: https://assistente-dados-hospitalar.vercel.app/chat
3. O backend deve responder rapidamente!

---

**💡 Dica**: O UptimeRobot também envia alertas se o serviço cair, então você fica sabendo se houver problemas!

