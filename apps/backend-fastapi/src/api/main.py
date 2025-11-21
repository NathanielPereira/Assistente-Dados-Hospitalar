from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import chat, sql, compliance
from src.database import db
from src.services.llm_service import LLMService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação."""
    # Startup
    await db.connect()
    print("[OK] Banco de dados conectado")
    
    # Testa conexão
    try:
        result = await db.execute_one("SELECT version() as version")
        if result:
            print(f"[OK] PostgreSQL conectado: {result.get('version', '')[:50]}...")
    except Exception as e:
        print(f"[!] Erro ao testar conexao: {e}")
    
    # Inicializa LLM se disponível
    llm = LLMService.get_llm()
    if llm:
        print("[OK] LLM inicializado")
    else:
        print("[!] LLM nao disponivel (OPENAI_API_KEY nao configurada)")
        print("    O sistema funcionara com SQL simples sem LangChain")
    
    yield
    
    # Shutdown
    await db.disconnect()
    print("[OK] Banco de dados desconectado")


app = FastAPI(
    title="Assistente de Dados Hospitalar API",
    version="0.1.0",
    description="API para assistente de dados hospitalares com LangChain SQLAgent + RAG",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://*.vercel.app",  # Vercel deployments
        "https://assistente-dados-hospitalar.vercel.app",  # Seu domínio específico
        "https://assistente-dados-hospitalar-*.vercel.app",  # Preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(chat.router)
app.include_router(sql.router)
app.include_router(compliance.router)


@app.get("/")
async def root():
    return {"message": "Assistente de Dados Hospitalar API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check com status do banco de dados."""
    try:
        result = await db.execute_one("SELECT 1 as healthy")
        db_status = "connected" if result else "disconnected"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
    
    return {
        "status": "healthy",
        "database": db_status
    }
