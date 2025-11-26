"""Configuração da aplicação usando variáveis de ambiente."""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()


class Settings:
    """Configurações da aplicação."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost/dbname"
    )

    # LLM Providers
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    
    # LLM Provider Configuration
    LLM_PROVIDER_PRIORITY: str = os.getenv("LLM_PROVIDER_PRIORITY", "openai,google,huggingface,openrouter")
    LLM_ROTATION_STRATEGY: str = os.getenv("LLM_ROTATION_STRATEGY", "round_robin")

    # S3
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "sa-east-1")
    S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME")

    # Redis
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

    # Smart Detection Configuration (Feature 003)
    ENABLE_SMART_DETECTION: bool = os.getenv("ENABLE_SMART_DETECTION", "true").lower() in ("true", "1", "yes")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.70"))
    SCHEMA_CACHE_TTL_SECONDS: int = int(os.getenv("SCHEMA_CACHE_TTL_SECONDS", "3600"))  # 1 hour default
    SYNONYMS_FILE_PATH: str = os.getenv("SYNONYMS_FILE_PATH", "config/synonyms.json")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    @property
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção."""
        return self.ENVIRONMENT == "production"


# Instância global de configurações
settings = Settings()
