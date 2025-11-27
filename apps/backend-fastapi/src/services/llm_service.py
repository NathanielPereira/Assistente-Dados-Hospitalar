"""Serviço para inicializar e gerenciar LLM com suporte multi-provider e fallback."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, date
from typing import Optional

# Importa bibliotecas LangChain de forma independente
# Se pelo menos langchain-core estiver disponível, consideramos LangChain disponível
try:
    from langchain_core.language_models import BaseLanguageModel
    LANGCHAIN_AVAILABLE = True
except ImportError:
    BaseLanguageModel = object
    LANGCHAIN_AVAILABLE = False

# Importa provedores específicos (opcionais)
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_huggingface import HuggingFaceEndpoint
except ImportError:
    HuggingFaceEndpoint = None

from src.config import settings
from src.domain.llm_provider import LLMProvider, ProviderType, ProviderStatus

# Tenta importar métricas, mas não falha se não existir
try:
    from src.observability.metrics import llm_metrics
except ImportError:
    # Cria um objeto mock se métricas não estiverem disponíveis
    class MockMetrics:
        def record_usage(self, provider_id, latency): pass
        def record_failure(self, provider_id): pass
        def record_circuit_breaker_open(self, provider_id): pass
    llm_metrics = MockMetrics()

logger = logging.getLogger(__name__)


class LLMService:
    """Serviço para gerenciar múltiplos provedores de LLM com fallback automático."""

    _providers: dict[str, LLMProvider] = {}
    _llm_instances: dict[str, BaseLanguageModel] = {}
    _current_provider_index: int = 0
    _health_check_task: Optional[asyncio.Task] = None
    _initialized: bool = False
    _usage_tracking: dict[str, dict] = {}  # Rastreia uso diário/mensal por provedor

    @classmethod
    def _initialize_providers(cls) -> None:
        """Inicializa provedores configurados a partir das variáveis de ambiente."""
        if cls._initialized:
            return

        # Verifica se LangChain está disponível
        if not LANGCHAIN_AVAILABLE:
            logger.warning("Bibliotecas LangChain não estão instaladas. LLM não estará disponível.")
            cls._initialized = True
            cls._providers = {}  # Garante que está vazio
            return

        priority_list = settings.LLM_PROVIDER_PRIORITY.split(",")
        priority_list = [p.strip().lower() for p in priority_list]

        priority = 1
        missing_keys = []
        
        for provider_name in priority_list:
            provider_id = provider_name.lower()

            # Google Gemini
            if provider_id == "google":
                if not settings.GOOGLE_API_KEY:
                    missing_keys.append("GOOGLE_API_KEY")
                    logger.warning("⚠️ Google Gemini não configurado: GOOGLE_API_KEY não encontrada")
                    continue
                provider = LLMProvider(
                    provider_id="google",
                    provider_type=ProviderType.GOOGLE,
                    api_key=settings.GOOGLE_API_KEY,
                    priority=priority,
                    enabled=True,
                )
                llm = cls._create_llm_instance(provider)
                if llm:
                    cls._llm_instances["google"] = llm
                    provider.mark_available()
                else:
                    provider.mark_unavailable()
                cls._providers["google"] = provider
                priority += 1

            # Anthropic Claude
            elif provider_id == "anthropic":
                if not settings.ANTHROPIC_API_KEY:
                    missing_keys.append("ANTHROPIC_API_KEY")
                    logger.warning("⚠️ Anthropic Claude não configurado: ANTHROPIC_API_KEY não encontrada")
                    continue
                provider = LLMProvider(
                    provider_id="anthropic",
                    provider_type=ProviderType.ANTHROPIC,
                    api_key=settings.ANTHROPIC_API_KEY,
                    priority=priority,
                    enabled=True,
                )
                llm = cls._create_llm_instance(provider)
                if llm:
                    cls._llm_instances["anthropic"] = llm
                    provider.mark_available()
                else:
                    provider.mark_unavailable()
                cls._providers["anthropic"] = provider
                priority += 1

            # Hugging Face
            elif provider_id == "huggingface":
                if not settings.HUGGINGFACE_API_KEY:
                    missing_keys.append("HUGGINGFACE_API_KEY")
                    logger.warning("⚠️ Hugging Face não configurado: HUGGINGFACE_API_KEY não encontrada")
                    continue
                provider = LLMProvider(
                    provider_id="huggingface",
                    provider_type=ProviderType.HUGGINGFACE,
                    api_key=settings.HUGGINGFACE_API_KEY,
                    priority=priority,
                    enabled=True,
                )
                llm = cls._create_llm_instance(provider)
                if llm:
                    cls._llm_instances["huggingface"] = llm
                    provider.mark_available()
                else:
                    provider.mark_unavailable()
                cls._providers["huggingface"] = provider
                priority += 1

            # OpenRouter
            elif provider_id == "openrouter":
                if not settings.OPENROUTER_API_KEY:
                    missing_keys.append("OPENROUTER_API_KEY")
                    logger.warning("⚠️ OpenRouter não configurado: OPENROUTER_API_KEY não encontrada")
                    continue
                provider = LLMProvider(
                    provider_id="openrouter",
                    provider_type=ProviderType.OPENROUTER,
                    api_key=settings.OPENROUTER_API_KEY,
                    priority=priority,
                    enabled=True,
                )
                llm = cls._create_llm_instance(provider)
                if llm:
                    cls._llm_instances["openrouter"] = llm
                    provider.mark_available()
                else:
                    provider.mark_unavailable()
                cls._providers["openrouter"] = provider
                priority += 1

            # OpenAI (fallback)
            elif provider_id == "openai":
                if not settings.OPENAI_API_KEY:
                    missing_keys.append("OPENAI_API_KEY")
                    logger.warning("⚠️ OpenAI não configurado: OPENAI_API_KEY não encontrada")
                    continue
                provider = LLMProvider(
                    provider_id="openai",
                    provider_type=ProviderType.OPENAI,
                    api_key=settings.OPENAI_API_KEY,
                    priority=priority,
                    enabled=True,
                )
                llm = cls._create_llm_instance(provider)
                if llm:
                    cls._llm_instances["openai"] = llm
                    provider.mark_available()
                else:
                    provider.mark_unavailable()
                cls._providers["openai"] = provider
                priority += 1

        cls._initialized = True
        available_count = sum(1 for p in cls._providers.values() if p.is_available())
        logger.info(f"Inicializados {len(cls._providers)} provedores de LLM ({available_count} disponíveis)")
        
        if missing_keys:
            logger.warning(f"⚠️ Provedores não configurados (faltam API keys): {', '.join(missing_keys)}")
            logger.warning(f"💡 Configure as variáveis de ambiente no Render para habilitar fallback automático")
        
        if available_count == 0:
            logger.error("❌ Nenhum provedor LLM disponível! Configure pelo menos uma API key.")
        elif available_count == 1:
            logger.warning("⚠️ Apenas 1 provedor LLM configurado. Configure mais provedores para fallback automático.")

    @classmethod
    def _create_llm_instance(cls, provider: LLMProvider) -> Optional[BaseLanguageModel]:
        """Cria instância LangChain para o provedor especificado com timeout configurado."""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        # Timeout padrão de 4 segundos por requisição
        timeout_seconds = settings.LLM_REQUEST_TIMEOUT
        max_retries = settings.LLM_MAX_RETRIES
            
        try:
            if provider.provider_type == ProviderType.GOOGLE and ChatGoogleGenerativeAI:
                # Google Gemini: usar modelo padrão ou gemini-1.0-pro (mais compatível)
                # Se não especificar model, usa o padrão da biblioteca
                return ChatGoogleGenerativeAI(
                    model=None,  # Usa modelo padrão da biblioteca (geralmente gemini-pro ou gemini-1.0-pro)
                    temperature=0,
                    google_api_key=provider.api_key,
                    timeout=timeout_seconds,
                    max_retries=max_retries,
                )
            elif provider.provider_type == ProviderType.ANTHROPIC and ChatAnthropic:
                # Modelos Claude disponíveis: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
                # Usando claude-3-5-sonnet-20241022 (mais recente) ou fallback para haiku (mais barato)
                return ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",  # Modelo mais recente e poderoso
                    temperature=0,
                    anthropic_api_key=provider.api_key,
                    timeout=timeout_seconds,
                    max_retries=max_retries,
                )
            elif provider.provider_type == ProviderType.HUGGINGFACE:
                # OPÇÃO 1: Usar ChatHuggingFace (suporta tool calling em modelos compatíveis)
                # Requer: pip install langchain-huggingface
                try:
                    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
                    
                    # Modelos recomendados que suportam tool calling:
                    # - "meta-llama/Meta-Llama-3-8B-Instruct"
                    # - "mistralai/Mistral-7B-Instruct-v0.2"
                    # - "HuggingFaceH4/zephyr-7b-beta"
                    
                    llm_endpoint = HuggingFaceEndpoint(
                        repo_id="meta-llama/Meta-Llama-3-8B-Instruct",  # Modelo que suporta tool calling
                        task="text-generation",
                        huggingfacehub_api_token=provider.api_key,
                        max_new_tokens=512,
                        temperature=0.1,
                        timeout=timeout_seconds,
                    )
                    
                    # Wrapper ChatHuggingFace adiciona suporte a tool calling
                    return ChatHuggingFace(llm=llm_endpoint)
                    
                except ImportError:
                    logger.warning("ChatHuggingFace não disponível. Instale: pip install langchain-huggingface")
                    return None
                except Exception as e:
                    logger.warning(f"Erro ao criar HuggingFace provider: {e}")
                    return None
            elif provider.provider_type == ProviderType.OPENROUTER and ChatOpenAI:
                # OpenRouter usa OpenAI client com endpoint customizado
                # Modelos OpenRouter: openai/gpt-3.5-turbo, anthropic/claude-3-haiku, etc.
                # Usando meta-llama/llama-3.2-3b-instruct como alternativa gratuita
                return ChatOpenAI(
                    model="meta-llama/llama-3.2-3b-instruct:free",  # Modelo gratuito no OpenRouter
                    temperature=0,
                    openai_api_key=provider.api_key,
                    openai_api_base="https://openrouter.ai/api/v1",
                    timeout=timeout_seconds,
                    max_retries=max_retries,
                )
            elif provider.provider_type == ProviderType.OPENAI and ChatOpenAI:
                # Modelos OpenAI: gpt-4o, gpt-4-turbo, gpt-4, gpt-3.5-turbo
                # Usando gpt-3.5-turbo como padrão (mais barato e estável)
                return ChatOpenAI(
                    model="gpt-3.5-turbo",  # Modelo estável e econômico
                    temperature=0,
                    openai_api_key=provider.api_key,
                    timeout=timeout_seconds,
                    max_retries=max_retries,
                )
        except Exception as e:
            logger.warning(f"Erro ao criar instância LLM para {provider.provider_id}: {e}")
            return None

        return None

    @classmethod
    def _handle_provider_error(cls, provider_id: str, error: Exception) -> None:
        """Trata erro de provedor e atualiza estado."""
        if provider_id not in cls._providers:
            return

        provider = cls._providers[provider_id]

        # Detecta tipo de erro
        error_str = str(error).lower()
        if "429" in error_str or "rate limit" in error_str or "quota" in error_str or "insufficient_quota" in error_str:
            provider.mark_rate_limited()
            logger.warning(f"⚠️ Provedor {provider_id} atingiu limite de quota/rate limit")
        elif "404" in error_str or "not found" in error_str or "does not exist" in error_str or "not supported" in error_str:
            provider.mark_error()
            logger.error(f"❌ Provedor {provider_id} com erro de modelo não encontrado (404): {error}")
        elif "401" in error_str or "403" in error_str:
            provider.mark_error()
            logger.error(f"❌ Provedor {provider_id} com erro de autenticação/autorização")
        else:
            provider.mark_unavailable()
            logger.warning(f"⚠️ Provedor {provider_id} indisponível: {error}")

        # Abre circuit breaker se necessário
        if provider.consecutive_failures >= 3:
            provider.open_circuit_breaker()
            llm_metrics.record_circuit_breaker_open(provider_id)
            logger.error(f"🔴 Circuit breaker aberto para {provider_id} após {provider.consecutive_failures} falhas")

        llm_metrics.record_failure(provider_id)
        logger.warning(
            f"Provedor {provider_id} falhou: {error}. "
            f"Falhas consecutivas: {provider.consecutive_failures}"
        )

    @classmethod
    async def _health_check_providers(cls) -> None:
        """Executa health check periódico em todos os provedores."""
        while True:
            try:
                await asyncio.sleep(30)  # Health check a cada 30 segundos

                for provider_id, provider in cls._providers.items():
                    if not provider.enabled:
                        continue

                    # Fecha circuit breaker se passou tempo suficiente
                    if provider.circuit_breaker_open:
                        provider.close_circuit_breaker()

                    # Testa provedor tentando criar/validar instância
                    try:
                        llm = cls._llm_instances.get(provider_id)
                        if not llm:
                            # Tenta criar instância se não existir
                            llm = cls._create_llm_instance(provider)
                            if llm:
                                cls._llm_instances[provider_id] = llm
                                provider.mark_available()
                            else:
                                provider.mark_unavailable()
                        else:
                            # Instância existe, marca como disponível
                            # Health check real seria muito custoso, então apenas
                            # verificamos se instância existe e circuit breaker está fechado
                            if not provider.circuit_breaker_open:
                                provider.mark_available()
                            logger.debug(f"Health check OK para {provider_id}")
                    except Exception as e:
                        cls._handle_provider_error(provider_id, e)

            except Exception as e:
                logger.error(f"Erro no health check: {e}")

    @classmethod
    def _rotate_providers(cls) -> str:
        """Rotaciona entre provedores habilitados conforme estratégia configurada."""
        strategy = settings.LLM_ROTATION_STRATEGY.lower()

        available_providers = [
            (p.provider_id, p)
            for p in sorted(cls._providers.values(), key=lambda x: x.priority)
            if p.is_available()
        ]

        if not available_providers:
            return None

        if strategy == "round_robin":
            cls._current_provider_index = (
                cls._current_provider_index + 1
            ) % len(available_providers)
            return available_providers[cls._current_provider_index][0]
        elif strategy == "priority":
            return available_providers[0][0]  # Sempre usa o de maior prioridade
        elif strategy == "least_used":
            # TODO: Implementar rastreamento de uso
            return available_providers[0][0]
        else:
            return available_providers[0][0]

    @classmethod
    def get_llm(cls) -> Optional[BaseLanguageModel]:
        """Retorna instância do LLM disponível ou None se nenhum estiver disponível.
        
        Tenta todos os provedores disponíveis em ordem de prioridade antes de retornar None.
        """
        import time
        start_time = time.perf_counter()
        
        cls._initialize_providers()

        if not cls._providers:
            logger.warning("Nenhum provedor de LLM configurado")
            return None

        # Lista de provedores para tentar (por prioridade)
        providers_to_try = sorted(cls._providers.values(), key=lambda x: x.priority)
        
        # Tenta obter LLM por rotação ou prioridade primeiro
        provider_id = cls._rotate_providers()
        if provider_id:
            providers_to_try = [p for p in providers_to_try if p.provider_id == provider_id] + \
                              [p for p in providers_to_try if p.provider_id != provider_id]
        
        # Tenta cada provedor até encontrar um que funcione
        for provider in providers_to_try:
            if not provider.enabled:
                continue
                
            # Se circuit breaker está aberto, pula este provedor
            if provider.circuit_breaker_open:
                logger.debug(f"Provedor {provider.provider_id} com circuit breaker aberto, pulando...")
                continue
            
            provider_id = provider.provider_id
            
            # Tenta obter ou criar instância
            if provider_id not in cls._llm_instances:
                llm = cls._create_llm_instance(provider)
                if llm:
                    cls._llm_instances[provider_id] = llm
                    provider.mark_available()
                    logger.info(f"Instância LLM criada para {provider_id}")
                else:
                    logger.warning(f"Falha ao criar instância LLM para {provider_id}")
                    provider.mark_unavailable()
                    continue
            
            # Verifica se instância existe e está válida
            llm_instance = cls._llm_instances.get(provider_id)
            if llm_instance:
                # Registra métricas de uso
                latency = time.perf_counter() - start_time
                llm_metrics.record_usage(provider_id, latency)
                cls._track_usage(provider_id)
                provider.mark_available()
                logger.debug(f"Usando provedor LLM: {provider_id}")
                return llm_instance
            else:
                logger.warning(f"Instância LLM não encontrada para {provider_id}")
                provider.mark_unavailable()

        # Se chegou aqui, nenhum provedor funcionou
        logger.error("Nenhum provedor de LLM disponível após tentar todos os provedores configurados")
        return None

    @classmethod
    def get_llm_with_fallback(cls, failed_provider_id: Optional[str] = None) -> Optional[BaseLanguageModel]:
        """Retorna instância do LLM disponível, tentando todos os provedores em caso de falha.
        
        Se um provedor falhar (ex: 429 rate limit), tenta os outros automaticamente.
        """
        if failed_provider_id:
            # Marca o provedor que falhou como rate limited ou unavailable
            if failed_provider_id in cls._providers:
                provider = cls._providers[failed_provider_id]
                error_str = str(failed_provider_id).lower()
                if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
                    provider.mark_rate_limited()
                    logger.warning(f"Provedor {failed_provider_id} marcado como rate limited, tentando outros...")
                else:
                    provider.mark_unavailable()
                    logger.warning(f"Provedor {failed_provider_id} marcado como unavailable, tentando outros...")
        
        # Tenta todos os provedores disponíveis (exceto o que falhou)
        providers_to_try = sorted(cls._providers.values(), key=lambda x: x.priority)
        
        for provider in providers_to_try:
            if not provider.enabled:
                continue
            
            # Pula o provedor que falhou
            if failed_provider_id and provider.provider_id == failed_provider_id:
                continue
                
            # Se circuit breaker está aberto, pula este provedor
            if provider.circuit_breaker_open:
                logger.debug(f"Provedor {provider.provider_id} com circuit breaker aberto, pulando...")
                continue
            
            provider_id = provider.provider_id
            
            # Tenta obter ou criar instância
            if provider_id not in cls._llm_instances:
                llm = cls._create_llm_instance(provider)
                if llm:
                    cls._llm_instances[provider_id] = llm
                    provider.mark_available()
                    logger.info(f"✅ Instância LLM criada para {provider_id} (fallback)")
                else:
                    logger.warning(f"Falha ao criar instância LLM para {provider_id}")
                    provider.mark_unavailable()
                    continue
            
            # Verifica se instância existe e está válida
            llm_instance = cls._llm_instances.get(provider_id)
            if llm_instance:
                provider.mark_available()
                logger.info(f"✅ Usando provedor LLM (fallback): {provider_id}")
                return llm_instance

        # Se chegou aqui, nenhum provedor funcionou
        logger.error("❌ Nenhum provedor de LLM disponível após fallback")
        return None

    @classmethod
    def is_available(cls) -> bool:
        """Verifica se pelo menos um LLM está disponível."""
        cls._initialize_providers()
        return any(p.is_available() for p in cls._providers.values())

    @classmethod
    async def start_health_check(cls) -> None:
        """Inicia task de health check periódico."""
        # Não inicia health check se não há provedores ou LangChain não está disponível
        if not LANGCHAIN_AVAILABLE or not cls._providers:
            return
            
        if cls._health_check_task is None or cls._health_check_task.done():
            cls._health_check_task = asyncio.create_task(cls._health_check_providers())
            logger.info("Health check de provedores iniciado")

    @classmethod
    async def stop_health_check(cls) -> None:
        """Para task de health check."""
        if cls._health_check_task and not cls._health_check_task.done():
            cls._health_check_task.cancel()
            try:
                await cls._health_check_task
            except asyncio.CancelledError:
                pass
            logger.info("Health check de provedores parado")
        # Se não há task ou já está feito, não precisa fazer nada

    @classmethod
    def _track_usage(cls, provider_id: str) -> None:
        """Rastreia uso de um provedor para monitoramento de limites."""
        today = date.today().isoformat()
        
        if provider_id not in cls._usage_tracking:
            cls._usage_tracking[provider_id] = {}
        
        if today not in cls._usage_tracking[provider_id]:
            cls._usage_tracking[provider_id][today] = 0
        
        cls._usage_tracking[provider_id][today] += 1

    @classmethod
    def get_usage_stats(cls, provider_id: str) -> dict:
        """Retorna estatísticas de uso de um provedor."""
        if provider_id not in cls._usage_tracking:
            return {"daily": 0, "monthly": 0}
        
        today = date.today().isoformat()
        daily = cls._usage_tracking[provider_id].get(today, 0)
        
        # Calcula uso mensal (últimos 30 dias)
        monthly = sum(
            count for date_str, count in cls._usage_tracking[provider_id].items()
            if (datetime.fromisoformat(date_str) - datetime.now()).days <= 30
        )
        
        return {"daily": daily, "monthly": monthly}

    @classmethod
    def get_providers_status(cls) -> list[dict]:
        """Retorna status de todos os provedores."""
        cls._initialize_providers()
        return [
            {
                "provider_id": p.provider_id,
                "provider_type": p.provider_type.value if hasattr(p.provider_type, 'value') else str(p.provider_type),
                "priority": p.priority,
                "enabled": p.enabled,
                "status": p.status.value if hasattr(p.status, 'value') else str(p.status),
                "consecutive_failures": p.consecutive_failures,
                "circuit_breaker_open": p.circuit_breaker_open,
                "last_health_check": (
                    p.last_health_check.isoformat() if p.last_health_check else None
                ),
                "usage": cls.get_usage_stats(p.provider_id),
            }
            for p in sorted(cls._providers.values(), key=lambda x: x.priority)
        ]

