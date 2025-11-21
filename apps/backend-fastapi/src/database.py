"""Conexão com o banco de dados NeonDB."""

from __future__ import annotations

import sys
import asyncio
import psycopg
from psycopg import AsyncConnection
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Fix para Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src.config import settings


class Database:
    """Gerenciador de conexões com o banco de dados."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._conn: AsyncConnection | None = None

    async def connect(self) -> None:
        """Cria conexão com o banco."""
        if self._conn is None:
            self._conn = await psycopg.AsyncConnection.connect(self.connection_string)

    async def disconnect(self) -> None:
        """Fecha conexão com o banco."""
        if self._conn:
            try:
                await self._conn.close()
            except:
                pass
            finally:
                self._conn = None

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[AsyncConnection, None]:
        """Context manager para obter conexão."""
        if self._conn is None or self._conn.closed:
            await self.connect()
        
        # Garante que a conexão está ativa
        try:
            if self._conn.closed:
                await self.connect()
        except:
            await self.connect()
        
        yield self._conn

    async def execute_query(self, query: str, params: tuple = ()) -> list[dict]:
        """Executa query e retorna resultados como lista de dicionários."""
        async with self.get_connection() as conn:
            # Usa autocommit para evitar idle-in-transaction timeout
            # psycopg3 faz commit automático quando o cursor fecha, mas garantimos com transaction
            async with conn.transaction():
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    if cur.description:
                        columns = [desc[0] for desc in cur.description]
                        rows = await cur.fetchall()
                        # Transaction faz commit automático ao sair do context
                        return [dict(zip(columns, row)) for row in rows]
                    return []

    async def execute_one(self, query: str, params: tuple = ()) -> dict | None:
        """Executa query e retorna um único resultado."""
        results = await self.execute_query(query, params)
        return results[0] if results else None


# Instância global do banco de dados
db = Database(settings.DATABASE_URL)

