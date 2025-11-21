from __future__ import annotations

from enum import Enum


class Role(Enum):
    CONSULTOR = "CONSULTOR"
    ANALISTA = "ANALISTA"
    COMPLIANCE = "COMPLIANCE"


class PrivacyGuard:
    """Middleware/POLICY: bloqueia prompts com PII e valida base legal."""

    def __init__(self, allowed_roles: set[Role]):
        self.allowed_roles = allowed_roles

    def validate(self, prompt: str, role: Role) -> None:
        if role not in self.allowed_roles:
            raise PermissionError("Role não autorizada para este recurso")
        if any(token in prompt.lower() for token in ("cpf", "rg", "paciente")):
            raise ValueError("Tentativa de identificar paciente detectada")
