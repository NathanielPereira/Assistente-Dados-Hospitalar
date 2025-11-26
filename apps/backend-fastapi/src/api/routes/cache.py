"""Rotas para gerenciamento de cache."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID

from src.services.cache_service import get_cache_service
from src.services.question_matcher import QuestionMatcher
from src.domain.cache_entry import CacheEntry

router = APIRouter(prefix="/v1/cache", tags=["cache"])


class MatchRequest(BaseModel):
    question: str


class MatchResponse(BaseModel):
    found: bool
    entry_id: str | None = None
    confidence: float | None = None
    question: str | None = None


class CreateEntryRequest(BaseModel):
    question: str
    sql: str
    response_template: str
    variations: list[str] | None = None
    keywords: list[str] | None = None
    requires_realtime: bool = False


class CreateEntryResponse(BaseModel):
    entry_id: str
    question: str
    status: str


@router.post("/match", response_model=MatchResponse)
async def match_question(req: MatchRequest):
    """Busca correspondência de pergunta no cache."""
    cache_service = get_cache_service()
    cache_entries = cache_service.get_all_entries()
    
    if not cache_entries:
        return MatchResponse(found=False)
    
    result = QuestionMatcher.match(req.question, cache_entries)
    
    if result:
        entry, confidence = result
        return MatchResponse(
            found=True,
            entry_id=str(entry.entry_id),
            confidence=confidence,
            question=entry.question,
        )
    
    return MatchResponse(found=False)


@router.post("/entries", response_model=CreateEntryResponse, status_code=201)
async def create_cache_entry(req: CreateEntryRequest):
    """Adiciona uma nova entrada ao cache manualmente."""
    try:
        cache_service = get_cache_service()
        
        # Cria CacheEntry
        entry = CacheEntry(
            question=req.question,
            sql=req.sql,
            response_template=req.response_template,
            variations=req.variations or [],
            keywords=req.keywords or [],
            requires_realtime=req.requires_realtime,
        )
        
        # Adiciona ao cache
        cache_service.add_entry(entry)
        
        return CreateEntryResponse(
            entry_id=str(entry.entry_id),
            question=entry.question,
            status="created"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar entrada no cache: {str(e)}")


@router.get("/stats")
async def get_cache_stats():
    """Retorna estatísticas do cache."""
    cache_service = get_cache_service()
    stats = cache_service.get_stats()
    
    # Calcula cache hit rate (seria necessário rastrear hits/misses)
    # Por enquanto retorna 0.0
    return {
        **stats,
        "cache_hit_rate": 0.0,
    }


@router.get("/entries")
async def list_cache_entries():
    """Lista todas as entradas do cache."""
    cache_service = get_cache_service()
    entries = cache_service.get_all_entries()
    
    return {
        "entries": [
            {
                "entry_id": str(e.entry_id),
                "question": e.question,
                "usage_count": e.usage_count,
                "confidence": e.confidence,
                "validated": e.validated,
                "last_used": e.last_used.isoformat() if e.last_used else None,
            }
            for e in entries
        ],
        "total": len(entries),
    }


@router.get("/entries/{entry_id}")
async def get_cache_entry(entry_id: UUID):
    """Retorna detalhes de uma entrada específica."""
    cache_service = get_cache_service()
    entry = cache_service.get_entry(entry_id)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")
    
    return {
        "entry_id": str(entry.entry_id),
        "question": entry.question,
        "variations": entry.variations,
        "keywords": entry.keywords,
        "sql": entry.sql,
        "response_template": entry.response_template,
        "requires_realtime": entry.requires_realtime,
        "created_at": entry.created_at.isoformat(),
        "last_used": entry.last_used.isoformat() if entry.last_used else None,
        "usage_count": entry.usage_count,
        "confidence": entry.confidence,
        "validated": entry.validated,
        "validation_metadata": entry.validation_metadata,
        "provider_used": entry.provider_used,
    }


@router.delete("/entries/{entry_id}")
async def delete_cache_entry(entry_id: UUID):
    """Remove uma entrada do cache."""
    cache_service = get_cache_service()
    entry = cache_service.get_entry(entry_id)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")
    
    cache_service.delete_entry(entry_id)
    return {"message": "Entrada removida com sucesso"}
