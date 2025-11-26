from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable


class ChatMetrics:
    """Métricas de latência e performance do chat."""
    
    def __init__(self) -> None:
        self._latencies: list[float] = []
        self._total_requests: int = 0
        self._failed_requests: int = 0

    def record(self, started_at: float) -> None:
        """Registra latência de uma requisição bem-sucedida."""
        latency = time.perf_counter() - started_at
        self._latencies.append(latency)
        self._total_requests += 1

    def record_failure(self) -> None:
        """Registra uma requisição que falhou."""
        self._failed_requests += 1
        self._total_requests += 1

    def p95_latency(self) -> float:
        """Retorna latência do percentil 95."""
        if not self._latencies:
            return 0.0
        sorted_values = sorted(self._latencies)
        index = int(len(sorted_values) * 0.95) - 1
        return sorted_values[max(index, 0)]
    
    def avg_latency(self) -> float:
        """Retorna latência média."""
        if not self._latencies:
            return 0.0
        return sum(self._latencies) / len(self._latencies)
    
    def get_stats(self) -> dict:
        """Retorna estatísticas completas."""
        return {
            "total_requests": self._total_requests,
            "successful_requests": len(self._latencies),
            "failed_requests": self._failed_requests,
            "avg_latency_seconds": self.avg_latency(),
            "p95_latency_seconds": self.p95_latency(),
        }


class LLMMetrics:
    """Métricas de uso e performance de provedores de LLM."""

    def __init__(self) -> None:
        self._provider_usage: dict[str, int] = defaultdict(int)
        self._provider_failures: dict[str, int] = defaultdict(int)
        self._provider_latencies: dict[str, list[float]] = defaultdict(list)
        self._circuit_breaker_opens: dict[str, int] = defaultdict(int)

    def record_usage(self, provider_id: str, latency: float) -> None:
        """Registra uso bem-sucedido de um provedor."""
        self._provider_usage[provider_id] += 1
        self._provider_latencies[provider_id].append(latency)

    def record_failure(self, provider_id: str) -> None:
        """Registra falha de um provedor."""
        self._provider_failures[provider_id] += 1

    def record_circuit_breaker_open(self, provider_id: str) -> None:
        """Registra abertura de circuit breaker."""
        self._circuit_breaker_opens[provider_id] += 1

    def get_provider_stats(self, provider_id: str) -> dict:
        """Retorna estatísticas de um provedor."""
        total_requests = self._provider_usage[provider_id] + self._provider_failures[provider_id]
        failure_rate = (
            self._provider_failures[provider_id] / total_requests
            if total_requests > 0
            else 0.0
        )
        latencies = self._provider_latencies[provider_id]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        return {
            "total_requests": total_requests,
            "successful_requests": self._provider_usage[provider_id],
            "failed_requests": self._provider_failures[provider_id],
            "failure_rate": round(failure_rate, 4),
            "average_latency": round(avg_latency, 3),
            "circuit_breaker_opens": self._circuit_breaker_opens[provider_id],
        }

    def get_all_stats(self) -> dict[str, dict]:
        """Retorna estatísticas de todos os provedores."""
        all_providers = set(self._provider_usage.keys()) | set(self._provider_failures.keys())
        return {provider_id: self.get_provider_stats(provider_id) for provider_id in all_providers}


# Instâncias globais
chat_metrics = ChatMetrics()
llm_metrics = LLMMetrics()
