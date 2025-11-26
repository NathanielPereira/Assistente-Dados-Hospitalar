"""Modelo de domínio para resultado de validação."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class ValidationStatus(str, Enum):
    """Status da validação."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


class ValidationResult(BaseModel):
    """Representa o resultado da validação de uma resposta gerada."""

    validation_id: UUID = Field(default_factory=uuid4, description="Identificador único da validação")
    entry_id: UUID = Field(..., description="Referência à CacheEntry validada")
    status: ValidationStatus = Field(..., description="Status da validação")
    sql_valid: bool = Field(False, description="Se SQL é válido")
    sql_error: Optional[str] = Field(None, description="Erro de SQL se houver")
    results_not_empty: bool = Field(False, description="Se resultados não estão vazios quando esperado")
    response_format_valid: bool = Field(False, description="Se formato da resposta está correto")
    response_errors: Optional[list[str]] = Field(None, description="Erros encontrados na resposta")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Score de confiança calculado")
    validated_at: datetime = Field(default_factory=datetime.utcnow, description="Quando foi validada")
    validator_version: str = Field("1.0", description="Versão do validador usado")

    @field_validator("status", mode="before")
    @classmethod
    def validate_status_consistency(cls, v: ValidationStatus, values) -> ValidationStatus:
        """Valida que status é consistente com flags booleanas."""
        # Validação será feita após todos os campos serem definidos
        return v

    @field_validator("status", mode="after")
    @classmethod
    def ensure_status_consistency(cls, v: ValidationStatus, info) -> ValidationStatus:
        """Garante consistência entre status e flags após validação."""
        sql_valid = info.data.get("sql_valid", False)
        results_not_empty = info.data.get("results_not_empty", False)
        response_format_valid = info.data.get("response_format_valid", False)

        # Se todos os checks passaram, status deve ser PASSED
        if sql_valid and results_not_empty and response_format_valid:
            if v != ValidationStatus.PASSED:
                return ValidationStatus.PASSED
        # Se algum check falhou, status deve ser FAILED ou WARNING
        elif not sql_valid or not response_format_valid:
            if v not in (ValidationStatus.FAILED, ValidationStatus.WARNING):
                return ValidationStatus.FAILED
        # Se apenas results_not_empty falhou, pode ser WARNING
        elif not results_not_empty:
            if v not in (ValidationStatus.FAILED, ValidationStatus.WARNING):
                return ValidationStatus.WARNING

        return v

    def calculate_confidence(self) -> float:
        """Calcula score de confiança baseado nos resultados de validação."""
        score = 0.0
        if self.sql_valid:
            score += 0.4
        if self.results_not_empty:
            score += 0.3
        if self.response_format_valid:
            score += 0.3
        self.confidence_score = score
        return score

    def is_valid(self) -> bool:
        """Verifica se a validação passou completamente."""
        return (
            self.status == ValidationStatus.PASSED
            and self.sql_valid
            and self.results_not_empty
            and self.response_format_valid
        )

    class Config:
        """Configuração do modelo."""

        use_enum_values = True
        json_schema_extra = {
            "example": {
                "validation_id": "123e4567-e89b-12d3-a456-426614174000",
                "entry_id": "123e4567-e89b-12d3-a456-426614174001",
                "status": "passed",
                "sql_valid": True,
                "results_not_empty": True,
                "response_format_valid": True,
                "confidence_score": 1.0,
                "validated_at": "2025-01-21T10:00:00Z",
                "validator_version": "1.0",
            }
        }

