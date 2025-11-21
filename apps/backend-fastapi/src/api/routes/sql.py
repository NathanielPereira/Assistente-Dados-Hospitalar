from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.agents.sql_agent import SQLAgentService
from src.connectors.neondb_schema_service import NeonDBSchemaService
from src.services.llm_service import LLMService
from src.database import db

router = APIRouter(prefix="/v1/sql", tags=["sql"])


class AssistRequest(BaseModel):
    prompt: str
    tables: list[str] = []


class ExecuteRequest(BaseModel):
    sql: str
    approved: bool


class SQLSuggestion(BaseModel):
    sql: str
    comments: str
    estimated_rows: int | None = None


@router.post("/assist", response_model=SQLSuggestion)
async def assist_sql(req: AssistRequest):
    """Gera sugestão de SQL comentado baseado em prompt natural."""
    llm = LLMService.get_llm()
    service = SQLAgentService(llm=llm, db_conn=db)
    suggestion = await service.suggest(req.prompt, req.tables)
    return SQLSuggestion(
        sql=suggestion.sql,
        comments=suggestion.comments,
        estimated_rows=suggestion.estimated_rows
    )


@router.post("/execute")
async def execute_sql(req: ExecuteRequest):
    """Executa SQL apenas se aprovado."""
    if not req.approved:
        raise HTTPException(status_code=400, detail="SQL deve ser aprovado antes da execução")
    
    llm = LLMService.get_llm()
    service = SQLAgentService(llm=llm, db_conn=db)
    result = await service.execute(req.sql, approved=True)

    # Registra auditoria básica da execução no banco
    try:
        await db.execute_query(
            """
            INSERT INTO public.audit_entries (session_id, user_id, prompt, sql_executed, legal_basis)
            VALUES (gen_random_uuid(), %s, %s, %s, %s)
            """,
            (
                "workbench-user",
                "[SQL Workbench] Execução manual de SQL",
                req.sql,
                "contract_execution",
            ),
        )
    except Exception as audit_err:
        print(f"[audit] Falha ao registrar auditoria de SQL: {audit_err}")

    return {"results": result.data, "row_count": result.row_count}
