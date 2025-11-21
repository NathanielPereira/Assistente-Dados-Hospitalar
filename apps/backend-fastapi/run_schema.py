"""Script para executar schema SQL no NeonDB."""

import asyncio
import sys
from pathlib import Path

# Fix para Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src.database import db
from src.config import settings


async def run_schema():
    """Executa schema SQL no banco."""
    print("[*] Conectando ao banco...")
    
    try:
        await db.connect()
        print("[OK] Conectado")
        
        # Lê arquivo SQL
        schema_path = Path(__file__).parent.parent.parent / "infra" / "scripts" / "schema_layers.sql"
        
        if not schema_path.exists():
            print(f"[ERRO] Arquivo nao encontrado: {schema_path}")
            return
        
        print(f"[*] Lendo schema: {schema_path}")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Executa SQL completo
        print(f"[*] Executando schema SQL...")
        
        async with db.get_connection() as conn:
            async with conn.cursor() as cur:
                try:
                    # Executa todo o SQL de uma vez
                    await cur.execute(schema_sql)
                    await conn.commit()
                    print("[OK] Schema executado com sucesso!")
                except Exception as e:
                    # Se der erro, tenta executar comando por comando
                    print(f"[!] Erro ao executar tudo de uma vez, tentando comando por comando...")
                    print(f"    Erro: {str(e)[:100]}")
                    
                    # Divide por ; e executa cada comando
                    commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
                    
                    for i, command in enumerate(commands, 1):
                        if command:
                            try:
                                await cur.execute(command)
                                await conn.commit()
                                print(f"    [OK] Comando {i}/{len(commands)} executado")
                            except Exception as e2:
                                # Ignora erros de "já existe"
                                error_str = str(e2).lower()
                                if "already exists" in error_str or "duplicate" in error_str or "violates unique constraint" in error_str:
                                    print(f"    [!] Comando {i} ja existe (ignorado)")
                                else:
                                    print(f"    [ERRO] Comando {i}: {str(e2)[:80]}")
        
        print("\n[OK] Schema executado!")
        
        # Verifica tabelas criadas
        tables = await db.execute_query("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        if tables:
            print(f"\n[*] Tabelas criadas ({len(tables)}):")
            for table in tables:
                print(f"     - {table['table_name']}")
        
        await db.disconnect()
        
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_schema())

