"""Serviço para inicializar e gerenciar LLM."""

from __future__ import annotations

from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseLanguageModel

from src.config import settings


class LLMService:
    """Serviço para gerenciar instância do LLM."""
    
    _instance: Optional[ChatOpenAI] = None
    
    @classmethod
    def get_llm(cls) -> Optional[BaseLanguageModel]:
        """Retorna instância do LLM ou None se não configurado."""
        if cls._instance is None:
            if not settings.OPENAI_API_KEY:
                print("[!] OPENAI_API_KEY nao configurada. LLM nao disponivel.")
                return None

            try:
                cls._instance = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0,
                    openai_api_key=settings.OPENAI_API_KEY,
                )
                print("[OK] LLM inicializado (GPT-3.5-turbo)")
            except Exception as e:
                print(f"[!] Erro ao inicializar LLM: {e}")
                return None
        
        return cls._instance
    
    @classmethod
    def is_available(cls) -> bool:
        """Verifica se LLM está disponível."""
        return cls.get_llm() is not None


