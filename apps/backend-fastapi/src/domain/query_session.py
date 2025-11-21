from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class SessionStatus(Enum):
    CREATED = "CREATED"
    STREAMING = "STREAMING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class QuerySession:
    """Representa uma interação de chat e/ou execução SQL."""

    session_id: UUID = field(default_factory=uuid4)
    user_id: str = ""
    prompt: str = ""
    sql_executed: Optional[str] = None
    result_summary: Optional[str] = None
    status: SessionStatus = SessionStatus.CREATED
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    audit_entry_id: Optional[UUID] = None
    degraded_mode: bool = False

    def mark_completed(self) -> None:
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def mark_failed(self) -> None:
        self.status = SessionStatus.FAILED
        self.completed_at = datetime.utcnow()


class QuerySessionRepository:
    """Repositório para persistir QuerySession."""

    def __init__(self, db_conn):
        self.db = db_conn

    async def save(self, session: QuerySession) -> None:
        # TODO: implementar INSERT/UPDATE no NeonDB
        pass

    async def get(self, session_id: UUID) -> Optional[QuerySession]:
        # TODO: implementar SELECT
        pass
