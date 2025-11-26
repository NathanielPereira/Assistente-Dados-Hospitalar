"""Service for analyzing user questions and determining if they can be answered."""

from __future__ import annotations

import json
import logging
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.config import settings
from src.domain.schema_info import SchemaInfo
from src.domain.question_analysis import QuestionAnalysis, QuestionIntent

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """
    Normalize text to handle encoding issues and accents.
    Removes ALL accents to handle malformed URL encoding from Windows/PowerShell.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text without accents (ASCII-friendly)
    """
    # First normalize unicode to NFD (decomposed form)
    text = unicodedata.normalize('NFD', text)
    
    # Remove all combining marks (accents)
    # This converts "estão" -> "estao", "disponível" -> "disponivel"
    text = ''.join(
        c for c in text
        if unicodedata.category(c) != 'Mn'
    )
    
    # Final NFC normalization
    return unicodedata.normalize('NFC', text)


# Portuguese stop words (Tier 1 - always remove)
# Versão expandida com mais palavras de pergunta e estados
STOP_WORDS_TIER1 = {
    # Artigos
    "o", "a", "os", "as", "um", "uma", "uns", "umas",
    # Preposições
    "de", "do", "da", "dos", "das", "no", "na", "nos", "nas",
    "em", "por", "para", "com", "sem", "sob", "sobre",
    # Conjunções
    "e", "ou", "mas", "porque", "que", "se", "não", "sim",
    # Pronomes interrogativos e relativos
    "qual", "quais", "quanto", "quantos", "quantas", "quem", "como", "onde", "quando",
    "o que", "por que", "porque",
    # Verbos comuns (com e sem acento para compatibilidade)
    "é", "e", "são", "sao", "foi", "foram", "ser", "estar", "estão", "estao", "está", "esta", "estou",
    "tem", "temos", "têm", "tem", "tenho", "tinha", "tinham", "há", "ha", "havia",
    "ser", "sou", "somos", "era", "eram",
    # Adjetivos e estados comuns (com e sem acento)
    "disponível", "disponíveis", "disponivel", "disponiveis",
    "cadastrado", "cadastrados", "cadastrada", "cadastradas",
    "existente", "existentes", "ativo", "ativos", "ativa", "ativas",
    "ocupado", "ocupados", "ocupada", "ocupadas",
    "livre", "livres", "vazio", "vazios", "vazia", "vazias",
    "total", "totais", "geral", "gerais", "atual", "atuais",
    # Variações adicionais sem acento (fallback para encoding issues)
    "disponivel", "disponiveis", "cadastrados", "ocupados",
    # Palavras de tempo (com e sem acento)
    "hoje", "agora", "ontem", "amanhã", "amanha", "sempre", "nunca", "já", "ja",
    # Outros
    "muito", "muitos", "muita", "muitas", "pouco", "poucos", "pouca", "poucas",
    "mais", "menos", "todo", "todos", "toda", "todas",
    "esse", "essa", "esses", "essas", "este", "esta", "estes", "estas",
    "aquele", "aquela", "aqueles", "aquelas", "isso", "isto", "aquilo",
    "meu", "minha", "meus", "minhas", "seu", "sua", "seus", "suas",
    "nosso", "nossa", "nossos", "nossas",
    # Fallback para encoding mal-formado do PowerShell/Windows
    "estao", "esta�o", "estaão", "estã£o",
    "disponiveis", "dispona�veis", "disponáveis", "disponã­veis"
}


class SynonymMapper:
    """Helper class for loading and caching synonym mappings."""
    
    _cache: Dict[str, str] = {}
    _loaded: bool = False
    
    @classmethod
    def load(cls, path: Optional[Path] = None):
        """
        Load synonym mappings from JSON file.
        
        Args:
            path: Path to synonyms.json (defaults to config/synonyms.json)
        """
        if cls._loaded:
            return
        
        if path is None:
            path = Path(settings.SYNONYMS_FILE_PATH)
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                cls._cache = data.get("mappings", {})
                cls._loaded = True
                logger.info(f"Loaded {len(cls._cache)} synonym mappings")
        except FileNotFoundError:
            logger.warning(f"Synonym file not found: {path}, using empty mappings")
            cls._cache = {}
            cls._loaded = True
        except Exception as e:
            logger.error(f"Error loading synonyms: {e}")
            cls._cache = {}
            cls._loaded = True
    
    @classmethod
    def get(cls, term: str) -> str:
        """
        Get mapped term or original if no mapping exists.
        
        Args:
            term: Term to map
            
        Returns:
            Mapped term or original term
        """
        if not cls._loaded:
            cls.load()
        return cls._cache.get(term.lower(), term)


class QuestionAnalyzerService:
    """
    Service for analyzing user questions and determining answerability.
    
    Extracts entities, maps to schema, calculates confidence score.
    """
    
    _synonyms: Dict[str, str] = {}
    
    @classmethod
    def analyze_question(
        cls, 
        question: str, 
        schema: SchemaInfo
    ) -> QuestionAnalysis:
        """
        Analyze question to determine if it can be answered.
        
        Args:
            question: User's natural language question
            schema: Current database schema
            
        Returns:
            QuestionAnalysis with decision and metadata
        """
        # Normalize text to fix encoding issues (especially from URL parameters)
        question = normalize_text(question)
        
        # Ensure synonyms are loaded
        if not SynonymMapper._loaded:
            SynonymMapper.load()
        
        # Extract entities from question
        entities_mentioned, synonym_mappings = cls.extract_entities(question, apply_synonyms=True)
        
        # Detect question intent
        intent = cls.detect_intent(question)
        
        # Map entities to schema
        entities_found = []
        entities_not_found = []
        similar_entities = {}
        
        for entity in entities_mentioned:
            match_result = cls._match_entity_to_schema(entity, schema)
            
            if match_result["found"]:
                entities_found.append(match_result["table_name"])
            else:
                entities_not_found.append(entity)
                
                # Add similar matches
                if match_result["similar"]:
                    for table_name, score in match_result["similar"]:
                        similar_entities[table_name] = score
        
        # Calculate confidence score
        confidence_score = cls._calculate_confidence(
            entities_mentioned=entities_mentioned,
            entities_found=entities_found,
            similar_entities=similar_entities
        )
        
        # Determine if can answer (threshold from config)
        can_answer = (
            confidence_score >= settings.CONFIDENCE_THRESHOLD
            and len(entities_found) > 0
        )
        
        # Generate reason if cannot answer
        reason = None
        if not can_answer:
            if len(entities_mentioned) == 0:
                reason = "Não foi possível extrair entidades da pergunta"
            elif len(entities_found) == 0:
                reason = "Nenhuma das entidades mencionadas foi encontrada no schema do banco de dados"
            else:
                reason = f"Confiança insuficiente ({confidence_score:.2f} < {settings.CONFIDENCE_THRESHOLD})"
        
        return QuestionAnalysis(
            question=question,
            entities_mentioned=entities_mentioned,
            entities_found_in_schema=entities_found,
            entities_not_found=entities_not_found,
            confidence_score=confidence_score,
            intent=intent,
            can_answer=can_answer,
            reason=reason,
            similar_entities=similar_entities,
            synonym_mappings=synonym_mappings
        )
    
    @classmethod
    def extract_entities(
        cls, 
        question: str, 
        apply_synonyms: bool = True
    ) -> Tuple[List[str], Dict[str, str]]:
        """
        Extract entities from question text.
        
        Args:
            question: Question text
            apply_synonyms: Whether to apply synonym mapping
            
        Returns:
            Tuple of (entities list, synonym mappings dict)
        """
        # Normalize unicode first (fixes encoding issues)
        question = normalize_text(question)
        
        # Normalize: lowercase and split
        words = question.lower().split()
        
        # Remove stop words (strip first, then check)
        entities = [
            word.strip("?.,!;:") 
            for word in words 
            if word.strip("?.,!;:").lower() not in STOP_WORDS_TIER1 and word.strip("?.,!;:")
        ]
        
        # Apply synonym mappings
        synonym_mappings = {}
        if apply_synonyms:
            mapped_entities = []
            for entity in entities:
                mapped = SynonymMapper.get(entity)
                if mapped != entity:
                    synonym_mappings[entity] = mapped
                    mapped_entities.append(mapped)
                else:
                    mapped_entities.append(entity)
            entities = mapped_entities
        
        # Remove duplicates while preserving order
        seen = set()
        unique_entities = []
        for entity in entities:
            if entity not in seen:
                seen.add(entity)
                unique_entities.append(entity)
        
        return unique_entities, synonym_mappings
    
    @classmethod
    def detect_intent(cls, question: str) -> QuestionIntent:
        """
        Detect the intent of the question.
        
        Args:
            question: Question text
            
        Returns:
            QuestionIntent enum value
        """
        # Normalize unicode first
        question = normalize_text(question)
        question_lower = question.lower()
        
        # COUNT intent
        count_keywords = ["quantos", "quantas", "total", "número", "conta"]
        if any(kw in question_lower for kw in count_keywords):
            return QuestionIntent.COUNT
        
        # LIST intent
        list_keywords = ["quais", "liste", "mostre", "exiba", "listar"]
        if any(kw in question_lower for kw in list_keywords):
            return QuestionIntent.LIST
        
        # AGGREGATE intent (com e sem acento)
        agg_keywords = ["média", "media", "medio", "soma", "total", "máximo", "maximo", "mínimo", "minimo", "calcule"]
        if any(kw in question_lower for kw in agg_keywords):
            return QuestionIntent.AGGREGATE
        
        # STATUS intent (com e sem acento)
        status_keywords = ["status", "estado", "situação", "situacao", "ocupação", "ocupacao"]
        if any(kw in question_lower for kw in status_keywords):
            return QuestionIntent.STATUS
        
        # FILTER intent
        filter_keywords = ["onde", "quando", "com", "que tem"]
        if any(kw in question_lower for kw in filter_keywords):
            return QuestionIntent.FILTER
        
        # COMPARISON intent
        comp_keywords = ["compare", "diferença", "maior", "menor", "versus"]
        if any(kw in question_lower for kw in comp_keywords):
            return QuestionIntent.COMPARISON
        
        return QuestionIntent.UNKNOWN
    
    @classmethod
    def _match_entity_to_schema(
        cls, 
        entity: str, 
        schema: SchemaInfo
    ) -> Dict:
        """
        Match entity against schema tables.
        
        Args:
            entity: Entity to match
            schema: Database schema
            
        Returns:
            Dict with found, table_name, and similar matches
        """
        entity_lower = entity.lower()
        
        # Try exact match
        for table in schema.tables:
            if table.name.lower() == entity_lower:
                return {
                    "found": True,
                    "table_name": table.name,
                    "match_type": "exact",
                    "similar": []
                }
        
        # Try partial match (entity in table name or vice versa)
        for table in schema.tables:
            table_lower = table.name.lower()
            if entity_lower in table_lower or table_lower in entity_lower:
                return {
                    "found": True,
                    "table_name": table.name,
                    "match_type": "partial",
                    "similar": []
                }
        
        # Try similarity matching
        similar = schema.find_similar_tables(entity, threshold=settings.SIMILARITY_THRESHOLD)
        
        if similar:
            # Return best match if similarity is high enough
            best_match = similar[0]
            if best_match[1] >= 0.85:  # Very high similarity
                return {
                    "found": True,
                    "table_name": best_match[0],
                    "match_type": "similar",
                    "similar": similar
                }
            else:
                return {
                    "found": False,
                    "table_name": None,
                    "match_type": "none",
                    "similar": similar
                }
        
        return {
            "found": False,
            "table_name": None,
            "match_type": "none",
            "similar": []
        }
    
    @classmethod
    def _calculate_confidence(
        cls,
        entities_mentioned: List[str],
        entities_found: List[str],
        similar_entities: Dict[str, float]
    ) -> float:
        """
        Calculate confidence score for answering the question.
        
        Uses weighted formula: 70% base match + 30% similarity boost.
        
        Args:
            entities_mentioned: All entities extracted from question
            entities_found: Entities that matched schema exactly
            similar_entities: Near-match entities with similarity scores
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if len(entities_mentioned) == 0:
            return 0.0
        
        # Base score: ratio of found to mentioned
        base_score = len(entities_found) / len(entities_mentioned)
        
        # Similarity boost: average similarity of near-matches
        similarity_boost = 0.0
        if similar_entities:
            similarity_boost = sum(similar_entities.values()) / len(entities_mentioned)
        
        # Weighted combination (70% base + 30% similarity)
        confidence = (base_score * 0.7) + (similarity_boost * 0.3)
        
        return round(min(confidence, 1.0), 3)

