from __future__ import annotations

from typing import List

from src.domain.document_catalog import DocumentMetadata


class RAGDocumentStore:
    """Conector para documentos RAG armazenados em S3 com metadados."""

    def __init__(self, s3_bucket: str, catalog: Any):
        self.bucket = s3_bucket
        self.catalog = catalog

    async def retrieve(self, query: str, top_k: int = 3) -> List[DocumentMetadata]:
        """Recupera documentos relevantes para a query."""
        # TODO: implementar busca semântica/BM25 + filtro por sigilo
        return []

    async def get_citation(self, doc_id: str) -> str:
        """Retorna trecho citável do documento."""
        # TODO: buscar do S3 e retornar snippet
        return ""
