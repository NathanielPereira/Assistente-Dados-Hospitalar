import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import chat, sql, compliance, llm, cache, schema
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
    from src.services.llm_service import LANGCHAIN_AVAILABLE
    
    if not LANGCHAIN_AVAILABLE:
        print("[!] LLM nao disponivel (bibliotecas LangChain nao estao instaladas)")
        print("    Instale as dependencias: poetry install")
        print("    O sistema funcionara com SQL simples sem LangChain")
    else:
        # Primeiro verifica se há provedores configurados
        LLMService._initialize_providers()
        if LLMService._providers:
            available_count = sum(1 for p in LLMService._providers.values() if p.is_available())
            llm_instance = LLMService.get_llm()
            if llm_instance:
                print(f"[OK] LLM inicializado ({available_count}/{len(LLMService._providers)} provedores disponíveis)")
                # Inicia health check periódico apenas se há provedores disponíveis
                await LLMService.start_health_check()
            else:
                if available_count == 0:
                    print(f"[!] LLM nao disponivel ({len(LLMService._providers)} provedores configurados mas nenhum disponível)")
                    print("    Verifique se as chaves de API são válidas e as bibliotecas estão corretamente instaladas")
                else:
                    print(f"[!] LLM nao disponivel no momento ({available_count}/{len(LLMService._providers)} provedores disponíveis)")
                print("    O sistema funcionara com SQL simples sem LangChain")
                # Inicia health check mesmo assim para tentar recuperar (só se há provedores)
                if LLMService._providers:
                    await LLMService.start_health_check()
        else:
            print("[!] LLM nao disponivel (nenhum provedor configurado)")
            print("    Configure pelo menos uma chave de API (OPENAI_API_KEY, GOOGLE_API_KEY, etc.)")
            print("    O sistema funcionara com SQL simples sem LangChain")
    
    try:
        yield
    except asyncio.CancelledError:
        # CancelledError é esperado quando o servidor é interrompido
        raise
    finally:
        # Shutdown: para health check e desconecta banco de dados
        try:
            await LLMService.stop_health_check()
        except (asyncio.CancelledError, Exception):
            # Ignora erros durante shutdown
            pass
        
        try:
            await db.disconnect()
            print("[OK] Banco de dados desconectado")
        except (asyncio.CancelledError, Exception):
            # Ignora erros durante shutdown
            pass


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
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(chat.router)
app.include_router(sql.router)
app.include_router(compliance.router)
app.include_router(llm.router)
app.include_router(cache.router)
app.include_router(schema.router)  # Feature 003: Smart Response Detection


@app.get("/")
async def root():
    return {"message": "Assistente de Dados Hospitalar API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check com status do banco de dados."""
    try:
        # Testa conexão com query simples e timeout curto
        result = await db.execute_one("SELECT 1 as healthy")
        db_status = "connected" if result else "disconnected"
    except Exception as e:
        error_msg = str(e)
        # Se for erro de conexão idle, tenta reconectar
        if "idle-in-transaction" in error_msg.lower() or "terminating connection" in error_msg.lower():
            try:
                await db.disconnect()
                await db.connect()
                result = await db.execute_one("SELECT 1 as healthy")
                db_status = "connected" if result else "disconnected"
            except:
                db_status = f"error: {error_msg[:100]}"
        else:
            db_status = f"error: {error_msg[:100]}"
    
    return {
        "status": "healthy",
        "database": db_status
    }
