# Guia de Setup e Instalação

## ✅ Frontend - CONCLUÍDO
- Dependências instaladas com npm
- Arquivos de configuração criados
- Pronto para rodar

## ⚠️ Backend - REQUER PYTHON

### Instalar Python 3.11+
1. Baixe de https://www.python.org/downloads/
2. Marque "Add Python to PATH" durante instalação
3. Reinicie o terminal

### Instalar Poetry
```powershell
pip install poetry
```

### Instalar Dependências do Backend
```powershell
cd apps\backend-fastapi
poetry install
```

## 🚀 Como Rodar o Projeto

### Terminal 1 - Backend (após instalar Python)
```powershell
cd apps\backend-fastapi
poetry run uvicorn src.api.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```powershell
cd apps\frontend-next
npm run dev
```

### Acessar
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📝 Variáveis de Ambiente

Os arquivos `.env` já foram criados com valores padrão.
Ajuste conforme necessário:
- `apps/backend-fastapi/.env`
- `apps/frontend-next/.env.local`


