"""Modelo de domínio para entrada de cache."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class CacheEntry(BaseModel):
    """Representa uma entrada no cache de perguntas e respostas conhecidas."""

    entry_id: UUID = Field(default_factory=uuid4, description="Identificador único da entrada")
    question: str = Field(..., min_length=1, description="Pergunta original")
    variations: list[str] = Field(default_factory=list, description="Variações conhecidas da pergunta")
    keywords: list[str] = Field(default_factory=list, description="Palavras-chave para correspondência rápida")
    sql: str = Field(..., min_length=1, description="SQL correspondente à pergunta")
    response_template: str = Field(..., description="Template de resposta (pode conter placeholders)")
    requires_realtime: bool = Field(False, description="Se a resposta requer dados em tempo real")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Quando a entrada foi criada")
    last_used: Optional[datetime] = Field(None, description="Última vez que foi usada")
    usage_count: int = Field(0, ge=0, description="Número de vezes que foi usada")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Nível de confiança (0.0 a 1.0)")
    validated: bool = Field(False, description="Se passou na validação")
    validation_metadata: Optional[dict[str, Any]] = Field(
        None, description="Metadados da validação (razões, erros, etc.)"
    )
    provider_used: Optional[str] = Field(None, description="Provedor de LLM usado para gerar esta entrada")

    @field_validator("variations", "keywords")
    @classmethod
    def validate_lists(cls, v: list[str]) -> list[str]:
        """Garante que listas não sejam None."""
        return v if v is not None else []

    def mark_validated(self, metadata: Optional[dict[str, Any]] = None) -> None:
        """Marca a entrada como validada."""
        self.validated = True
        self.validation_metadata = metadata or {}

    def mark_invalidated(self, reason: str) -> None:
        """Marca a entrada como inválida."""
        self.validated = False
        self.validation_metadata = {
            **(self.validation_metadata or {}),
            "invalidated_reason": reason,
            "invalidated_at": datetime.utcnow().isoformat(),
        }

    def increment_usage(self) -> None:
        """Incrementa contador de uso e atualiza timestamp."""
        self.usage_count += 1
        self.last_used = datetime.utcnow()

    def update_confidence(self, confidence: float) -> None:
        """Atualiza nível de confiança."""
        if 0.0 <= confidence <= 1.0:
            self.confidence = confidence
        else:
            raise ValueError("Confidence deve estar entre 0.0 e 1.0")

    class Config:
        """Configuração do modelo."""

        json_schema_extra = {
            "example": {
                "entry_id": "123e4567-e89b-12d3-a456-426614174000",
                "question": "Qual a taxa de ocupação da UTI pediátrica?",
                "variations": ["taxa ocupação UTI pediátrica", "ocupação UTI ped"],
                "keywords": ["taxa", "ocupação", "UTI", "pediátrica"],
                "sql": "SELECT COUNT(*) FROM leitos WHERE tipo = 'UTI' AND setor = 'Pediatria'",
                "response_template": "A taxa de ocupação da UTI pediátrica é {count} leitos.",
                "requires_realtime": True,
                "created_at": "2025-01-21T10:00:00Z",
                "usage_count": 5,
                "confidence": 0.95,
                "validated": True,
            }
        }

