from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class CircuitBreaker:
    """Circuit breaker para integrações externas."""

    name: str
    failure_threshold: int = 3
    timeout_seconds: int = 60
    _failures: int = 0
    _last_failure: Optional[datetime] = None
    _state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_failure(self) -> None:
        """Registra uma falha."""
        self._failures += 1
        self._last_failure = datetime.utcnow()
        if self._failures >= self.failure_threshold:
            self._state = "OPEN"

    def record_success(self) -> None:
        """Registra um sucesso."""
        self._failures = 0
        self._state = "CLOSED"

    def is_open(self) -> bool:
        """Verifica se breaker está aberto."""
        if self._state == "OPEN":
            # Verifica se timeout expirou
            if self._last_failure and (datetime.utcnow() - self._last_failure).seconds > self.timeout_seconds:
                self._state = "HALF_OPEN"
                return False
            return True
        return False

    def should_alert(self) -> bool:
        """Indica se deve gerar alerta."""
        return self.is_open()
