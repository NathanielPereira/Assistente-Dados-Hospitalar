from __future__ import annotations

import csv
import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.domain.query_session import QuerySession
from src.observability.audit_logger import AuditLogger
from src.database import db


class AuditExporter:
    """Exporta trilhas de auditoria em CSV/JSON."""

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger

    async def export_session_csv(self, session_id: UUID) -> str:
        """Exporta sessão em formato CSV."""
        # TODO: buscar AuditEntry e QuerySession, formatar CSV
        rows = [
            ["session_id", "user_id", "prompt", "sql_executed", "timestamp"],
            [str(session_id), "user", "test", "SELECT 1", "2025-11-20T00:00:00Z"],
        ]
        output = []
        for row in rows:
            output.append(",".join(row))
        return "\n".join(output)

    async def export_session_json(
        self,
        session_id: Optional[UUID] = None,
        user_id: Optional[str] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Exporta auditoria em formato JSON a partir da tabela public.audit_entries."""
        # Filtro simples por período e usuário/sessão
        where_clauses = ["timestamp >= NOW() - INTERVAL '7 days'"]
        params: List[Any] = []

        if user_id:
            where_clauses.append("user_id = %s")
            params.append(user_id)
        if session_id:
            where_clauses.append("session_id = %s")
            params.append(str(session_id))

        where_sql = " AND ".join(where_clauses)

        query = f"""
        SELECT
            session_id,
            user_id,
            prompt,
            sql_executed,
            timestamp,
            legal_basis
        FROM public.audit_entries
        WHERE {where_sql}
        ORDER BY timestamp DESC
        LIMIT 200
        """

        try:
            rows = await db.execute_query(query, tuple(params))
            
            # Remove duplicatas baseado em (session_id, prompt, sql_executed, timestamp)
            # O execute_query já retorna lista de dicionários
            seen = set()
            unique_rows = []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                
                # Cria chave única para detectar duplicatas
                key = (
                    str(row.get("session_id", "")),
                    str(row.get("prompt", "")),
                    str(row.get("sql_executed", "")),
                    str(row.get("timestamp", "")),
                )
                
                if key not in seen:
                    seen.add(key)
                    unique_rows.append(row)
            
            rows = unique_rows
        except Exception as e:
            # Fallback: retorna lista vazia, mas sem quebrar painel
            print(f"Erro ao carregar audit_entries: {e}")
            import traceback
            traceback.print_exc()
            rows = []

        return {
            "session_id": str(session_id) if session_id else None,
            "audit_entries": rows,
        }
