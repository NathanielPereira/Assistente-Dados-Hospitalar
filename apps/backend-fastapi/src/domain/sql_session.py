from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from src.observability.audit_logger import AuditLogger


class SQLExecutionStatus(Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


@dataclass
class SQLSession:
    """Representa uma sessão de execução SQL com aprovação."""

    session_id: UUID = field(default_factory=uuid4)
    user_id: str = ""
    original_prompt: str = ""
    suggested_sql: str = ""
    approved_sql: Optional[str] = None
    status: SQLExecutionStatus = SQLExecutionStatus.PENDING_APPROVAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    result_hash: Optional[str] = None
    audit_entry_id: Optional[UUID] = None

    def approve(self, sql: str) -> None:
        """Aprova SQL para execução."""
        self.approved_sql = sql
        self.status = SQLExecutionStatus.APPROVED

    def mark_executed(self, result_hash: str, audit_entry_id: UUID) -> None:
        """Marca como executado e registra auditoria."""
        self.status = SQLExecutionStatus.EXECUTED
        self.executed_at = datetime.utcnow()
        self.result_hash = result_hash
        self.audit_entry_id = audit_entry_id


class SQLSessionRepository:
    """Repositório para persistir SQLSession."""

    def __init__(self, db_conn, audit_logger: AuditLogger):
        self.db = db_conn
        self.audit_logger = audit_logger

    async def save(self, session: SQLSession) -> None:
        """Salva sessão e registra AuditEntry."""
        # TODO: INSERT no NeonDB
        # Registrar auditoria
        await self.audit_logger.log_execution(
            session_id=str(session.session_id),
            user_id=session.user_id,
            sql_executed=session.approved_sql or session.suggested_sql,
            result_hash=session.result_hash or "",
        )
