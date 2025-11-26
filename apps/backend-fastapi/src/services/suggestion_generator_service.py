"""Service for generating smart responses and alternative question suggestions."""

from __future__ import annotations

import logging
from typing import List

from src.domain.schema_info import SchemaInfo
from src.domain.question_analysis import QuestionAnalysis, SmartResponse

logger = logging.getLogger(__name__)


# Priority tables for suggestions (from research.md clarifications)
PRIORITY_TABLES = ["leitos", "atendimentos", "especialidades", "ocupacao", "uti"]


class SuggestionGeneratorService:
    """
    Service for generating smart responses when questions cannot be answered.
    
    Provides clear explanations, available entities, and 3 alternative suggestions.
    """
    
    @classmethod
    def generate_smart_response(
        cls,
        analysis: QuestionAnalysis,
        schema: SchemaInfo,
        is_partial_match: bool = False
    ) -> SmartResponse:
        """
        Generate smart response for unanswerable question.
        
        Args:
            analysis: Question analysis result
            schema: Database schema
            is_partial_match: Whether some entities were found
            
        Returns:
            SmartResponse with explanation and suggestions
        """
        # Generate message based on what wasn't found
        message = cls._generate_message(analysis, is_partial_match)
        
        # Get all available entities from schema
        available_entities = schema.get_all_entities()
        
        # Generate 3 suggestions
        suggestions = cls.generate_suggestions(schema, user_intent=analysis.intent)
        
        return SmartResponse(
            can_answer=False,
            message=message,
            available_entities=available_entities,
            suggestions=suggestions,
            partial_match=is_partial_match,
            found_entities=analysis.entities_found_in_schema if is_partial_match else []
        )
    
    @classmethod
    def _generate_message(cls, analysis: QuestionAnalysis, is_partial_match: bool) -> str:
        """
        Generate explanation message.
        
        Args:
            analysis: Question analysis
            is_partial_match: Whether partial match occurred
            
        Returns:
            Explanation message in Portuguese
        """
        if is_partial_match:
            # Partial match: some found, others not
            not_found_str = "', '".join(analysis.entities_not_found)
            return (
                f"Mostrando resultados para dados disponíveis. "
                f"As informações sobre '{not_found_str}' não estão disponíveis no banco de dados."
            )
        else:
            # Complete miss: nothing found
            if len(analysis.entities_not_found) == 0:
                return "Não foi possível identificar informações específicas para essa pergunta no banco de dados atual."
            elif len(analysis.entities_not_found) == 1:
                entity = analysis.entities_not_found[0]
                return f"As informações sobre '{entity}' não estão disponíveis no banco de dados atual."
            else:
                entities_str = "', '".join(analysis.entities_not_found)
                return f"As informações sobre '{entities_str}' não estão disponíveis no banco de dados atual."
    
    @classmethod
    def generate_suggestions(
        cls,
        schema: SchemaInfo,
        user_intent: str = None,
        count: int = 3
    ) -> List[str]:
        """
        Generate alternative question suggestions.
        
        Uses templates from spec.md: Count, List, Status, Aggregation.
        Prioritizes important tables from research.md.
        
        Args:
            schema: Database schema
            user_intent: Original question intent (for relevance)
            count: Number of suggestions to generate (default 3)
            
        Returns:
            List of suggested questions
        """
        suggestions = []
        tables = schema.tables
        
        # Prioritize tables from PRIORITY_TABLES list
        priority_tables = [
            t for t in tables 
            if any(priority in t.name.lower() for priority in PRIORITY_TABLES)
        ]
        other_tables = [
            t for t in tables 
            if not any(priority in t.name.lower() for priority in PRIORITY_TABLES)
        ]
        
        # Combine: priority first
        ordered_tables = priority_tables + other_tables
        
        # Generate suggestions using different templates
        templates_used = []
        
        for table in ordered_tables:
            if len(suggestions) >= count:
                break
            
            table_name = table.name
            
            # Template 1: COUNT (if not used yet)
            if "count" not in templates_used and len(suggestions) < count:
                suggestions.append(f"Quantos registros de {table_name} existem?")
                templates_used.append("count")
            
            # Template 2: LIST (if not used yet)
            if "list" not in templates_used and len(suggestions) < count:
                if table.has_status_column():
                    suggestions.append(f"Mostrar todos os {table_name} e seus status")
                else:
                    suggestions.append(f"Listar informações sobre {table_name}")
                templates_used.append("list")
            
            # Template 3: STATUS (if table has status column and not used yet)
            if "status" not in templates_used and len(suggestions) < count:
                if table.has_status_column():
                    suggestions.append(f"Qual o status dos {table_name}?")
                    templates_used.append("status")
            
            # Template 4: AGGREGATE (if numeric columns and not used yet)
            if "aggregate" not in templates_used and len(suggestions) < count:
                numeric_cols = table.numeric_columns
                if numeric_cols:
                    col_name = numeric_cols[0]  # Use first numeric column
                    suggestions.append(f"Qual a média de {col_name} por {table_name}?")
                    templates_used.append("aggregate")
        
        # Ensure we have exactly 3 suggestions (pad with generic if needed)
        while len(suggestions) < count and len(suggestions) < len(ordered_tables):
            remaining_tables = [t for t in ordered_tables if t.name not in " ".join(suggestions)]
            if remaining_tables:
                table = remaining_tables[0]
                suggestions.append(f"Mostre informações sobre {table.name}")
            else:
                break
        
        # Return exactly `count` suggestions
        return suggestions[:count]

