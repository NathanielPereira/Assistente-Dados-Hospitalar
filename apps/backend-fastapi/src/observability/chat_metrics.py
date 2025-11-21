from __future__ import annotations

import time
from typing import Dict

from src.observability.metrics import chat_metrics


class ChatMetricsCollector:
    """Coleta métricas específicas do chat para observabilidade."""

    def __init__(self):
        self.session_count = 0
        self.error_count = 0
        self.streaming_sessions: Dict[str, float] = {}

    def record_session_start(self, session_id: str) -> None:
        self.session_count += 1
        self.streaming_sessions[session_id] = time.perf_counter()

    def record_session_end(self, session_id: str, success: bool) -> None:
        if session_id in self.streaming_sessions:
            duration = time.perf_counter() - self.streaming_sessions[session_id]
            chat_metrics.record(self.streaming_sessions[session_id])
            del self.streaming_sessions[session_id]
            if not success:
                self.error_count += 1

    def get_stats(self) -> dict:
        return {
            "total_sessions": self.session_count,
            "errors": self.error_count,
            "p95_latency": chat_metrics.p95_latency(),
        }


chat_metrics_collector = ChatMetricsCollector()
