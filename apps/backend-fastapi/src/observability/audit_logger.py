from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


class AuditLogger:
    """Base logger responsável por gerar eventos imutáveis e gravá-los no storage local/S3."""

    def __init__(self, out_dir: Path) -> None:
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def _hash_payload(self, payload: dict) -> str:
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def emit(
        self,
        *,
        query_session_id: uuid.UUID,
        event_type: str,
        actor: str,
        payload: dict,
        legal_basis: str,
    ) -> Path:
        event = {
            "event_id": str(uuid.uuid4()),
            "query_session_id": str(query_session_id),
            "event_type": event_type,
            "actor": actor,
            "legal_basis": legal_basis,
            "payload": payload,
            "input_hash": self._hash_payload(payload.get("input", {})),
            "output_hash": self._hash_payload(payload.get("output", {})),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        path = self.out_dir / f"{event['event_id']}.json"
        path.write_text(json.dumps(event, indent=2), encoding="utf-8")
        return path

