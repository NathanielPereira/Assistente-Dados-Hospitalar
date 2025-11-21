from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.domain.privacy_guard import PrivacyGuard, Role
from src.domain.query_session import QuerySession, QuerySessionRepository
from src.agents.chat_pipeline import ChatPipeline

router = APIRouter(prefix="/v1/chat", tags=["chat"])


class CreateSessionRequest(BaseModel):
    user_id: str


class StreamRequest(BaseModel):
    session_id: str
    prompt: str


@router.post("/sessions", status_code=201)
async def create_session(req: CreateSessionRequest):
    """Cria nova sessão de chat."""
    session = QuerySession(user_id=req.user_id)
    # TODO: salvar via repositório
    return {"session_id": str(session.session_id), "created_at": session.created_at.isoformat()}


def _validate_sql(sql: str) -> bool:
    """Valida se o SQL parece correto antes de executar."""
    if not sql or not sql.strip():
        return False
    
    sql_upper = sql.upper().strip()
    
    # Deve começar com SELECT
    if not sql_upper.startswith("SELECT"):
        return False
    
    # Não deve ter comandos perigosos
    dangerous = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
    for cmd in dangerous:
        if cmd in sql_upper and not sql_upper.startswith('--'):
            return False
    
    # Deve ter FROM (quase sempre necessário)
    if 'FROM' not in sql_upper:
        return False
    
    return True


def _calculate_uti_occupation_from_rows(rows: list[dict], prompt: str) -> dict | None:
    """Calcula ocupação de UTI quando o SQL retornou linhas individuais de leitos."""
    if not rows:
        return None
    
    prompt_lower = prompt.lower()
    
    # Verifica se a pergunta é sobre UTI
    is_uti_pediatrica = "pediatrica" in prompt_lower or "pediátrica" in prompt_lower
    is_uti_adulto = "adulto" in prompt_lower or "adulta" in prompt_lower
    is_uti = "uti" in prompt_lower
    
    # Filtra leitos por setor se especificado
    filtered_rows = rows
    if is_uti_pediatrica:
        filtered_rows = [r for r in rows if r.get("setor") == "UTI_PEDIATRICA"]
    elif is_uti_adulto:
        filtered_rows = [r for r in rows if r.get("setor") == "UTI_ADULTO"]
    elif is_uti:
        # Se só menciona UTI, pega todas as UTIs
        filtered_rows = [r for r in rows if "UTI" in str(r.get("setor", "")).upper()]
    
    if not filtered_rows:
        return None
    
    # Conta ocupados e totais
    total = len(filtered_rows)
    ocupados = sum(1 for r in filtered_rows if r.get("status", "").lower() == "ocupado")
    taxa = round(100.0 * ocupados / total, 2) if total > 0 else 0
    
    # Determina label do setor
    if is_uti_pediatrica:
        setor_label = "UTI Pediátrica"
    elif is_uti_adulto:
        setor_label = "UTI Adulto"
    elif is_uti:
        setor_label = "UTI"
    else:
        setor_label = filtered_rows[0].get("setor", "Setor consultado") if filtered_rows else "Setor"
    
    return {
        "tipo": "uti_ocupacao",
        "ocupados": str(ocupados),
        "total": str(total),
        "taxa": str(taxa),
        "setor": setor_label
    }


def _calculate_aggregation_from_rows(rows: list[dict], prompt: str) -> dict | None:
    """Calcula agregação quando a pergunta pede mas o SQL retornou linhas individuais."""
    if not rows:
        return None
    
    prompt_lower = prompt.lower()
    
    # Procura coluna de valor/receita para somar
    value_key = None
    for key in rows[0].keys():
        if any(term in key.lower() for term in ['valor', 'value', 'preco', 'price', 'receita', 'faturamento', 'faturado']):
            value_key = key
            break
    
    if value_key:
        # Calcula soma total
        if any(word in prompt_lower for word in ["total", "soma", "sum"]) and \
           any(word in prompt_lower for word in ["faturado", "faturamento", "receita", "valor"]):
            try:
                total = sum(float(row.get(value_key, 0) or 0) for row in rows)
                return {
                    "tipo": "soma",
                    "label": "Total faturado",
                    "valor": str(round(total, 2)),
                    "formato": "currency"
                }
            except (ValueError, TypeError):
                pass
        
        # Calcula média
        if any(word in prompt_lower for word in ["media", "média", "average", "avg"]):
            try:
                avg = sum(float(row.get(value_key, 0) or 0) for row in rows) / len(rows) if rows else 0
                label = "Receita média" if any(word in prompt_lower for word in ["receita", "faturamento"]) else "Média"
                return {
                    "tipo": "media",
                    "label": label,
                    "valor": str(round(avg, 2)),
                    "formato": "currency"
                }
            except (ValueError, TypeError):
                pass
    
    # Contagem - detecta várias palavras-chave
    if any(word in prompt_lower for word in ["quantos", "quanto", "quantas", "total"]) and \
       any(word in prompt_lower for word in ["procedimento", "atendimento", "leito", "especialidade", "cadastrado", "cadastrados"]):
        label = "Total"
        if "procedimento" in prompt_lower:
            label = "Procedimentos cadastrados"
        elif "atendimento" in prompt_lower:
            label = "Atendimentos cadastrados"
        elif "leito" in prompt_lower:
            label = "Leitos cadastrados"
        elif "especialidade" in prompt_lower:
            label = "Especialidades cadastradas"
        
        return {
            "tipo": "contagem",
            "label": label,
            "valor": str(len(rows))
        }
    
    return None


def _infer_summary_from_context(rows: list[dict], prompt: str) -> dict | None:
    """Tenta inferir um resumo do contexto quando não há agregação explícita."""
    if not rows:
        return None
    
    prompt_lower = prompt.lower()
    row0 = rows[0]
    
    # Se há apenas 1 linha e poucas colunas, pode ser um resultado direto
    if len(rows) == 1 and len(row0) <= 3:
        # Procura por valores numéricos que podem ser a resposta
        for key, value in row0.items():
            if isinstance(value, (int, float)) and value > 0:
                # Tenta inferir o tipo
                if "valor" in key.lower() or "receita" in key.lower():
                    return {
                        "tipo": "soma",
                        "label": "Valor encontrado",
                        "valor": str(round(float(value), 2)),
                        "formato": "currency"
                    }
                else:
                    return {
                        "tipo": "contagem",
                        "label": key.replace('_', ' ').title(),
                        "valor": str(value)
                    }
    
    return None


def _detect_aggregate_metric(row: dict, prompt: str) -> dict | None:
    """Detecta automaticamente métricas agregadas (médias, somas, contagens) e gera SUMMARY."""
    prompt_lower = prompt.lower()
    
    # Detecta contagens
    count_keys = [k for k in row.keys() if 'count' in k.lower() or 'total' in k.lower() or 'quantidade' in k.lower()]
    if count_keys and len(row) <= 3:
        count_key = count_keys[0]
        count_value = row.get(count_key, 0)
        
        # Tenta inferir label do prompt
        label = "Total"
        if "procedimento" in prompt_lower:
            label = "Procedimentos cadastrados"
        elif "atendimento" in prompt_lower:
            label = "Atendimentos cadastrados"
        elif "leito" in prompt_lower:
            label = "Leitos cadastrados"
        elif "especialidade" in prompt_lower:
            label = "Especialidades cadastradas"
        
        return {
            "tipo": "contagem",
            "label": label,
            "valor": str(count_value)
        }
    
    # Detecta médias
    avg_keys = [k for k in row.keys() if 'avg' in k.lower() or 'media' in k.lower() or 'média' in k.lower() or 'average' in k.lower()]
    if avg_keys and len(row) <= 3:
        avg_key = avg_keys[0]
        avg_value = row.get(avg_key, 0)
        
        label = "Média"
        is_currency = False
        if "receita" in prompt_lower or "valor" in prompt_lower or "faturamento" in prompt_lower:
            label = "Receita média"
            is_currency = True
        
        result = {
            "tipo": "media",
            "label": label,
            "valor": str(round(float(avg_value), 2))
        }
        if is_currency:
            result["formato"] = "currency"
        return result
    
    # Detecta somas
    sum_keys = [k for k in row.keys() if 'sum' in k.lower() or 'soma' in k.lower() or 'total_faturado' in k.lower() or 'total_faturamento' in k.lower()]
    if sum_keys and len(row) <= 3:
        sum_key = sum_keys[0]
        sum_value = row.get(sum_key, 0)
        
        label = "Total"
        is_currency = False
        if "receita" in prompt_lower or "valor" in prompt_lower or "faturamento" in prompt_lower or "faturado" in prompt_lower:
            label = "Total faturado"
            is_currency = True
        
        result = {
            "tipo": "soma",
            "label": label,
            "valor": str(round(float(sum_value), 2))
        }
        if is_currency:
            result["formato"] = "currency"
        return result
    
    return None


@router.get("/stream")
async def stream_chat_get(
    session_id: str = Query(..., description="ID da sessão"),
    prompt: str = Query(..., description="Pergunta do usuário")
):
    """Streama resposta do chat via SSE (GET para compatibilidade com EventSource)."""
    import asyncio
    from src.agents.sql_agent import SQLAgentService
    from src.services.llm_service import LLMService
    from src.database import db
    
    async def generate():
        # Passo 1: feedback imediato
        yield "data: Analisando sua pergunta...\n\n"
        
        # Inicializa serviços
        llm = LLMService.get_llm()
        sql_agent = SQLAgentService(llm=llm, db_conn=db)

        # Indica modo de operação apenas em log (não exibe para o usuário)
        mode = "LangChain SQLAgent (LLM ativo)" if sql_agent.sql_agent else "SQL simples (fallback, sem LangChain)"
        print(f"[chat] Modo de operacao: {mode}")
        yield "data: \n\nConsultando banco de dados...\n\n"
        
        try:
            # Gera SQL baseado no prompt
            suggestion = await sql_agent.suggest(prompt)
            sql = suggestion.sql

            # Log do SQL gerado (não mostra para o usuário por padrão, apenas em debug)
            print(f"[chat] SQL gerado: {sql[:200]}...")
            
            # Valida se o SQL parece correto antes de executar
            if not self._validate_sql(sql):
                yield (
                    "data: ⚠️ **Aviso:** O SQL gerado pode não estar correto.\n"
                    "data: Tentando executar mesmo assim...\n\n"
                )
            
            # Executa SQL
            yield "data: Executando consulta...\n\n"
            result = await sql_agent.execute(sql, approved=True)

            # Analisa a pergunta para entender a intenção
            prompt_lower = prompt.lower()
            wants_aggregation = any(word in prompt_lower for word in [
                "total", "soma", "sum", "média", "media", "average", "avg",
                "faturado", "faturamento", "receita", "quantos", "quanto", "quantas"
            ])
            
            summary_generated = False
            
            # Se houver resultados, SEMPRE tenta gerar resumo inteligente em card
            if result.row_count > 0 and isinstance(result.data[0], dict):
                row0 = result.data[0]

                # 1) Ocupação de UTI (card especial)
                if all(k in row0 for k in ("ocupados", "total", "taxa_ocupacao")):
                    summary = (
                        "SUMMARY|tipo=uti_ocupacao;"
                        f"ocupados={row0.get('ocupados')};"
                        f"total={row0.get('total')};"
                        f"taxa={row0.get('taxa_ocupacao')}"
                    )
                    yield f"data: {summary}\n\n"
                    summary_generated = True

                # 2) Quantidade de leitos disponíveis em um setor (card de métrica)
                elif "leitos_disponiveis" in row0:
                    setor_label = row0.get("setor") or "Setor consultado"
                    disponiveis = row0.get("leitos_disponiveis", 0)
                    summary_leitos = (
                        "SUMMARY|tipo=leitos_disponiveis;"
                        f"setor={setor_label};"
                        f"disponiveis={disponiveis}"
                    )
                    yield f"data: {summary_leitos}\n\n"
                    summary_generated = True

                # 3) Se o resultado já é uma agregação (1 linha, poucas colunas)
                elif result.row_count == 1 and len(row0) <= 5:
                    summary_data = _detect_aggregate_metric(row0, prompt)
                    if summary_data:
                        summary_str = "SUMMARY|" + ";".join([f"{k}={v}" for k, v in summary_data.items()])
                        yield f"data: {summary_str}\n\n"
                        summary_generated = True
                
                # 4) Se a pergunta é sobre ocupação de UTI mas o SQL retornou linhas individuais
                # Calcula a ocupação a partir das linhas brutas
                if not summary_generated and any(word in prompt_lower for word in ["ocupacao", "ocupação", "taxa", "uti"]):
                    summary_data = _calculate_uti_occupation_from_rows(result.data, prompt)
                    if summary_data:
                        summary_str = "SUMMARY|" + ";".join([f"{k}={v}" for k, v in summary_data.items()])
                        yield f"data: {summary_str}\n\n"
                        summary_generated = True
                
                # 5) Se a pergunta pede agregação mas o SQL retornou linhas individuais
                # SEMPRE calcula a agregação no backend
                if not summary_generated and (wants_aggregation or result.row_count > 1):
                    summary_data = _calculate_aggregation_from_rows(result.data, prompt)
                    if summary_data:
                        summary_str = "SUMMARY|" + ";".join([f"{k}={v}" for k, v in summary_data.items()])
                        yield f"data: {summary_str}\n\n"
                        summary_generated = True
                
                # 5) Se ainda não gerou summary mas há resultados, tenta inferir do contexto
                if not summary_generated:
                    summary_data = _infer_summary_from_context(result.data, prompt)
                    if summary_data:
                        summary_str = "SUMMARY|" + ";".join([f"{k}={v}" for k, v in summary_data.items()])
                        yield f"data: {summary_str}\n\n"
                        summary_generated = True
                
                # Se gerou summary, NÃO mostra detalhes técnicos - só o card
                if summary_generated:
                    # Registra auditoria ANTES de retornar
                    try:
                        await db.execute_query(
                            """
                            INSERT INTO public.audit_entries (session_id, user_id, prompt, sql_executed, legal_basis)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (
                                session_id,
                                "demo-user",
                                prompt,
                                result.sql_executed,
                                "legitimate_interest",
                            ),
                        )
                    except Exception as audit_err:
                        print(f"[audit] Falha ao registrar auditoria de chat: {audit_err}")
                    
                    yield "data: [DONE]\n\n"
                    return

            # Se não gerou summary ainda, tenta uma última vez com inferência mais agressiva
            if not summary_generated and result.row_count > 0:
                summary_data = _infer_summary_from_context(result.data, prompt)
                if summary_data:
                    summary_str = "SUMMARY|" + ";".join([f"{k}={v}" for k, v in summary_data.items()])
                    yield f"data: {summary_str}\n\n"
                    summary_generated = True
                    
                    # Registra auditoria ANTES de retornar
                    try:
                        await db.execute_query(
                            """
                            INSERT INTO public.audit_entries (session_id, user_id, prompt, sql_executed, legal_basis)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (
                                session_id,
                                "demo-user",
                                prompt,
                                result.sql_executed,
                                "legitimate_interest",
                            ),
                        )
                    except Exception as audit_err:
                        print(f"[audit] Falha ao registrar auditoria de chat: {audit_err}")
                    
                    yield "data: [DONE]\n\n"
                    return
            
            # Se ainda não gerou summary, mostra resposta informativa sobre o que foi tentado
            if not summary_generated:
                yield "data: \n\n**📊 Análise da Consulta:**\n\n"
                
                # Mostra o que foi executado
                yield f"data: **SQL Executado:**\n```sql\n{result.sql_executed}\n```\n\n"
                
                if result.row_count > 0:
                    # Encontrou dados mas não conseguiu gerar resposta estruturada
                    yield f"data: **Resultado:** Encontrei **{result.row_count}** registro(s) no banco de dados.\n\n"
                    
                    # Mostra amostra dos dados encontrados
                    if result.row_count <= 5:
                        yield "data: **Dados encontrados:**\n\n"
                        for i, row in enumerate(result.data, 1):
                            row_str = ", ".join([f"`{k}`: {v}" for k, v in row.items()])
                            yield f"data: {i}. {row_str}\n\n"
                    else:
                        yield "data: **Amostra dos dados encontrados:**\n\n"
                        for i, row in enumerate(result.data[:3], 1):
                            row_str = ", ".join([f"`{k}`: {v}" for k, v in row.items()])
                            yield f"data: {i}. {row_str}\n\n"
                        yield f"data: ... e mais {result.row_count - 3} registro(s)\n\n"
                    
                    # Explica por que não conseguiu gerar resposta
                    yield (
                        "data: ⚠️ **Não foi possível gerar uma resposta estruturada** a partir dos dados encontrados.\n\n"
                        "data: **Possíveis motivos:**\n"
                        "data: - Os dados não contêm as informações necessárias para responder sua pergunta\n"
                        "data: - A pergunta requer cálculos ou agregações que não estão nos dados brutos\n"
                        "data: - Os dados estão em formato diferente do esperado\n\n"
                        "data: **Sugestões:**\n"
                        "data: - Reformule a pergunta de forma mais específica (ex: 'qual o total faturado?', 'quantos leitos disponíveis na UTI pediátrica?')\n"
                        "data: - Verifique se os dados necessários estão no banco de dados\n"
                        "data: - Tente perguntar sobre métricas agregadas (totais, médias, contagens)\n\n"
                    )
                else:
                    # Não encontrou nenhum dado
                    yield (
                        "data: ⚠️ **Nenhum dado foi encontrado** para essa consulta.\n\n"
                        "data: **O que foi tentado:**\n"
                        f"data: - SQL executado: `{result.sql_executed}`\n"
                        "data: - Consulta realizada no banco de dados\n"
                        "data: - Nenhum registro retornado\n\n"
                        "data: **Possíveis motivos:**\n"
                        "data: - Os dados solicitados não existem no banco de dados\n"
                        "data: - Os filtros aplicados não correspondem a nenhum registro\n"
                        "data: - Os dados de teste podem não cobrir este cenário específico\n\n"
                        "data: **Sugestões:**\n"
                        "data: - Verifique se os dados necessários estão no banco\n"
                        "data: - Reformule a pergunta com termos diferentes\n"
                        "data: - Tente perguntar sobre dados que você sabe que existem (ex: 'quantos leitos temos?', 'qual o total faturado?')\n\n"
                    )
            
            # Registra auditoria UMA ÚNICA VEZ no final (garantindo que sempre registra)
            try:
                await db.execute_query(
                    """
                    INSERT INTO public.audit_entries (session_id, user_id, prompt, sql_executed, legal_basis)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        session_id,
                        "demo-user",
                        prompt,
                        result.sql_executed,
                        "legitimate_interest",
                    ),
                )
            except Exception as audit_err:
                print(f"[audit] Falha ao registrar auditoria de chat: {audit_err}")
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            
            yield (
                "data: \n\n❌ **Erro ao processar sua pergunta**\n\n"
                "data: **O que foi tentado:**\n"
                f"data: - Pergunta analisada: `{prompt}`\n"
                "data: - Tentativa de gerar SQL com LangChain\n"
                "data: - Tentativa de executar consulta no banco de dados\n\n"
                "data: **Erro encontrado:**\n"
                f"data: ```\n{str(e)}\n```\n\n"
                "data: **Possíveis motivos:**\n"
                "data: - Problema de conexão com o banco de dados\n"
                "data: - Erro na geração do SQL pelo LangChain\n"
                "data: - Dados ou estrutura do banco diferentes do esperado\n\n"
                "data: **Sugestões:**\n"
                "data: - Verifique se o banco de dados está acessível\n"
                "data: - Tente reformular a pergunta\n"
                "data: - Verifique os logs do sistema para mais detalhes\n\n"
            )
            
            # Log detalhado do erro para debug
            print(f"[chat] ERRO ao processar pergunta '{prompt}': {e}")
            print(f"[chat] Traceback completo:\n{error_trace}")
            
            yield "data: [DONE]\n\n"
            return
    
    return StreamingResponse(
        generate(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/stream")
async def stream_chat_post(req: StreamRequest):
    """Streama resposta do chat via SSE (POST alternativo)."""
    # Reutiliza a mesma lógica do GET
    from fastapi import Query
    return await stream_chat_get(
        session_id=req.session_id,
        prompt=req.prompt
    )
    
    return StreamingResponse(
        generate(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
