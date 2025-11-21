from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AlertSeverity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    """Representa um alerta do sistema."""

    severity: AlertSeverity
    message: str
    component: str
    timestamp: datetime
    resolved: bool = False

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


class AlertManager:
    """Gerencia criação e envio de alertas."""

    def __init__(self):
        self._alerts: list[Alert] = []

    def create_alert(
        self,
        severity: AlertSeverity | str,
        message: str,
        component: str,
    ) -> Alert:
        """Cria um novo alerta."""
        if isinstance(severity, str):
            severity = AlertSeverity[severity.upper()]
        
        alert = Alert(
            severity=severity,
            message=message,
            component=component,
            timestamp=datetime.utcnow(),
        )
        self._alerts.append(alert)
        return alert

    def get_active_alerts(self) -> list[Alert]:
        """Retorna alertas não resolvidos."""
        return [a for a in self._alerts if not a.resolved]
