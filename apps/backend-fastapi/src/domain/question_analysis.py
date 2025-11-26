"""Domain models for question analysis and smart response generation."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class QuestionIntent(str, Enum):
    """Detected intent of the user's question."""
    COUNT = "count"                # "Quantos X existem?"
    LIST = "list"                  # "Quais X estão cadastrados?"
    AGGREGATE = "aggregate"        # "Qual a média de X?"
    FILTER = "filter"              # "Mostre X onde Y"
    STATUS = "status"              # "Qual o estado de X?"
    COMPARISON = "comparison"      # "Compare X com Y"
    UNKNOWN = "unknown"            # Cannot determine intent


class QuestionAnalysis(BaseModel):
    """Result of analyzing a user question."""
    
    question: str = Field(
        description="Original question text from user"
    )
    entities_mentioned: List[str] = Field(
        description="Entities (nouns) extracted from question after stop word removal"
    )
    entities_found_in_schema: List[str] = Field(
        description="Entities that exist in database schema (exact or close match)"
    )
    entities_not_found: List[str] = Field(
        description="Entities that do NOT exist in database schema"
    )
    confidence_score: float = Field(
        description="Confidence that question can be answered (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    intent: QuestionIntent = Field(
        default=QuestionIntent.UNKNOWN,
        description="Detected intent of the question"
    )
    can_answer: bool = Field(
        description="Whether system believes it can answer this question"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Explanation if question cannot be answered"
    )
    similar_entities: Dict[str, float] = Field(
        default_factory=dict,
        description="Near-match entities with similarity scores (0.0 to 1.0)"
    )
    synonym_mappings: Dict[str, str] = Field(
        default_factory=dict,
        description="Synonyms that were mapped (e.g., 'camas' -> 'leitos')"
    )
    
    @field_validator("confidence_score")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        return round(v, 3)  # Round to 3 decimal places
    
    @property
    def is_partial_match(self) -> bool:
        """Check if some entities found but others not found."""
        return len(self.entities_found_in_schema) > 0 and len(self.entities_not_found) > 0
    
    @property
    def match_ratio(self) -> float:
        """Ratio of found entities to total entities."""
        total = len(self.entities_mentioned)
        if total == 0:
            return 0.0
        found = len(self.entities_found_in_schema)
        return round(found / total, 3)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Quantas camas estão disponíveis?",
                "entities_mentioned": ["camas", "disponíveis"],
                "entities_found_in_schema": ["leitos"],
                "entities_not_found": [],
                "confidence_score": 0.85,
                "intent": "count",
                "can_answer": True,
                "reason": None,
                "similar_entities": {"leitos": 0.75},
                "synonym_mappings": {"camas": "leitos"}
            }
        }


class SmartResponse(BaseModel):
    """Response for questions that cannot be answered with available data."""
    
    can_answer: bool = Field(
        default=False,
        description="Always False for smart responses (indicates rejection)"
    )
    message: str = Field(
        description="Clear explanation of why question cannot be answered"
    )
    available_entities: List[str] = Field(
        description="Data categories that ARE available in the database"
    )
    suggestions: List[str] = Field(
        description="Alternative questions that CAN be answered",
        min_length=3,
        max_length=3
    )
    partial_match: bool = Field(
        default=False,
        description="True if some entities found but others not found"
    )
    found_entities: List[str] = Field(
        default_factory=list,
        description="Entities that WERE found (for partial matches)"
    )
    
    @field_validator("suggestions")
    @classmethod
    def validate_suggestions(cls, v: List[str]) -> List[str]:
        """Ensure exactly 3 suggestions."""
        if len(v) != 3:
            raise ValueError("Must provide exactly 3 suggestions")
        return v
    
    def format_for_streaming(self) -> List[str]:
        """Format response as list of SSE messages.
        
        Returns:
            List of strings to be sent as SSE data events
        """
        messages = []
        
        # 1. Mensagem principal
        if self.partial_match:
            messages.append(f"⚠️  {self.message}")
            messages.append("")  # Linha em branco
            if self.found_entities:
                messages.append(f"✅ Entidades encontradas: {', '.join(self.found_entities)}")
                messages.append("")
        else:
            messages.append(f"❌ {self.message}")
            messages.append("")
        
        # 2. Informações disponíveis (formatadas como lista)
        messages.append("📊 **Informações disponíveis no sistema:**")
        messages.append("")
        
        # Mostrar apenas as tabelas mais relevantes (primeiras 6)
        main_entities = self.available_entities[:6] if len(self.available_entities) > 6 else self.available_entities
        for entity in main_entities:
            messages.append(f"   • {entity}")
        
        if len(self.available_entities) > 6:
            messages.append(f"   • ... e mais {len(self.available_entities) - 6}")
        
        messages.append("")
        
        # 3. Sugestões de perguntas
        messages.append("💡 **Perguntas que posso responder:**")
        messages.append("")
        for i, suggestion in enumerate(self.suggestions, 1):
            messages.append(f"   {i}. {suggestion}")
        
        return messages
    
    class Config:
        json_schema_extra = {
            "example": {
                "can_answer": False,
                "message": "A informação sobre 'protocolos de isolamento' não está disponível no sistema",
                "available_entities": ["leitos", "atendimentos", "especialidades", "procedimentos"],
                "suggestions": [
                    "Quantos leitos estão disponíveis?",
                    "Qual a ocupação da UTI?",
                    "Quais especialidades estão cadastradas?"
                ],
                "partial_match": False,
                "found_entities": []
            }
        }

