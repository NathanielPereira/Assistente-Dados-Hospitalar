from __future__ import annotations

from typing import Any, Dict, List

# LangChain 1.0 - imports atualizados
try:
    from langchain_core.language_models import BaseLanguageModel
except ImportError:
    BaseLanguageModel = Any


class SQLResultSummarizer:
    """Gera resumos textuais e insights de resultados SQL."""

    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm

    async def summarize(self, sql: str, results: List[Dict[str, Any]]) -> Dict[str, str]:
        """Gera resumo textual dos resultados."""
        if not results:
            return {
                "summary": "Nenhum resultado encontrado.",
                "insights": "A consulta não retornou dados."
            }
        
        # TODO: usar LLM para gerar resumo
        summary = f"Consulta retornou {len(results)} registros."
        insights = "Análise automática dos dados disponível."
        
        return {
            "summary": summary,
            "insights": insights,
            "key_metrics": self._extract_metrics(results)
        }

    def _extract_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrai métricas principais dos resultados."""
        if not results:
            return {}
        
        # Exemplo: calcular médias, totais, etc.
        return {
            "total_rows": len(results),
            "sample_size": min(10, len(results))
        }
