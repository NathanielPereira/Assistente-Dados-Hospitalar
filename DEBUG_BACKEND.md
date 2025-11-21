# 🔍 Debug: Backend Não Conectando

## ✅ Checklist Rápido

### 1. Verificar Variável no Vercel

1. Acesse: https://vercel.com/dashboard
2. Clique no projeto: **Assistente-Dados-Hospitalar**
3. Vá em **Settings** > **Environment Variables**
4. Verifique se existe:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://assistente-dados-hospitalar.onrender.com`
   - ⚠️ **SEM `/` no final!**

### 2. Verificar Backend no Render

1. Acesse: https://assistente-dados-hospitalar.onrender.com/health
2. Deve retornar: `{"status":"healthy","database":"connected"}`
3. Se retornar isso, o backend está OK! ✅

### 3. Verificar Logs do Vercel

1. No Vercel Dashboard, vá em **Deployments**
2. Clique no último deploy
3. Clique em **"View Function Logs"**
4. Procure por mensagens como:
   - `[health] Tentando conectar em: ...`
   - `[chat/stream] NEXT_PUBLIC_API_URL: ...`

### 4. Fazer Redeploy

Se a variável foi adicionada agora:

1. Vá em **Deployments**
2. Clique nos **3 pontos** (⋯) do último deploy
3. Clique em **"Redeploy"**
4. Aguarde 2-3 minutos

## 🧪 Teste Manual

Abra o console do navegador (F12) e execute:

```javascript
fetch('/api/health').then(r => r.json()).then(console.log)
```

Isso vai mostrar:
- Se a variável está configurada
- Qual URL está tentando acessar
- Qual erro está acontecendo

## 🔧 Problemas Comuns

### Problema 1: Variável não configurada
**Sintoma**: Logs mostram `NEXT_PUBLIC_API_URL: NÃO CONFIGURADO`
**Solução**: Configure a variável no Vercel (passo 1 acima)

### Problema 2: URL errada
**Sintoma**: Erro de conexão ou timeout
**Solução**: Verifique se a URL está correta e sem `/` no final

### Problema 3: Backend dormindo
**Sintoma**: Timeout ou erro 503
**Solução**: Configure UptimeRobot para manter ativo (veja `KEEP_RENDER_ALIVE.md`)

### Problema 4: CORS
**Sintoma**: Erro de CORS no console
**Solução**: Verifique se o backend tem CORS configurado para `*.vercel.app`

## 📋 Próximos Passos

1. Configure a variável `NEXT_PUBLIC_API_URL` no Vercel
2. Faça redeploy
3. Aguarde 2-3 minutos
4. Teste novamente
5. Se ainda não funcionar, envie os logs do console do navegador (F12)

