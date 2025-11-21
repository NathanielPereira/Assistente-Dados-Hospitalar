# 🔍 Explicação: Erro "idle-in-transaction"

## O que é o erro?

```
"database": "error: terminating connection due to idle-in-transaction"
```

Este erro acontece quando:
1. Uma **transação** é aberta no PostgreSQL
2. A transação fica **aberta por muito tempo** sem commit ou rollback
3. O banco de dados (NeonDB) **mata a conexão** para evitar recursos presos

## Por que acontece?

### Problema no Código Original

O código estava executando queries assim:
```python
async with conn.cursor() as cur:
    await cur.execute(query, params)
    # Cursor fecha, mas transação pode ficar aberta!
```

Quando o cursor fecha, a **transação pode continuar aberta** se não houver commit explícito.

### NeonDB Timeout

O NeonDB (e PostgreSQL em geral) tem um timeout para transações idle:
- Se uma transação ficar aberta por muito tempo sem atividade
- O banco mata a conexão para liberar recursos
- Isso causa o erro "terminating connection due to idle-in-transaction"

## ✅ Solução Aplicada

### 1. Usar Transactions Explícitas

```python
async with conn.transaction():
    async with conn.cursor() as cur:
        await cur.execute(query, params)
        # Transaction faz commit automático ao sair do context
```

O `conn.transaction()` garante que:
- A transação é **commitada automaticamente** ao sair do bloco
- Não fica transação aberta
- Evita o timeout

### 2. Reconexão Automática

Se ainda houver erro de idle-in-transaction:
- O código detecta o erro
- Fecha a conexão antiga
- Reconecta automaticamente
- Tenta novamente

## 📊 Impacto

- ✅ **Antes**: Conexões ficavam abertas, causando timeout
- ✅ **Depois**: Transações são commitadas automaticamente
- ✅ **Resultado**: Sem erros de idle-in-transaction

## 🧪 Como Verificar

Após o deploy no Render, teste:

```bash
curl https://assistente-dados-hospitalar.onrender.com/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

Sem mais erros de "idle-in-transaction"! ✅

## 📚 Referências

- [PostgreSQL Idle-in-Transaction Timeout](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-IDLE-IN-TRANSACTION-SESSION-TIMEOUT)
- [psycopg3 Transactions](https://www.psycopg.org/psycopg3/docs/api/connections.html#transaction-management)

