"""Rotas para gerenciamento de provedores de LLM."""

from fastapi import APIRouter
from src.services.llm_service import LLMService

router = APIRouter(prefix="/v1/llm", tags=["llm"])


@router.get("/providers")
async def get_providers_status():
    """Retorna status de todos os provedores de LLM configurados."""
    providers = LLMService.get_providers_status()
    return {
        "providers": providers,
        "total": len(providers),
        "available": sum(1 for p in providers if p["status"] == "available"),
    }

