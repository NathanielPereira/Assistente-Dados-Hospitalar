"""Modelo de domínio para provedor de LLM."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ProviderType(str, Enum):
    """Tipos de provedores de LLM suportados."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    OPENROUTER = "openrouter"


class ProviderStatus(str, Enum):
    """Status de disponibilidade do provedor."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


class LLMProvider(BaseModel):
    """Representa um provedor de LLM configurado no sistema."""

    provider_id: str = Field(..., description="Identificador único do provedor")
    provider_type: ProviderType = Field(..., description="Tipo do provedor")
    api_key: Optional[str] = Field(None, description="Chave de API (criptografada em repouso)")
    api_url: Optional[str] = Field(None, description="URL base da API (para provedores locais)")
    priority: int = Field(..., ge=1, description="Ordem de prioridade (1 = mais prioritário)")
    enabled: bool = Field(True, description="Se o provedor está habilitado")
    status: ProviderStatus = Field(
        ProviderStatus.AVAILABLE, description="Status atual do provedor"
    )
    last_health_check: Optional[datetime] = Field(
        None, description="Última verificação de saúde"
    )
    consecutive_failures: int = Field(
        0, ge=0, description="Número de falhas consecutivas"
    )
    circuit_breaker_open: bool = Field(
        False, description="Se o circuit breaker está aberto"
    )
    circuit_breaker_opened_at: Optional[datetime] = Field(
        None, description="Quando o circuit breaker foi aberto"
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: Optional[str], info) -> Optional[str]:
        """Valida que api_key está presente para provedores que requerem."""
        provider_type = info.data.get("provider_type")
        if provider_type in (ProviderType.OPENAI, ProviderType.ANTHROPIC, ProviderType.GOOGLE):
            if not v:
                raise ValueError(f"api_key é obrigatório para {provider_type}")
        return v

    @field_validator("api_url")
    @classmethod
    def validate_api_url(cls, v: Optional[str], info) -> Optional[str]:
        """Valida que api_url está presente para provedores locais se necessário."""
        # Por enquanto, nenhum provedor requer api_url obrigatório
        # Futuro: Ollama ou outros provedores locais
        return v

    def mark_available(self) -> None:
        """Marca o provedor como disponível."""
        self.status = ProviderStatus.AVAILABLE
        self.consecutive_failures = 0
        self.last_health_check = datetime.utcnow()

    def mark_unavailable(self) -> None:
        """Marca o provedor como indisponível."""
        self.status = ProviderStatus.UNAVAILABLE
        self.consecutive_failures += 1
        self.last_health_check = datetime.utcnow()

    def mark_rate_limited(self) -> None:
        """Marca o provedor como rate limited."""
        self.status = ProviderStatus.RATE_LIMITED
        self.last_health_check = datetime.utcnow()

    def mark_error(self) -> None:
        """Marca o provedor com erro crítico."""
        self.status = ProviderStatus.ERROR
        self.consecutive_failures += 1
        self.last_health_check = datetime.utcnow()

    def open_circuit_breaker(self) -> None:
        """Abre o circuit breaker após múltiplas falhas."""
        if self.consecutive_failures >= 3:
            self.circuit_breaker_open = True
            self.circuit_breaker_opened_at = datetime.utcnow()

    def close_circuit_breaker(self) -> None:
        """Fecha o circuit breaker após período de recuperação."""
        if self.circuit_breaker_opened_at:
            elapsed = (datetime.utcnow() - self.circuit_breaker_opened_at).total_seconds()
            if elapsed >= 300:  # 5 minutos
                self.circuit_breaker_open = False
                self.circuit_breaker_opened_at = None
                self.consecutive_failures = 0

    def is_available(self) -> bool:
        """Verifica se o provedor está disponível para uso."""
        return (
            self.enabled
            and not self.circuit_breaker_open
            and self.status == ProviderStatus.AVAILABLE
        )

    class Config:
        """Configuração do modelo."""

        use_enum_values = True
        json_schema_extra = {
            "example": {
                "provider_id": "google",
                "provider_type": "google",
                "priority": 1,
                "enabled": True,
                "status": "available",
                "consecutive_failures": 0,
                "circuit_breaker_open": False,
            }
        }
