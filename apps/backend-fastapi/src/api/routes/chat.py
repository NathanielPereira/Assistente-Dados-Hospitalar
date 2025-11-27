from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.domain.privacy_guard import PrivacyGuard, Role
from src.domain.query_session import QuerySession, QuerySessionRepository
from src.agents.chat_pipeline import ChatPipeline

router = APIRouter(prefix="/v1/chat", tags=["chat"])


def _ensure_valid_uuid(session_id: str) -> str:
    """
    Garante que session_id seja um UUID válido.
    Se não for, gera um UUID determinístico a partir da string.
    
    Args:
        session_id: Session ID (pode ser UUID válido ou string simples)
        
    Returns:
        UUID válido como string
    """
    try:
        # Tenta parsear como UUID
        uuid.UUID(session_id)
        return session_id  # Já é válido
    except ValueError:
        # Gera UUID determinístico (UUID5) a partir da string
        # Sempre retornará o mesmo UUID para o mesmo session_id
        namespace = uuid.UUID('00000000-0000-0000-0000-000000000000')  # Namespace fixo
        return str(uuid.uuid5(namespace, session_id))


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
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[chat/generate] 📨 Starting generate for prompt: '{prompt[:60]}...'")
        print(f"[chat/generate] 📨 Starting generate for prompt: '{prompt[:60]}...'")
        
        # Passo 1: Verifica cache antes de processar
        print(f"[chat/generate] 🔄 Loading cache service...")
        from src.services.cache_service import get_cache_service
        from src.services.question_matcher import QuestionMatcher
        
        print(f"[chat/generate] 🔄 Getting cache entries...")
        cache_service = get_cache_service()
        cache_entries = cache_service.get_all_entries()
        print(f"[chat/generate] ✅ Cache has {len(cache_entries) if cache_entries else 0} entries")
        
        if cache_entries:
            print(f"[chat/generate] 🔍 Checking cache match...")
            match_result = QuestionMatcher.match(prompt, cache_entries)
            if match_result:
                entry, confidence = match_result
                print(f"[chat/generate] ✅ CACHE HIT! confidence={confidence:.2f}, returning cached response")
                # Cache hit! Retorna resposta instantânea
                cache_service.increment_usage(entry.entry_id)
                
                # Executa SQL do cache
                try:
                    sql_agent_temp = SQLAgentService(llm=None, db_conn=db)
                    result = await sql_agent_temp.execute(entry.sql, approved=True)
                    
                    # Verifica se é ocupação UTI e gera SUMMARY card
                    if result.row_count > 0 and isinstance(result.data[0], dict):
                        row0 = result.data[0]
                        print(f"[chat/generate] 📊 Cache SQL result keys: {list(row0.keys())}")
                        
                        # Detecta se é dados de ocupação (com ou sem porcentagem)
                        has_occupation_data = (
                            ("ocupados" in row0 or "leitos_ocupados" in row0) and 
                            ("total" in row0 or "total_leitos" in row0)
                        )
                        
                        if has_occupation_data and ("taxa" in prompt.lower() or "ocupação" in prompt.lower() or "ocupacao" in prompt.lower()):
                            # Gera SUMMARY card para ocupação
                            ocupados = row0.get('ocupados') or row0.get('leitos_ocupados', 0)
                            total = row0.get('total') or row0.get('total_leitos', 0)
                            
                            # Calcula taxa se não estiver no resultado
                            taxa = row0.get('taxa_ocupacao') or row0.get('taxa_ocupacao_percentual')
                            if taxa is None and total > 0:
                                taxa = round(100.0 * int(ocupados) / int(total), 2)
                            
                            print(f"[chat/generate] 📊 Generating SUMMARY card from cache: ocupados={ocupados}, total={total}, taxa={taxa}")
                            
                            summary = (
                                "SUMMARY|tipo=uti_ocupacao;"
                                f"ocupados={ocupados};"
                                f"total={total};"
                                f"taxa={taxa}"
                            )
                            yield f"data: {summary}\n\n"
                            yield "data: [DONE]\n\n"
                            print(f"[chat/generate] ✅ Cache SUMMARY card sent, ending stream")
                            return
                    
                    # Caso contrário, usa template de texto normal
                    response = entry.response_template
                    print(f"[chat/generate] 📄 Cache template: '{response[:100]}...'")
                    if result.row_count > 0 and isinstance(result.data[0], dict):
                        # Substitui placeholders no template
                        row = result.data[0]
                        for key, value in row.items():
                            response = response.replace(f"{{{key}}}", str(value))
                    
                    print(f"[chat/generate] 📤 Sending cache response: '{response[:100]}...'")
                    yield f"data: {response}\n\n"
                    yield "data: [DONE]\n\n"
                    print(f"[chat/generate] ✅ Cache response sent, ending stream")
                    return
                except Exception as cache_err:
                    # Se falhar ao executar SQL do cache, continua com LLM
                    print(f"[chat] Erro ao executar SQL do cache: {cache_err}")
            else:
                print(f"[chat/generate] ❌ No cache match, proceeding with LLM")
        
        # Passo 2: feedback imediato (se não encontrou no cache)
        yield "data: Analisando sua pergunta...\n\n"
        
        # Inicializa serviços
        llm = LLMService.get_llm()
        
        # Verifica se há pelo menos um LLM disponível
        if not llm:
            available_providers = LLMService.get_providers_status()
            unavailable_count = sum(1 for p in available_providers if p.get("status") != "available")
            
            yield (
                "data: ⚠️ **Aviso: Nenhum provedor de LLM disponível no momento**\n\n"
                "data: O sistema precisa de um provedor de IA configurado para gerar consultas SQL.\n\n"
                "data: **Provedores configurados:**\n"
            )
            
            for provider in available_providers:
                status_icon = "✅" if provider.get("status") == "available" else "❌"
                yield f"data: - {status_icon} {provider.get('provider_id', 'unknown').upper()}: {provider.get('status', 'unknown')}\n"
            
            yield (
                "\n\n"
                "data: **Possíveis motivos:**\n"
                "data: - Chaves de API não configuradas ou inválidas\n"
                "data: - Quota/rate limit atingido em todos os provedores\n"
                "data: - Circuit breaker aberto após múltiplas falhas\n"
                "data: - Problemas temporários de conexão com as APIs\n\n"
                "data: **Sugestões:**\n"
                "data: - Verifique as variáveis de ambiente no Render (GOOGLE_API_KEY, OPENAI_API_KEY, etc.)\n"
                "data: - Aguarde alguns minutos e tente novamente (circuit breakers fecham após 5 minutos)\n"
                "data: - Configure pelo menos um provedor LLM válido (Google Gemini é recomendado e gratuito)\n\n"
                "data: O sistema tentará usar fallback mínimo de SQL, mas respostas podem ser limitadas.\n\n"
            )
        
        sql_agent = SQLAgentService(llm=llm, db_conn=db)

        # Indica modo de operação apenas em log (não exibe para o usuário)
        mode = "LangChain SQLAgent (LLM ativo)" if sql_agent.sql_agent else "SQL simples (fallback, sem LangChain)"
        print(f"[chat] Modo de operacao: {mode}")
        
        if not sql_agent.sql_agent:
            yield "data: ⚠️ Usando modo fallback (sem IA) - SQL será gerado com base em padrões simples\n\n"
        
        yield "data: \n\nConsultando banco de dados...\n\n"
        
        try:
            # Gera SQL baseado no prompt
            logger.info(f"[chat/generate] 🔄 About to call sql_agent.suggest()...")
            print(f"[chat/generate] 🔄 About to call sql_agent.suggest()...")
            
            suggestion = await sql_agent.suggest(prompt)
            
            logger.info(f"[chat/generate] ✅ suggest() returned! Type: {type(suggestion)}")
            print(f"[chat/generate] ✅ suggest() returned! Type: {type(suggestion)}")
            
            sql = suggestion.sql

            # Log do SQL gerado (não mostra para o usuário por padrão, apenas em debug)
            logger.info(f"[chat/generate] 📄 SQL returned ({len(sql)} chars): {sql[:200]}...")
            print(f"[chat/generate] 📄 SQL returned ({len(sql)} chars): {sql[:200]}...")
            
            # T053-T056: Smart Response Integration - Handle unanswerable questions
            if sql and sql.strip().startswith("--SMART_RESPONSE_MARKER"):
                print(f"[smart_detection] Detected unanswerable question, generating smart response")
                
                # Parse analysis info from comments
                comments = suggestion.comments or ""
                parts = comments.split("|")
                
                # Get schema and generate smart response
                from src.services.schema_detector_service import SchemaDetectorService
                from src.services.question_analyzer_service import QuestionAnalyzerService
                from src.services.suggestion_generator_service import SuggestionGeneratorService
                
                schema = await SchemaDetectorService.get_schema()
                analysis = QuestionAnalyzerService.analyze_question(prompt, schema)
                smart_response = SuggestionGeneratorService.generate_smart_response(
                    analysis, 
                    schema,
                    is_partial_match=analysis.is_partial_match
                )
                
                # Stream smart response
                yield "data: [SMART_RESPONSE]\n\n"
                
                # Format and stream response components
                for message_line in smart_response.format_for_streaming():
                    yield f"data: {message_line}\n\n"
                
                # T057: Audit logging (simplified - console only for now)
                try:
                    print(f"[audit] Question analysis logged: can_answer=False, confidence={analysis.confidence_score:.3f}, reason={analysis.reason}")
                except Exception as audit_error:
                    print(f"[audit] Error logging analysis decision: {audit_error}")
                
                yield "data: [DONE]\n\n"
                return
            
            # Handle partial match (some entities found, others not)
            if sql and "--PARTIAL_MATCH" in sql:
                yield "data: [PARTIAL_MATCH]\n\n"
                yield "data: ⚠️ Alguns dados solicitados não estão disponíveis, mostrando informações parciais.\n\n"
            
            # Verifica se é uma resposta de informação não disponível (legacy)
            if suggestion.comments and "INFO_NAO_DISPONIVEL" in suggestion.comments:
                # Extrai informações da resposta especial
                parts = suggestion.comments.split("|")
                entidade = "informação solicitada"
                sugestoes = []
                
                for part in parts:
                    if part.startswith("entidade="):
                        entidade = part.split("=", 1)[1]
                    elif part.startswith("sugestoes="):
                        sugestoes_str = part.split("=", 1)[1]
                        sugestoes = sugestoes_str.split("|") if sugestoes_str else []
                
                # Mostra mensagem apropriada
                yield "data: \n\n**📋 Informação Não Disponível**\n\n"
                yield f"data: ⚠️ **A informação sobre '{entidade}' não está cadastrada no banco de dados.**\n\n"
                yield "data: **Informações disponíveis no banco:**\n\n"
                yield "data: - **Leitos**: Informações sobre leitos hospitalares (UTI pediátrica, UTI adulto, enfermaria)\n"
                yield "data: - **Atendimentos**: Informações sobre procedimentos médicos realizados e valores faturados\n"
                yield "data: - **Especialidades**: Informações sobre especialidades médicas cadastradas\n\n"
                
                if sugestoes:
                    yield "data: **💡 Sugestões de perguntas que podem ser respondidas:**\n\n"
                    for i, sugestao in enumerate(sugestoes[:5], 1):
                        yield f"data: {i}. {sugestao}\n"
                    yield "data: \n"
                
                yield "data: [DONE]\n\n"
                return
            
            # Valida se o SQL parece correto antes de executar
            if not _validate_sql(sql):
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
                # Aceita tanto 'taxa_ocupacao' quanto 'taxa_ocupacao_percentual' ou 'leitos_ocupados'
                logger.info(f"[chat/generate] Checking occupation data. row0 keys: {list(row0.keys())}")
                print(f"[chat/generate] 🔍 Checking occupation data. row0 keys: {list(row0.keys())}")
                
                has_occupation_data = (
                    ("ocupados" in row0 or "leitos_ocupados" in row0) and 
                    ("total" in row0 or "total_leitos" in row0) and
                    ("taxa_ocupacao" in row0 or "taxa_ocupacao_percentual" in row0)
                )
                
                logger.info(f"[chat/generate] has_occupation_data = {has_occupation_data}")
                print(f"[chat/generate] ✅ has_occupation_data = {has_occupation_data}")
                
                if has_occupation_data:
                    ocupados = row0.get('ocupados') or row0.get('leitos_ocupados', 0)
                    total = row0.get('total') or row0.get('total_leitos', 0)
                    taxa = row0.get('taxa_ocupacao') or row0.get('taxa_ocupacao_percentual', 0)
                    
                    logger.info(f"[chat/generate] 📊 Generating occupation card: ocupados={ocupados}, total={total}, taxa={taxa}")
                    print(f"[chat/generate] 📊 Generating occupation card: ocupados={ocupados}, total={total}, taxa={taxa}")
                    
                    summary = (
                        "SUMMARY|tipo=uti_ocupacao;"
                        f"ocupados={ocupados};"
                        f"total={total};"
                        f"taxa={taxa}"
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
                                _ensure_valid_uuid(session_id),  # Converte para UUID válido
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
                                _ensure_valid_uuid(session_id),  # Converte para UUID válido
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
            error_str = str(e).lower()
            
            # Detecta tipo de erro para mensagem mais específica
            is_llm_error = any(phrase in error_str for phrase in [
                "404", "not found", "does not exist", "not supported", 
                "429", "quota", "rate limit", "insufficient_quota",
                "modelo", "model", "api key", "authentication", "authorization"
            ])
            is_db_error = any(phrase in error_str for phrase in [
                "connection", "conexão", "lost", "perdida", "closed", 
                "broken", "timeout", "database", "banco"
            ])
            
            yield (
                "data: \n\n❌ **Erro ao processar sua pergunta**\n\n"
                "data: **O que foi tentado:**\n"
                f"data: - Pergunta analisada: `{prompt}`\n"
                "data: - Tentativa de gerar SQL com LangChain\n"
                "data: - Tentativa de executar consulta no banco de dados\n\n"
                "data: **Erro encontrado:**\n"
                f"data: ```\n{str(e)[:500]}\n```\n\n"
            )
            
            # Mensagens específicas por tipo de erro
            if is_llm_error:
                yield (
                    "data: **Possíveis motivos (Provedor de IA):**\n"
                    "data: - Modelo de IA não encontrado ou desatualizado (ex: gemini-pro não existe mais)\n"
                    "data: - Quota/rate limit atingido em todos os provedores configurados\n"
                    "data: - Chave de API inválida ou expirada\n"
                    "data: - Circuit breaker aberto após múltiplas falhas\n\n"
                    "data: **Sugestões:**\n"
                    "data: - Verifique as variáveis de ambiente no Render (GOOGLE_API_KEY, OPENAI_API_KEY)\n"
                    "data: - Aguarde alguns minutos e tente novamente (circuit breakers fecham após 5 minutos)\n"
                    "data: - O sistema tentou usar fallback, mas pode precisar de configuração de API\n\n"
                )
            elif is_db_error:
                yield (
                    "data: **Possíveis motivos (Banco de Dados):**\n"
                    "data: - Conexão com o banco de dados foi perdida\n"
                    "data: - Timeout na conexão (banco pode estar sobrecarregado)\n"
                    "data: - Problemas temporários de rede\n"
                    "data: - Banco de dados indisponível ou em manutenção\n\n"
                    "data: **Sugestões:**\n"
                    "data: - O sistema tentará reconectar automaticamente\n"
                    "data: - Aguarde alguns segundos e tente novamente\n"
                    "data: - Verifique se o banco de dados está acessível\n\n"
                )
            else:
                yield (
                    "data: **Possíveis motivos:**\n"
                    "data: - Problema de conexão com o banco de dados\n"
                    "data: - Erro na geração do SQL pelo LangChain\n"
                    "data: - Dados ou estrutura do banco diferentes do esperado\n"
                    "data: - Problemas temporários de rede ou serviço\n\n"
                    "data: **Sugestões:**\n"
                    "data: - Verifique se o banco de dados está acessível\n"
                    "data: - Tente reformular a pergunta\n"
                    "data: - Aguarde alguns segundos e tente novamente\n"
                    "data: - Verifique os logs do sistema para mais detalhes\n\n"
                )
            
            # Log detalhado do erro para debug
            print(f"[chat] ERRO ao processar pergunta '{prompt}': {e}")
            print(f"[chat] Traceback completo:\n{error_trace}")
            logger.error(f"[chat] ERRO ao processar pergunta: {e}", exc_info=True)
            
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
