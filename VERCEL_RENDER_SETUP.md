# 🔧 Configuração Completa: Vercel + Render

## ✅ Passo 1: Configurar Variável de Ambiente no Vercel

O frontend precisa saber onde está o backend!

1. **Acesse**: https://vercel.com/dashboard
2. Vá no seu projeto: `Assistente-Dados-Hospitalar`
3. Clique em **"Settings"** > **"Environment Variables"**
4. Adicione:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://hospital-assistant-backend-xxxx.onrender.com
   ```
   ⚠️ **Substitua `xxxx` pela URL real do seu Render!**
5. Selecione **"Production"**, **"Preview"** e **"Development"**
6. Clique em **"Save"**
7. Vá em **"Deployments"** > Clique nos 3 pontos > **"Redeploy"**

## 🔄 Passo 2: Manter Render Ativo (Sem Dormir)

O Render gratuito "dorme" após 15 minutos. Use **UptimeRobot** para mantê-lo ativo:

### 2.1 Criar Conta no UptimeRobot

1. Acesse: https://uptimerobot.com
2. Clique em **"Sign Up"** (100% gratuito)
3. Crie sua conta

### 2.2 Adicionar Monitor

1. No Dashboard, clique em **"+ Add New Monitor"**
2. Configure:
   - **Monitor Type**: `HTTP(s)`
   - **Friendly Name**: `Hospital Assistant Backend`
   - **URL**: `https://hospital-assistant-backend-xxxx.onrender.com/health`
     (Use a URL real do seu Render + `/health`)
   - **Monitoring Interval**: `5 minutes` (máximo no plano gratuito)
   - **Alert Contacts**: Seu email (opcional, mas recomendado)
3. Clique em **"Create Monitor"**

### 2.3 Verificar

- ✅ O UptimeRobot vai fazer ping a cada 5 minutos
- ✅ Isso mantém o Render "acordado" 24/7
- ✅ **100% gratuito** e funciona perfeitamente!

## 📋 Checklist Completo

- [ ] Variável `NEXT_PUBLIC_API_URL` configurada no Vercel
- [ ] Redeploy do Vercel feito após configurar variável
- [ ] Conta criada no UptimeRobot
- [ ] Monitor configurado para pingar `/health` a cada 5 minutos
- [ ] Testado o frontend: https://assistente-dados-hospitalar.vercel.app/chat

## 🧪 Teste Final

1. Aguarde 1-2 minutos após configurar tudo
2. Acesse: https://assistente-dados-hospitalar.vercel.app/chat
3. Faça uma pergunta de teste (ex: "Qual a taxa de ocupação da UTI pediátrica?")
4. Deve funcionar! 🎉

## ⚠️ Importante

- O plano gratuito do Render tem limite de **750 horas/mês**
- Com UptimeRobot pingando a cada 5 minutos, você usa ~216 horas/mês
- Ainda sobra bastante para uso real! ✅

## 🐛 Troubleshooting

### Backend ainda não responde

1. Verifique se o Render está rodando:
   - Acesse: `https://hospital-assistant-backend-xxxx.onrender.com/health`
   - Deve retornar `{"status":"ok"}`

2. Verifique se a variável está correta no Vercel:
   - Deve ser `https://` (não `http://`)
   - Deve terminar sem `/` no final

3. Aguarde alguns minutos após configurar o UptimeRobot
   - O primeiro ping pode levar alguns minutos

### Frontend mostra erro

1. Verifique os logs do Vercel:
   - Vercel Dashboard > Deployments > Clique no deploy > "View Function Logs"

2. Verifique os logs do Render:
   - Render Dashboard > Seu serviço > "Logs"

---

**💡 Dica**: O UptimeRobot também envia alertas se o serviço cair, então você fica sabendo se houver problemas!

