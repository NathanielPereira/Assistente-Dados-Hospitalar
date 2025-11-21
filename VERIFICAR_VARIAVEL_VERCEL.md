# ✅ Verificar Variável de Ambiente no Vercel

## 🔍 Passo a Passo para Verificar

### 1. Acessar Vercel Dashboard

1. Acesse: https://vercel.com/dashboard
2. Clique no projeto: **Assistente-Dados-Hospitalar**

### 2. Verificar Variável de Ambiente

1. Clique em **"Settings"** (no topo)
2. No menu lateral, clique em **"Environment Variables"**
3. Procure por: `NEXT_PUBLIC_API_URL`

**Se NÃO existir:**
- Clique em **"+ Add New"**
- **Name**: `NEXT_PUBLIC_API_URL`
- **Value**: `https://assistente-dados-hospitalar.onrender.com`
- ⚠️ **SEM `/` no final!**
- Selecione: ✅ Production, ✅ Preview, ✅ Development
- Clique em **"Save"**

**Se JÁ existir:**
- Verifique se o **Value** está correto: `https://assistente-dados-hospitalar.onrender.com`
- ⚠️ **SEM `/` no final!**
- Se estiver errado, clique nos 3 pontos (⋯) > **"Edit"** > Corrija > **"Save"**

### 3. Fazer Redeploy OBRIGATÓRIO

⚠️ **IMPORTANTE**: Variáveis de ambiente só são aplicadas em NOVOS deploys!

1. Vá em **"Deployments"** (no topo)
2. Clique nos **3 pontos** (⋯) do último deploy
3. Clique em **"Redeploy"**
4. Aguarde 2-3 minutos para o build completar

### 4. Verificar se Funcionou

Após o redeploy:

1. Acesse: https://assistente-dados-hospitalar.vercel.app/chat
2. Abra o Console do Navegador (F12)
3. Procure por mensagens como:
   - `[health] Tentando conectar em: https://assistente-dados-hospitalar.onrender.com/health`
   - `[chat/stream] NEXT_PUBLIC_API_URL: https://assistente-dados-hospitalar.onrender.com`

Se aparecer `NEXT_PUBLIC_API_URL: NÃO CONFIGURADO` ou `http://localhost:8000`, a variável não está configurada corretamente!

## 🧪 Teste Rápido no Console

Abra o console do navegador (F12) e execute:

```javascript
fetch('/api/health').then(r => r.json()).then(console.log)
```

Deve retornar algo como:
```json
{
  "status": "online",
  "backendUrl": "https://assistente-dados-hospitalar.onrender.com",
  "backendData": {"status":"healthy","database":"connected"}
}
```

Se retornar `backendUrl: "http://localhost:8000"`, a variável não está configurada!

## 📋 Checklist Final

- [ ] Variável `NEXT_PUBLIC_API_URL` existe no Vercel
- [ ] Valor está correto: `https://assistente-dados-hospitalar.onrender.com` (sem `/`)
- [ ] Ambientes selecionados: Production, Preview, Development
- [ ] Redeploy feito após configurar/atualizar variável
- [ ] Aguardou 2-3 minutos após redeploy
- [ ] Testou no console do navegador (F12)
- [ ] Backend está respondendo em: https://assistente-dados-hospitalar.onrender.com/health

## ⚠️ Erro Comum

**Problema**: Variável configurada mas ainda não funciona

**Causa**: Variáveis de ambiente só são aplicadas em NOVOS deploys!

**Solução**: Faça um **Redeploy** após configurar a variável!

---

**💡 Dica**: Se ainda não funcionar após seguir todos os passos, envie:
1. Screenshot da página de Environment Variables do Vercel
2. O que aparece no console do navegador (F12)
3. Os logs do último deploy do Vercel

