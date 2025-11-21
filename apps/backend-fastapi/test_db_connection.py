"""Script para testar conexão com NeonDB."""

import asyncio
import sys

# Fix para Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src.database import db
from src.config import settings


async def test_connection():
    """Testa conexão com o banco."""
    print(f"[*] Conectando ao banco: {settings.DATABASE_URL[:50]}...")
    
    try:
        await db.connect()
        print("[OK] Pool de conexoes criado")
        
        # Testa query simples
        result = await db.execute_one("SELECT version() as version")
        if result:
            print("[OK] PostgreSQL conectado!")
            print(f"     Versao: {result.get('version', '')[:80]}...")
        
        # Lista tabelas
        tables = await db.execute_query("""
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        if tables:
            print(f"\n[*] Tabelas encontradas ({len(tables)}):")
            for table in tables:
                print(f"     - {table['table_name']} ({table['table_type']})")
        else:
            print("\n[!] Nenhuma tabela encontrada no schema 'public'")
            print("     Execute o script schema_layers.sql para criar as tabelas")
        
        await db.disconnect()
        print("\n[OK] Teste concluido com sucesso!")
        
    except Exception as e:
        print(f"[ERRO] Erro ao conectar: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_connection())

