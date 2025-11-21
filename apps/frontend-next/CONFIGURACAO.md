# Configuração do Frontend

## ✅ O que foi configurado

### 1. Rotas de API no Next.js
Criamos rotas de API que fazem proxy para o backend, evitando erros quando o backend não está rodando:

- `/api/health` - Health check do backend
- `/api/v1/chat/sessions` - Criação de sessões de chat
- `/api/v1/chat/stream` - Streaming de respostas (SSE)
- `/api/v1/sql/assist` - Assistência SQL
- `/api/v1/sql/execute` - Execução SQL
- `/api/v1/audit/exports` - Exportação de auditoria
- `/api/v1/observability/health` - Status do sistema

### 2. Tratamento de Erros
- Quando o backend não está rodando, as rotas retornam respostas mock/empty
- Mensagens amigáveis são exibidas na UI
- Não gera mais erros no console do Next.js

### 3. Variáveis de Ambiente
O frontend usa `NEXT_PUBLIC_API_URL` (opcional, padrão: `http://localhost:8000`)

## 🚀 Como usar

### Frontend apenas (sem backend)
- O frontend funciona normalmente
- Mostra mensagens indicando que o backend não está rodando
- Permite navegar e ver todas as páginas

### Frontend + Backend
1. Inicie o backend:
   ```powershell
   cd apps\backend-fastapi
   poetry run uvicorn src.api.main:app --reload
   ```

2. O frontend detecta automaticamente quando o backend está online
3. Todas as funcionalidades ficam disponíveis

## 📝 Notas

- As rotas de API do Next.js fazem proxy para o backend
- Se o backend não estiver rodando, retornam respostas mock/empty
- Isso evita erros no console e permite desenvolvimento do frontend independentemente

