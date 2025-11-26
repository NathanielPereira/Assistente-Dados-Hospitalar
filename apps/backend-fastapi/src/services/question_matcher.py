"""Serviço para correspondência semântica de perguntas."""

from __future__ import annotations

import difflib
import logging
import re
from typing import Optional, Tuple
from unicodedata import normalize

from src.domain.cache_entry import CacheEntry

logger = logging.getLogger(__name__)


class QuestionMatcher:
    """Corresponde perguntas do usuário com entradas no cache."""

    KEYWORD_OVERLAP_THRESHOLD = 0.7  # 70% de overlap mínimo
    SIMILARITY_THRESHOLD = 0.8  # 80% de similaridade mínimo

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normaliza texto para comparação (lowercase, remove acentos opcional)."""
        # Remove acentos (opcional - pode ser desabilitado se necessário)
        text = normalize("NFD", text.lower())
        text = "".join(c for c in text if not (ord(c) > 127 and ord(c) < 256))
        # Remove caracteres especiais, mantém apenas letras, números e espaços
        text = re.sub(r"[^a-z0-9\s]", "", text)
        # Remove espaços múltiplos
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _extract_keywords(text: str) -> set[str]:
        """Extrai palavras-chave de um texto (remove stopwords básicas)."""
        stopwords = {
            "a", "o", "e", "de", "do", "da", "em", "para", "com", "por", "que",
            "qual", "quais", "quanto", "quantos", "quantas", "como", "quando",
            "onde", "é", "são", "foi", "ser", "estar", "ter", "há", "tem",
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "are", "was", "were",
        }
        
        normalized = QuestionMatcher._normalize_text(text)
        words = normalized.split()
        keywords = {w for w in words if len(w) > 2 and w not in stopwords}
        return keywords

    @classmethod
    def _match_by_keywords(
        cls, question: str, entry: CacheEntry
    ) -> Optional[float]:
        """Corresponde pergunta com entrada usando palavras-chave."""
        question_keywords = cls._extract_keywords(question)
        
        # Usa keywords da entrada se disponíveis
        if entry.keywords:
            entry_keywords = {cls._normalize_text(kw) for kw in entry.keywords}
        else:
            # Extrai keywords da pergunta original
            entry_keywords = cls._extract_keywords(entry.question)
        
        if not question_keywords or not entry_keywords:
            return None
        
        # Calcula overlap (intersecção / união)
        intersection = question_keywords & entry_keywords
        union = question_keywords | entry_keywords
        
        if not union:
            return None
        
        overlap = len(intersection) / len(union)
        
        if overlap >= cls.KEYWORD_OVERLAP_THRESHOLD:
            return overlap
        
        return None

    @classmethod
    def _match_by_similarity(
        cls, question: str, entry: CacheEntry
    ) -> Optional[float]:
        """Corresponde pergunta com entrada usando similaridade de texto."""
        normalized_question = cls._normalize_text(question)
        normalized_entry = cls._normalize_text(entry.question)
        
        # Usa SequenceMatcher do difflib
        similarity = difflib.SequenceMatcher(
            None, normalized_question, normalized_entry
        ).ratio()
        
        if similarity >= cls.SIMILARITY_THRESHOLD:
            return similarity
        
        # Também testa variações
        for variation in entry.variations:
            normalized_variation = cls._normalize_text(variation)
            similarity = difflib.SequenceMatcher(
                None, normalized_question, normalized_variation
            ).ratio()
            if similarity >= cls.SIMILARITY_THRESHOLD:
                return similarity
        
        return None

    @classmethod
    def match(
        cls, question: str, cache_entries: list[CacheEntry]
    ) -> Optional[Tuple[CacheEntry, float]]:
        """Encontra melhor correspondência para uma pergunta no cache.
        
        Returns:
            Tupla (CacheEntry, confidence_score) ou None se não encontrar correspondência.
        """
        best_match: Optional[CacheEntry] = None
        best_score: float = 0.0
        
        for entry in cache_entries:
            # Tenta correspondência por keywords primeiro (mais rápido)
            keyword_score = cls._match_by_keywords(question, entry)
            if keyword_score and keyword_score > best_score:
                best_match = entry
                best_score = keyword_score
            
            # Se keywords não funcionou, tenta similaridade de texto
            if not keyword_score:
                similarity_score = cls._match_by_similarity(question, entry)
                if similarity_score and similarity_score > best_score:
                    best_match = entry
                    best_score = similarity_score
        
        if best_match and best_score > 0.0:
            logger.debug(
                f"Correspondência encontrada: {best_match.entry_id} "
                f"(score: {best_score:.2f})"
            )
            return (best_match, best_score)
        
        return None

    @classmethod
    def match_template(cls, question: str, cache_entries: list[CacheEntry]) -> Optional[Tuple[CacheEntry, dict]]:
        """Corresponde pergunta com template que contém placeholders.
        
        Returns:
            Tupla (CacheEntry, placeholders_dict) ou None se não encontrar.
        """
        import re
        
        # Procura por placeholders como [SETOR], [ESPECIALIDADE], etc.
        placeholder_pattern = r'\[(\w+)\]'
        
        for entry in cache_entries:
            # Verifica se a pergunta original tem placeholders
            placeholders = re.findall(placeholder_pattern, entry.question)
            if not placeholders:
                continue
            
            # Tenta extrair valores da pergunta do usuário
            extracted = {}
            question_lower = question.lower()
            entry_lower = entry.question.lower()
            
            # Extrai valores baseado em padrões comuns
            for placeholder in placeholders:
                # Procura por padrões como "UTI pediátrica", "setor X", etc.
                # Implementação simplificada - pode ser melhorada
                if placeholder.lower() == "setor":
                    # Procura por setores conhecidos na pergunta
                    setores = ["pediátrica", "adulto", "neonatal", "cardio"]
                    for setor in setores:
                        if setor in question_lower:
                            extracted[placeholder] = setor
                            break
            
            # Se extraiu valores suficientes, retorna match
            if len(extracted) == len(placeholders):
                return (entry, extracted)
        
        return None

    @classmethod
    def identify_variations(cls, question: str) -> list[str]:
        """Identifica variações comuns de uma pergunta."""
        variations = []
        normalized = cls._normalize_text(question)
        keywords = cls._extract_keywords(question)
        
        # Variação 1: Apenas keywords principais
        if keywords:
            variations.append(" ".join(sorted(keywords)))
        
        # Variação 2: Pergunta sem artigos/preposições
        words = normalized.split()
        important_words = [w for w in words if len(w) > 3]
        if important_words:
            variations.append(" ".join(important_words))
        
        return variations

