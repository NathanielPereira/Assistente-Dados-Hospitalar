# ⚙️ Configuração do Vercel - Conectar ao Backend Render

## 🔴 Problema

O frontend está rodando no Vercel, mas não consegue conectar ao backend no Render porque a variável de ambiente `NEXT_PUBLIC_API_URL` não está configurada.

## ✅ Solução

### Passo 1: Pegar a URL do Backend no Render

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Vá em seu serviço `hospital-assistant-backend`
3. Copie a **URL** (algo como: `https://hospital-assistant-backend-xxxx.onrender.com`)
4. Teste se está funcionando: `https://hospital-assistant-backend-xxxx.onrender.com/health`

### Passo 2: Configurar Variável de Ambiente no Vercel

1. Acesse [Vercel Dashboard](https://vercel.com/dashboard)
2. Vá em seu projeto `Assistente-Dados-Hospitalar`
3. Clique em **"Settings"**
4. Vá em **"Environment Variables"**
5. Adicione:

**Key:**
```
NEXT_PUBLIC_API_URL
```

**Value:**
```
https://hospital-assistant-backend-xxxx.onrender.com
```
(Substitua `xxxx` pela URL real do seu backend no Render)

**Environments:** Marque todas (Production, Preview, Development)

6. Clique em **"Save"**

### Passo 3: Fazer Novo Deploy

1. No Vercel Dashboard, vá em **"Deployments"**
2. Clique nos **3 pontinhos** do último deployment
3. Clique em **"Redeploy"**
4. Ou faça um novo commit/push para trigger automático

## ✅ Verificação

Após o redeploy:

1. Acesse: https://assistente-dados-hospitalar.vercel.app/chat
2. O aviso de "Backend não está rodando" deve desaparecer
3. Teste fazer uma pergunta no chat

## 🔧 Troubleshooting

### Se ainda aparecer o aviso:

1. Verifique se a URL do backend está correta (teste no navegador)
2. Verifique se o backend está rodando no Render (veja os logs)
3. Verifique se a variável `NEXT_PUBLIC_API_URL` está configurada corretamente no Vercel
4. Verifique se fez redeploy após configurar a variável

### Erro de CORS:

Se aparecer erro de CORS, verifique se o backend no Render tem CORS configurado para aceitar requisições do Vercel. O código já está configurado, mas verifique os logs do Render.

## 📋 Checklist

- [ ] Backend rodando no Render ✅
- [ ] URL do backend copiada
- [ ] Variável `NEXT_PUBLIC_API_URL` configurada no Vercel
- [ ] Redeploy feito no Vercel
- [ ] Teste no chat funcionando

---

**🎉 Depois disso, seu projeto estará 100% funcional!**

