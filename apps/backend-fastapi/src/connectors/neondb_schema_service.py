from __future__ import annotations

from typing import Dict, List, Optional, Any
from src.database import Database


class SchemaRegistry:
    """Introspecção do schema NeonDB com regras de masking."""

    def __init__(self, db: Database):
        self.db = db
        self._cache: Dict[str, List[Dict]] = {}

    async def get_tables(self, schema: str = "public") -> List[Dict]:
        """Lista tabelas do schema com metadados."""
        cache_key = f"{schema}_tables"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        query = """
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_schema = %s
            ORDER BY table_name
        """
        try:
            tables = await self.db.execute_query(query, (schema,))
            self._cache[cache_key] = tables
            return tables
        except Exception as e:
            print(f"Erro ao buscar tabelas: {e}")
            return []

    async def get_columns(self, table: str, schema: str = "public") -> List[Dict]:
        """Lista colunas com tipos e regras de masking."""
        query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        try:
            columns = await self.db.execute_query(query, (schema, table))
            return columns
        except Exception as e:
            print(f"Erro ao buscar colunas: {e}")
            return []

    def get_masking_rules(self, column: str) -> Optional[str]:
        """Retorna regra de masking para coluna sensível."""
        sensitive_patterns = {
            "cpf": "MASK_CPF",
            "rg": "MASK_RG",
            "email": "MASK_EMAIL",
        }
        for pattern, rule in sensitive_patterns.items():
            if pattern in column.lower():
                return rule
        return None


class NeonDBSchemaService:
    """Serviço principal de introspecção NeonDB."""

    def __init__(self, db: Database):
        self.db = db
        self.registry = SchemaRegistry(db)

    async def introspect(self, schema: str = "public") -> Dict:
        """Retorna schema completo com masking rules."""
        tables = await self.registry.get_tables(schema)
        result = {}
        for table_info in tables:
            table_name = table_info["table_name"]
            columns = await self.registry.get_columns(table_name, schema)
            result[table_name] = {
                "columns": columns,
                "masking_rules": {
                    col["column_name"]: self.registry.get_masking_rules(col["column_name"])
                    for col in columns
                }
            }
        return result

    async def test_connection(self) -> bool:
        """Testa conexão com o banco."""
        try:
            result = await self.db.execute_one("SELECT 1 as test")
            return result is not None and result.get("test") == 1
        except Exception as e:
            print(f"Erro ao testar conexão: {e}")
            return False
