from __future__ import annotations

from typing import Any, AsyncIterator

# LangChain 1.0 - imports atualizados
try:
    from langchain_community.agent_toolkits import create_sql_agent
    from langchain_core.language_models import BaseLanguageModel
except ImportError:
    # Fallback se não estiver disponível
    create_sql_agent = None
    BaseLanguageModel = Any

from src.connectors.rag_document_store import RAGDocumentStore
from src.domain.query_session import QuerySession


class ChatPipeline:
    """Pipeline LangChain combinando SQLAgent + RAG de documentos."""

    def __init__(
        self,
        llm: BaseLanguageModel | Any,
        sql_agent: Any,
        rag_store: RAGDocumentStore,
    ):
        self.llm = llm
        self.sql_agent = sql_agent
        self.rag_store = rag_store

    async def stream_response(
        self, session: QuerySession, prompt: str
    ) -> AsyncIterator[str]:
        """Streama resposta combinando SQL e documentos RAG."""
        # 1. Busca documentos relevantes
        docs = await self.rag_store.retrieve(prompt, top_k=3)
        
        # 2. Executa SQLAgent
        sql_result = await self.sql_agent.arun(prompt)
        
        # 3. Combina resultados e streama
        combined = f"Baseado em {len(docs)} documentos e dados SQL: {sql_result}"
        for chunk in combined.split():
            yield chunk + " "
