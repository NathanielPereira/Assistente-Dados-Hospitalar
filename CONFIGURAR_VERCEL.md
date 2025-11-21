# ⚙️ Configurar Variável de Ambiente no Vercel

## 🔴 Problema

O frontend está mostrando "Backend não está rodando" porque não sabe onde está o backend.

## ✅ Solução Rápida (2 minutos)

### Passo 1: Acessar Vercel Dashboard

1. Acesse: https://vercel.com/dashboard
2. Clique no projeto: **Assistente-Dados-Hospitalar**

### Passo 2: Configurar Variável de Ambiente

1. Clique em **"Settings"** (no topo)
2. No menu lateral, clique em **"Environment Variables"**
3. Clique em **"+ Add New"**
4. Preencha:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://assistente-dados-hospitalar.onrender.com`
   - ⚠️ **IMPORTANTE**: Sem `/` no final!
5. Selecione os ambientes:
   - ✅ **Production**
   - ✅ **Preview**  
   - ✅ **Development**
6. Clique em **"Save"**

### Passo 3: Fazer Redeploy

1. Vá em **"Deployments"** (no topo)
2. Clique nos **3 pontos** (⋯) do último deploy
3. Clique em **"Redeploy"**
4. Aguarde o build (2-3 minutos)

## ✅ Verificação

Após o redeploy:

1. Acesse: https://assistente-dados-hospitalar.vercel.app/chat
2. Deve funcionar agora! 🎉

## 🧪 Teste Rápido

Você pode testar se o backend está respondendo:

1. Acesse: https://assistente-dados-hospitalar.onrender.com/health
2. Deve retornar: `{"status":"healthy","database":"connected"}`

Se retornar isso, o backend está OK! ✅

## 📋 Checklist

- [ ] Variável `NEXT_PUBLIC_API_URL` criada no Vercel
- [ ] Valor: `https://assistente-dados-hospitalar.onrender.com` (sem `/` no final)
- [ ] Ambientes selecionados: Production, Preview, Development
- [ ] Redeploy feito
- [ ] Testado o frontend

---

**💡 Dica**: Se ainda não funcionar após 5 minutos, verifique os logs do Vercel em "Deployments" > "View Function Logs"

