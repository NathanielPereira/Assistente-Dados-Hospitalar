from __future__ import annotations

import time
from typing import Callable


class ChatMetrics:
    def __init__(self) -> None:
        self._latencies: list[float] = []

    def record(self, started_at: float) -> None:
        self._latencies.append(time.perf_counter() - started_at)

    def p95_latency(self) -> float:
        if not self._latencies:
            return 0.0
        sorted_values = sorted(self._latencies)
        index = int(len(sorted_values) * 0.95) - 1
        return sorted_values[max(index, 0)]

chat_metrics = ChatMetrics()
