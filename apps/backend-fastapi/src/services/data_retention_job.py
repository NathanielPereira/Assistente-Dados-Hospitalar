from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import List

from src.domain.query_session import QuerySession, QuerySessionRepository
from src.observability.audit_logger import AuditLogger


class DataRetentionJob:
    """Job de retenção e anonimização contínua conforme LGPD/HIPAA."""

    def __init__(
        self,
        session_repo: QuerySessionRepository,
        audit_logger: AuditLogger,
        retention_days: int = 730  # 2 anos
    ):
        self.session_repo = session_repo
        self.audit_logger = audit_logger
        self.retention_days = retention_days

    async def run(self) -> dict:
        """Executa job de retenção."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        # TODO: buscar sessões antigas e aplicar anonimização
        anonymized_count = 0
        deleted_count = 0
        
        return {
            "anonymized": anonymized_count,
            "deleted": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }

    def anonymize_session(self, session: QuerySession) -> QuerySession:
        """Anonimiza dados sensíveis de uma sessão."""
        # Remove PII do prompt
        if any(token in session.prompt.lower() for token in ["cpf", "rg", "paciente"]):
            session.prompt = "[ANONIMIZADO]"
        return session

    async def schedule(self, interval_hours: int = 24) -> None:
        """Agenda execução periódica do job."""
        while True:
            await self.run()
            await asyncio.sleep(interval_hours * 3600)
