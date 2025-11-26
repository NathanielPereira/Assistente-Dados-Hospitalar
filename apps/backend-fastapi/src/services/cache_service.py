"""ServiÃ§o para gerenciamento de cache de respostas."""

from __future__ import annotations

import json
import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from uuid import UUID

from src.domain.cache_entry import CacheEntry
from src.domain.validation_result import ValidationResult, ValidationStatus

logger = logging.getLogger(__name__)


class ResponseValidator:
    """Valida respostas geradas antes de adicionar ao cache."""

    def __init__(self, db_conn=None):
        """Inicializa validador com conexÃ£o de banco de dados."""
        self.db_conn = db_conn

    async def validate_sql(self, sql: str) -> tuple[bool, Optional[str]]:
        """Valida SQL: sintaxe bÃ¡sica e execuÃ§Ã£o de teste."""
        if not sql or not sql.strip():
            return False, "SQL vazio"

        sql_upper = sql.upper().strip()

        # Deve comeÃ§ar com SELECT
        if not sql_upper.startswith("SELECT"):
            return False, "SQL deve comeÃ§ar com SELECT"

        # NÃ£o deve ter comandos perigosos
        dangerous = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE"]
        for cmd in dangerous:
            if cmd in sql_upper and not sql_upper.startswith("--"):
                return False, f"SQL contÃ©m comando perigoso: {cmd}"

        # Deve ter FROM (quase sempre necessÃ¡rio)
        if "FROM" not in sql_upper:
            return False, "SQL deve conter FROM"

        # Tenta executar query de teste se db_conn disponÃ­vel
        if self.db_conn:
            try:
                # Limita resultado para teste (adiciona LIMIT se nÃ£o tiver)
                test_sql = sql
                if "LIMIT" not in sql_upper:
                    test_sql = f"{sql.rstrip(';')} LIMIT 1"
                
                await self.db_conn.execute_one(test_sql)
                return True, None
            except Exception as e:
                return False, f"Erro ao executar SQL: {str(e)}"

        return True, None

    def validate_results(
        self, results: list[dict], expected_not_empty: bool = True
    ) -> tuple[bool, list[str]]:
        """Valida resultados: nÃ£o vazios quando esperado, formato correto."""
        errors = []

        if expected_not_empty:
            if not results or len(results) == 0:
                errors.append("Resultados estÃ£o vazios quando esperado dados")

        # Valida formato bÃ¡sico dos resultados
        if results:
            for i, row in enumerate(results[:5]):  # Valida primeiras 5 linhas
                if not isinstance(row, dict):
                    errors.append(f"Linha {i+1} nÃ£o Ã© um dicionÃ¡rio")
                    continue

                # Verifica se hÃ¡ valores vÃ¡lidos
                if not any(v is not None for v in row.values()):
                    errors.append(f"Linha {i+1} contÃ©m apenas valores None")

        return len(errors) == 0, errors

    def validate_response_format(self, response: str) -> tuple[bool, list[str]]:
        """Valida formato da resposta textual."""
        errors = []

        if not response or not response.strip():
            errors.append("Resposta estÃ¡ vazia")

        # Verifica se contÃ©m erros Ã³bvios
        error_indicators = [
            "erro",
            "error",
            "exception",
            "traceback",
            "failed",
            "falhou",
        ]
        response_lower = response.lower()
        for indicator in error_indicators:
            if indicator in response_lower:
                # Verifica contexto para evitar falsos positivos
                if "sem erro" not in response_lower and "no error" not in response_lower:
                    errors.append(f"Resposta pode conter erro: '{indicator}'")

        # Verifica tamanho mÃ­nimo
        if len(response.strip()) < 10:
            errors.append("Resposta muito curta (menos de 10 caracteres)")

        return len(errors) == 0, errors

    def calculate_confidence(
        self,
        sql_valid: bool,
        results_not_empty: bool,
        response_format_valid: bool,
    ) -> float:
        """Calcula score de confianÃ§a baseado nas validaÃ§Ãµes."""
        score = 0.0
        if sql_valid:
            score += 0.4
        if results_not_empty:
            score += 0.3
        if response_format_valid:
            score += 0.3
        return score

    async def validate(
        self,
        sql: str,
        results: list[dict],
        response: str,
        expected_not_empty: bool = True,
    ) -> ValidationResult:
        """Executa validaÃ§Ã£o completa e retorna ValidationResult."""
        from uuid import uuid4

        # Valida SQL
        sql_valid, sql_error = await self.validate_sql(sql)

        # Valida resultados
        results_not_empty, result_errors = self.validate_results(
            results, expected_not_empty
        )

        # Valida formato de resposta
        response_format_valid, response_errors = self.validate_response_format(response)

        # Calcula confidence score
        confidence_score = self.calculate_confidence(
            sql_valid, results_not_empty, response_format_valid
        )

        # Determina status
        if sql_valid and results_not_empty and response_format_valid:
            status = ValidationStatus.PASSED
        elif not sql_valid or not response_format_valid:
            status = ValidationStatus.FAILED
        else:
            status = ValidationStatus.WARNING

        return ValidationResult(
            validation_id=uuid4(),
            entry_id=uuid4(),  # SerÃ¡ atualizado quando associado Ã  entrada
            status=status,
            sql_valid=sql_valid,
            sql_error=sql_error,
            results_not_empty=results_not_empty,
            response_format_valid=response_format_valid,
            response_errors=response_errors if response_errors else None,
            confidence_score=confidence_score,
            validator_version="1.0",
        )


class CacheService:
    """Gerencia cache de perguntas e respostas conhecidas."""

    def __init__(self, cache_file: Optional[str] = None):
        """Inicializa serviÃ§o de cache."""
        if cache_file is None:
            # Caminho padrÃ£o relativo ao diretÃ³rio do projeto
            base_dir = Path(__file__).parent.parent.parent
            cache_file = base_dir / "data" / "response_cache.json"
        
        self.cache_file = Path(cache_file)
        self.cache_data: dict = {"version": "1.0", "last_updated": None, "entries": []}
        self._entries: dict[UUID, CacheEntry] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Carrega cache do arquivo JSON."""
        if not self.cache_file.exists():
            logger.info(f"Arquivo de cache nÃ£o encontrado: {self.cache_file}. Criando novo.")
            self._save_cache()
            return

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.cache_data = data
                
                # Converte entradas para objetos CacheEntry
                self._entries = {}
                for entry_dict in data.get("entries", []):
                    try:
                        entry = CacheEntry(**entry_dict)
                        self._entries[entry.entry_id] = entry
                    except Exception as e:
                        logger.warning(f"Erro ao carregar entrada de cache: {e}")
                        continue
                
                logger.info(f"Cache carregado: {len(self._entries)} entradas")
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {e}")
            self.cache_data = {"version": "1.0", "last_updated": None, "entries": []}
            self._entries = {}

    def _save_cache(self) -> None:
        """Salva cache no arquivo JSON de forma atÃ´mica."""
        try:
            # Cria diretÃ³rio se nÃ£o existir
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Atualiza timestamp
            self.cache_data["last_updated"] = datetime.utcnow().isoformat()
            self.cache_data["entries"] = [
                entry.model_dump(mode='json') for entry in self._entries.values()
            ]
            
            # Escreve em arquivo temporÃ¡rio primeiro
            temp_file = self.cache_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.cache_data, f, indent=2, ensure_ascii=False)
            
            # Move arquivo temporÃ¡rio para o arquivo final (operaÃ§Ã£o atÃ´mica)
            shutil.move(str(temp_file), str(self.cache_file))
            logger.debug(f"Cache salvo: {len(self._entries)} entradas")
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
            raise

    def get_entry(self, entry_id: UUID) -> Optional[CacheEntry]:
        """Retorna entrada de cache por ID."""
        return self._entries.get(entry_id)

    def get_all_entries(self) -> list[CacheEntry]:
        """Retorna todas as entradas de cache."""
        return list(self._entries.values())

    def add_entry(self, entry: CacheEntry) -> None:
        """Adiciona nova entrada ao cache."""
        # Cria backup antes de adicionar
        self.create_backup()
        
        self._entries[entry.entry_id] = entry
        self._save_cache()
        logger.info(f"Entrada adicionada ao cache: {entry.entry_id}")

    def update_entry(self, entry: CacheEntry) -> None:
        """Atualiza entrada existente no cache."""
        if entry.entry_id not in self._entries:
            raise ValueError(f"Entrada {entry.entry_id} nÃ£o encontrada no cache")
        
        self._entries[entry.entry_id] = entry
        self._save_cache()
        logger.debug(f"Entrada atualizada no cache: {entry.entry_id}")

    def increment_usage(self, entry_id: UUID) -> None:
        """Incrementa contador de uso de uma entrada."""
        entry = self._entries.get(entry_id)
        if entry:
            entry.increment_usage()
            self._save_cache()

    def delete_entry(self, entry_id: UUID) -> None:
        """Remove entrada do cache."""
        if entry_id in self._entries:
            del self._entries[entry_id]
            self._save_cache()
            logger.info(f"Entrada removida do cache: {entry_id}")

    def cleanup_cache(self, max_size_mb: float = 10.0, max_age_days: int = 30) -> int:
        """Limpa cache removendo entradas antigas ou menos usadas."""
        cache_size_mb = self.cache_file.stat().st_size / (1024 * 1024)
        
        if cache_size_mb <= max_size_mb:
            return 0
        
        removed_count = 0
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        
        # Remove entradas antigas ou pouco usadas
        entries_to_remove = []
        for entry in self._entries.values():
            should_remove = False
            
            # Remove se muito antiga e pouco usada
            if entry.last_used:
                age = datetime.utcnow() - entry.last_used
                if age.days > max_age_days and entry.usage_count < 3:
                    should_remove = True
            
            # Remove se criada hÃ¡ muito tempo e nunca usada
            if not entry.last_used:
                age = datetime.utcnow() - entry.created_at
                if age.days > max_age_days:
                    should_remove = True
            
            if should_remove:
                entries_to_remove.append(entry.entry_id)
        
        # MantÃ©m pelo menos 50 entradas mais usadas
        if len(self._entries) - len(entries_to_remove) < 50:
            # Ordena por uso e mantÃ©m as top 50
            sorted_entries = sorted(
                self._entries.values(),
                key=lambda x: x.usage_count,
                reverse=True
            )
            keep_ids = {e.entry_id for e in sorted_entries[:50]}
            entries_to_remove = [
                eid for eid in entries_to_remove if eid not in keep_ids
            ]
        
        # Remove entradas selecionadas
        for entry_id in entries_to_remove:
            del self._entries[entry_id]
            removed_count += 1
        
        if removed_count > 0:
            self._save_cache()
            logger.info(f"Cache limpo: {removed_count} entradas removidas")
        
        return removed_count

    def create_backup(self) -> Path:
        """Cria backup do cache com timestamp."""
        if not self.cache_file.exists():
            return None
        
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        backup_file = self.cache_file.parent / f"{self.cache_file.stem}.backup.{timestamp}.json"
        
        try:
            shutil.copy2(self.cache_file, backup_file)
            logger.info(f"Backup criado: {backup_file}")
            
            # Limpa backups antigos (mantÃ©m Ãºltimos 5)
            self._cleanup_old_backups(keep=5)
            
            return backup_file
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return None

    def _cleanup_old_backups(self, keep: int = 5) -> None:
        """Remove backups antigos, mantendo apenas os Ãºltimos N."""
        backup_pattern = f"{self.cache_file.stem}.backup.*.json"
        backups = sorted(
            self.cache_file.parent.glob(backup_pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Remove backups alÃ©m do limite
        for backup in backups[keep:]:
            try:
                backup.unlink()
                logger.debug(f"Backup antigo removido: {backup}")
            except Exception as e:
                logger.warning(f"Erro ao remover backup {backup}: {e}")

    def get_stats(self) -> dict:
        """Retorna estatÃ­sticas do cache."""
        total_requests = sum(e.usage_count for e in self._entries.values())
        cache_size_bytes = self.cache_file.stat().st_size if self.cache_file.exists() else 0
        
        return {
            "total_entries": len(self._entries),
            "total_requests": total_requests,
            "cache_size_bytes": cache_size_bytes,
            "cache_hit_rate": 0.0,  # SerÃ¡ calculado externamente
        }


# InstÃ¢ncia global do serviÃ§o de cache
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Retorna instÃ¢ncia global do serviÃ§o de cache."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def get_response_validator(db_conn=None) -> ResponseValidator:
    """Retorna instÃ¢ncia do validador de respostas."""
    return ResponseValidator(db_conn=db_conn)
