from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class DocumentClassification(Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


@dataclass
class DocumentMetadata:
    """Metadados obrigatórios para DocumentCorpus."""

    doc_id: UUID = field(default_factory=uuid4)
    origin: str = ""  # Fonte do documento
    version: str = "1.0"
    classification: DocumentClassification = DocumentClassification.INTERNAL
    owner: str = ""  # Proprietário/equipe responsável
    created_at: datetime = field(default_factory=datetime.utcnow)
    s3_key: str = ""
    hash: str = ""


class DocumentCatalog:
    """Catálogo de documentos com políticas de acesso."""

    def __init__(self):
        self._documents: dict[UUID, DocumentMetadata] = {}

    def register(self, metadata: DocumentMetadata) -> None:
        """Registra documento no catálogo."""
        self._documents[metadata.doc_id] = metadata

    def get(self, doc_id: UUID) -> Optional[DocumentMetadata]:
        """Recupera metadados de um documento."""
        return self._documents.get(doc_id)

    def list_by_classification(self, classification: DocumentClassification) -> list[DocumentMetadata]:
        """Lista documentos por classificação de sigilo."""
        return [doc for doc in self._documents.values() if doc.classification == classification]
