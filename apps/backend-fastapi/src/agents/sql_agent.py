from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional
import logging

# LangChain 1.0 - imports atualizados
try:
    from langchain_community.agent_toolkits import create_sql_agent
    from langchain_community.utilities import SQLDatabase
    from langchain_core.language_models import BaseLanguageModel
    from langchain_openai import ChatOpenAI
except ImportError:
    create_sql_agent = None
    SQLDatabase = None
    BaseLanguageModel = Any
    ChatOpenAI = None

from src.database import db
from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SQLSuggestion:
    sql: str
    comments: str
    estimated_rows: int | None = None


@dataclass
class SQLResult:
    data: List[dict]
    row_count: int
    sql_executed: str


class SQLAgentService:
    """Serviço para sugestão e execução de SQL com LangChain."""

    def __init__(self, llm: BaseLanguageModel | None = None, db_conn: Any = None):
        self.llm = llm
        self.db_conn = db_conn
        self.sql_agent = None
        self.sql_db = None
        
        # Inicializa se tiver LLM e conexão
        if llm and db_conn:
            self._initialize_agent()

    def _initialize_agent(self):
        """Inicializa SQLAgent do LangChain com prompt customizado e contexto melhorado."""
        if not create_sql_agent or not SQLDatabase:
            return
        
        try:
            # Ajusta URI para usar driver psycopg (v3) em vez de psycopg2
            db_uri = settings.DATABASE_URL
            if db_uri.startswith("postgresql://"):
                db_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)

            # Cria SQLDatabase do LangChain com mais informações
            self.sql_db = SQLDatabase.from_uri(
                db_uri,
                include_tables=['leitos', 'especialidades', 'atendimentos'],
                sample_rows_in_table_info=3,  # Mostra exemplos de dados
                custom_table_info={
                    "leitos": """
                    Tabela de leitos hospitalares. Contém informações sobre leitos de UTI e enfermaria.
                    Colunas principais:
                    - leito_id: ID único do leito
                    - setor: Setor do leito (UTI_PEDIATRICA, UTI_ADULTO, ENFERMARIA)
                    - numero: Número do leito (ex: UTI-P-01)
                    - status: Status do leito (ocupado, disponivel)
                    - tipo: Tipo do leito (UTI, ENFERMARIA)
                    
                    IMPORTANTE: Para calcular TAXA de ocupação, sempre use esta fórmula:
                    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'ocupado') / NULLIF(COUNT(*), 0), 2) as taxa_ocupacao_percentual
                    
                    Exemplos de queries:
                    - Taxa de ocupação da UTI pediátrica (SEMPRE retornar em %): 
                      SELECT 
                        COUNT(*) FILTER (WHERE status = 'ocupado') as ocupados, 
                        COUNT(*) as total, 
                        ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'ocupado') / NULLIF(COUNT(*), 0), 2) as taxa_ocupacao_percentual 
                      FROM leitos WHERE setor = 'UTI_PEDIATRICA';
                    
                    - Leitos disponíveis por setor: 
                      SELECT setor, COUNT(*) as leitos_disponiveis 
                      FROM leitos WHERE status = 'disponivel' GROUP BY setor;
                    """,
                    "atendimentos": """
                    Tabela de atendimentos/procedimentos realizados. Contém informações sobre procedimentos médicos e valores.
                    Colunas principais:
                    - atendimento_id: ID único do atendimento
                    - especialidade_id: ID da especialidade
                    - valor: Valor do procedimento (em reais)
                    - data_atendimento: Data do atendimento
                    
                    Exemplos de queries:
                    - Total faturado: SELECT SUM(valor) as total_faturado FROM atendimentos;
                    - Receita média: SELECT AVG(valor) as receita_media FROM atendimentos;
                    - Total de procedimentos: SELECT COUNT(*) as total_procedimentos FROM atendimentos;
                    """,
                    "especialidades": """
                    Tabela de especialidades médicas.
                    Colunas principais:
                    - especialidade_id: ID único da especialidade
                    - nome: Nome da especialidade
                    """
                }
            )
            
            # Cria SQLAgent (o prompt customizado será adicionado via enhance_prompt)
            self.sql_agent = create_sql_agent(
                llm=self.llm,
                db=self.sql_db,
                verbose=True,
                agent_type="openai-tools"
            )
        except Exception as e:
            print(f"Erro ao inicializar SQLAgent: {e}")
            import traceback
            traceback.print_exc()
            self.sql_agent = None

    async def suggest(self, prompt: str, tables: List[str] = None) -> SQLSuggestion:
        """Gera SQL comentado baseado em prompt natural usando LangChain SQLAgent."""
        
        logger.info(f"[sql_agent] 🔍 suggest() called with prompt: '{prompt[:60]}...'")
        print(f"[sql_agent] 🔍 suggest() called with prompt: '{prompt[:60]}...'")
        
        # T050-T052: Smart Detection Integration - Pre-generation analysis
        from src.config import settings
        if settings.ENABLE_SMART_DETECTION:
            try:
                from src.services.schema_detector_service import SchemaDetectorService
                from src.services.question_analyzer_service import QuestionAnalyzerService
                
                # Get current schema
                schema = await SchemaDetectorService.get_schema()
                
                # Analyze question
                analysis = QuestionAnalyzerService.analyze_question(prompt, schema)
                
                logger.info(f"[smart_detection] Question analysis: can_answer={analysis.can_answer}, confidence={analysis.confidence_score:.3f}")
                print(f"[smart_detection] Question analysis: can_answer={analysis.can_answer}, confidence={analysis.confidence_score:.3f}")
                
                # Check if question is about existing tables (even if entities not directly found)
                # Common queries like "taxa de ocupação" should NOT trigger smart response
                import unicodedata
                
                def normalize_text(text: str) -> str:
                    """Normaliza texto removendo acentos para comparação."""
                    nfkd = unicodedata.normalize('NFKD', text)
                    return ''.join([c for c in nfkd if not unicodedata.combining(c)]).lower()
                
                prompt_normalized = normalize_text(prompt)
                prompt_lower = prompt.lower()
                
                # Verifica padrões válidos (com e sem acentos para robustez)
                is_valid_query_pattern = any([
                    ("taxa" in prompt_normalized and "ocupacao" in prompt_normalized),  # Taxa de ocupação
                    ("leitos" in prompt_normalized or "leito" in prompt_normalized),     # Leitos
                    ("atendimento" in prompt_normalized),                                # Atendimentos
                    ("especialidade" in prompt_normalized),                              # Especialidades
                    ("receita" in prompt_normalized or "faturamento" in prompt_normalized),  # Financeiro
                ])
                
                logger.info(f"[smart_detection] Debug: prompt_normalized='{prompt_normalized[:80]}', is_valid={is_valid_query_pattern}")
                print(f"[smart_detection] Debug: prompt_normalized='{prompt_normalized[:80]}', is_valid={is_valid_query_pattern}")
                
                # If question cannot be answered AND is not a valid query pattern, return special marker
                if not analysis.can_answer and not is_valid_query_pattern:
                    print(f"[smart_detection] ⚠️ Question cannot be answered: {analysis.reason}")
                    
                    # Return special SQLSuggestion with marker for chat.py to handle
                    return SQLSuggestion(
                        sql="--SMART_RESPONSE_MARKER",
                        comments=f"UNANSWERABLE|{analysis.reason}|{','.join(analysis.entities_not_found)}",
                        estimated_rows=None
                    )
                elif not analysis.can_answer and is_valid_query_pattern:
                    print(f"[smart_detection] ℹ️ Low confidence but valid query pattern detected, proceeding with SQL generation")
                
                # If partial match, log warning
                if analysis.is_partial_match:
                    print(f"[smart_detection] ⚠️ Partial match detected: found={analysis.entities_found_in_schema}, not_found={analysis.entities_not_found}")
                    # Continue with SQL generation but mark as partial
                    # (will be handled in chat.py streaming)
                
            except Exception as e:
                print(f"[smart_detection] Error during analysis (continuing with SQL generation): {e}")
        
        # SEMPRE tenta usar LangChain primeiro se disponível
        if self.sql_agent:
            try:
                print(f"[sql_agent] Gerando SQL com LangChain SQLAgent para: '{prompt}'")
                
                # Melhora o prompt com contexto adicional e instrução para retornar SQL
                enhanced_prompt = self._enhance_prompt(prompt)
                
                # Adiciona instrução explícita para retornar o SQL executado
                enhanced_prompt += "\n\nIMPORTANTE: Ao final da sua resposta, inclua o SQL executado no formato: SQL_EXECUTADO: SELECT ..."
                
                # Captura SQL executado durante o processo
                executed_sql = None
                
                # Usa astream_events para capturar os passos intermediários
                try:
                    async for event in self.sql_agent.astream_events({"input": enhanced_prompt}, version="v2"):
                        # Captura quando o SQL é executado (tool call)
                        if event.get("event") == "on_tool_start":
                            tool_input = event.get("data", {}).get("input", {})
                            if isinstance(tool_input, dict):
                                query = tool_input.get("query") or tool_input.get("sql")
                                if query and "SELECT" in query.upper():
                                    executed_sql = query
                                    print(f"[sql_agent] SQL capturado durante execução: {executed_sql[:200]}...")
                except Exception as stream_error:
                    print(f"[sql_agent] Aviso: Não foi possível capturar SQL via stream: {stream_error}")
                
                # Invoca o SQLAgent do LangChain
                result = await self.sql_agent.ainvoke({"input": enhanced_prompt})
                
                # O resultado do SQLAgent pode vir em diferentes formatos
                # Tenta extrair o SQL de várias formas
                sql = None
                
                if isinstance(result, dict):
                    # Pode ter 'output', 'answer', 'result', etc.
                    sql = result.get("output") or result.get("answer") or result.get("result") or result.get("sql")
                    # Verifica se há intermediate_steps com SQL
                    if not executed_sql and "intermediate_steps" in result:
                        for step in result.get("intermediate_steps", []):
                            if len(step) >= 2:
                                tool_result = step[1]
                                if isinstance(tool_result, dict) and "query" in tool_result:
                                    executed_sql = tool_result["query"]
                                elif isinstance(tool_result, str) and "SELECT" in tool_result.upper():
                                    executed_sql = tool_result
                elif isinstance(result, str):
                    sql = result
                else:
                    # Tenta converter para string
                    sql = str(result)
                
                print(f"[sql_agent] Resposta do LangChain (tipo: {type(result)}): {str(sql)[:500]}...")
                
                # Verifica se o LangChain indicou que não sabe ou não encontrou informação
                sql_str = str(sql).lower() if sql else ""
                if self._is_unknown_response(sql_str):
                    print(f"[sql_agent] ⚠️ LangChain indicou que não encontrou a informação solicitada")
                    return self._generate_not_found_response(prompt)
                
                # Prioriza SQL capturado durante execução
                sql_clean = None
                if executed_sql:
                    sql_clean = executed_sql.strip()
                    print(f"[sql_agent] ✅ SQL capturado da execução: {sql_clean[:300]}...")
                else:
                    # Tenta extrair SQL da resposta
                    sql_clean = self._extract_sql_from_response(sql) if sql else ""
                
                if sql_clean and "SELECT" in sql_clean.upper():
                    print(f"[sql_agent] ✅ SQL extraído com sucesso: {sql_clean[:300]}...")
                    return SQLSuggestion(
                        sql=sql_clean,
                        comments=f"SQL gerado pelo LangChain SQLAgent baseado no contexto do banco",
                        estimated_rows=None
                    )
                else:
                    print(f"[sql_agent] ⚠️ AVISO: LangChain retornou resposta mas não foi possível extrair SQL válido")
                    print(f"[sql_agent] Resposta original: {str(sql)[:500]}")
                    print(f"[sql_agent] SQL extraído (vazio?): '{sql_clean}'")
                    
                    # Verifica se a pergunta menciona entidades que não existem
                    if self._mentions_unknown_entities(prompt):
                        print(f"[sql_agent] Pergunta menciona entidades que não existem no banco")
                        return self._generate_not_found_response(prompt)
                    
                    print(f"[sql_agent] Tentando fallback mínimo...")
                    # Fallback mínimo apenas se LangChain não retornou SQL válido
                    return self._generate_minimal_fallback(prompt)
                    
            except Exception as e:
                logger.error(f"[sql_agent] ERRO ao gerar SQL com LangChain: {e}")
                print(f"[sql_agent] ERRO ao gerar SQL com LangChain: {e}")
                import traceback
                traceback.print_exc()
                logger.info(f"[sql_agent] 🔄 Chamando fallback devido ao erro...")
                print(f"[sql_agent] 🔄 Chamando fallback devido ao erro...")
                # Fallback mínimo apenas em caso de erro
                fallback_result = self._generate_minimal_fallback(prompt)
                logger.info(f"[sql_agent] ✅ Fallback retornou: {type(fallback_result)}")
                print(f"[sql_agent] ✅ Fallback retornou: {type(fallback_result)}")
                return fallback_result
        else:
            # Se SQLAgent não está disponível, tenta fallback mínimo
            print(f"[sql_agent] AVISO: SQLAgent não disponível (LLM não configurado ou erro na inicialização)")
            print(f"[sql_agent] Usando fallback mínimo...")
            return self._generate_minimal_fallback(prompt)
    
    def _enhance_prompt(self, prompt: str) -> str:
        """Melhora o prompt com contexto adicional e instruções claras."""
        prompt_lower = prompt.lower()
        
        # Instruções base para o LangChain
        base_instructions = (
            "Você é um especialista em SQL. Gere APENAS SQL válido e executável, sem explicações. "
            "Use agregações (COUNT, SUM, AVG) quando apropriado. "
            "Use filtros WHERE específicos baseados na pergunta. "
            "NUNCA use SELECT * a menos que seja absolutamente necessário. "
            "Para perguntas sobre TAXA ou PORCENTAGEM, SEMPRE inclua o cálculo com ROUND(100.0 * ...) para retornar o valor percentual."
        )
        
        # Adiciona contexto específico baseado na pergunta
        context_hints = []
        
        if any(word in prompt_lower for word in ["ocupacao", "ocupação", "taxa"]):
            context_hints.append(
                "OBRIGATÓRIO: Para taxa de ocupação, SEMPRE retorne a porcentagem calculada usando: "
                "ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'ocupado') / NULLIF(COUNT(*), 0), 2) as taxa_ocupacao_percentual. "
                "A resposta final deve incluir o valor percentual (ex: 60.00%), não apenas os números absolutos."
            )
        
        if any(word in prompt_lower for word in ["faturado", "faturamento", "receita"]):
            if any(word in prompt_lower for word in ["total", "soma"]):
                context_hints.append("Use SUM(valor) as total_faturado FROM atendimentos")
            elif any(word in prompt_lower for word in ["media", "média", "average"]):
                context_hints.append("Use AVG(valor) as receita_media FROM atendimentos")
        
        if any(word in prompt_lower for word in ["disponivel", "disponíveis", "livre", "livres"]):
            context_hints.append("Filtre por status = 'disponivel' na tabela leitos")
        
        if any(word in prompt_lower for word in ["pediatrica", "pediátrica"]):
            context_hints.append("Filtre por setor = 'UTI_PEDIATRICA'")
        
        if any(word in prompt_lower for word in ["adulto", "adulta"]):
            context_hints.append("Filtre por setor = 'UTI_ADULTO'")
        
        # Constrói prompt melhorado
        enhanced_parts = [prompt]
        if context_hints:
            enhanced_parts.append("\n\nInstruções específicas:")
            for hint in context_hints:
                enhanced_parts.append(f"- {hint}")
        
        enhanced = "\n".join(enhanced_parts)
        print(f"[sql_agent] Prompt melhorado: {enhanced[:300]}...")
        return enhanced
    
    def _extract_sql_from_response(self, response: str) -> str:
        """Extrai SQL limpo de uma resposta do LangChain que pode conter explicações."""
        if not response:
            return ""
        
        import re
        
        # 1) Se já é SQL puro, retorna
        response_stripped = response.strip()
        if response_stripped.upper().startswith(("SELECT", "WITH")):
            return response_stripped
        
        # 2) Procura por blocos de código SQL (```sql ... ```)
        sql_block = re.search(r'```sql\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
        if sql_block:
            sql = sql_block.group(1).strip()
            if "SELECT" in sql.upper():
                return sql
        
        # 3) Procura por blocos de código genéricos (``` ... ```)
        code_block = re.search(r'```[a-z]*\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
        if code_block:
            code = code_block.group(1).strip()
            if "SELECT" in code.upper():
                return code
        
        # 4) Procura por SQL entre aspas ou após marcadores comuns
        # Padrões como "SELECT ..." ou SQL: SELECT ... ou Query: SELECT ...
        sql_patterns = [
            r'(?:SQL|Query|sql|query):\s*(SELECT.*?)(?:\n\n|\Z)',
            r'["\'](SELECT.*?)["\']',
            r'(SELECT.*?)(?:$|\n\n|\.\s|$)',
        ]
        
        for pattern in sql_patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                sql = match.group(1).strip()
                if "SELECT" in sql.upper() and len(sql) > 10:  # Garante que é SQL válido
                    return sql
        
        # 5) Tenta extrair linhas que parecem SQL (método mais permissivo)
        lines = response.split('\n')
        sql_lines = []
        in_sql = False
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                if in_sql:
                    sql_lines.append("")  # Preserva quebras de linha
                continue
                
            line_upper = line_stripped.upper()
            
            # Inicia SQL
            if line_upper.startswith(('SELECT', 'WITH')):
                in_sql = True
                sql_lines.append(line_stripped)
            # Continua SQL
            elif in_sql:
                # Palavras-chave SQL válidas
                if any(line_upper.startswith(kw) for kw in (
                    'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER',
                    'GROUP', 'ORDER', 'HAVING', 'LIMIT', 'UNION', 'INTERSECT', 'EXCEPT',
                    'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN', 'LIKE', 'ILIKE',
                    'AS', 'ON', 'BY', 'ASC', 'DESC', 'NULL', 'IS', 'CASE', 'WHEN',
                    'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'DISTINCT', '--'
                )):
                    sql_lines.append(line_stripped)
                # Linhas que parecem parte de SQL (contém operadores, funções, etc.)
                elif re.search(r'[=<>!]|\(|\)|,|COUNT|SUM|AVG|MAX|MIN|ROUND|COALESCE', line_stripped, re.IGNORECASE):
                    sql_lines.append(line_stripped)
                # Linha vazia dentro de SQL (preserva formatação)
                elif not line_stripped:
                    sql_lines.append("")
                else:
                    # Linha que não parece SQL, pode ser fim
                    break
        
        if sql_lines:
            sql_result = '\n'.join(sql_lines).strip()
            # Remove linhas vazias no final
            sql_result = '\n'.join([l for l in sql_result.split('\n') if l.strip() or sql_result.split('\n').index(l) < len(sql_result.split('\n')) - 3])
            if "SELECT" in sql_result.upper():
                return sql_result
        
        # 6) Última tentativa: procura qualquer SELECT na resposta
        select_match = re.search(r'(SELECT.*)', response, re.DOTALL | re.IGNORECASE)
        if select_match:
            sql = select_match.group(1).strip()
            # Remove explicações após o SQL (linhas que não parecem SQL)
            sql_lines_clean = []
            for line in sql.split('\n'):
                if any(kw in line.upper() for kw in ('SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP', 'ORDER', 'LIMIT', '--', 'AND', 'OR')):
                    sql_lines_clean.append(line)
                elif re.search(r'[=<>!]|\(|\)|,', line):
                    sql_lines_clean.append(line)
                elif not line.strip():
                    sql_lines_clean.append("")
                else:
                    break  # Para na primeira linha que não parece SQL
            if sql_lines_clean:
                return '\n'.join(sql_lines_clean).strip()
        
        return ""

    def _is_unknown_response(self, response: str) -> bool:
        """Verifica se a resposta indica que a informação não foi encontrada."""
        if not response:
            return False
        
        unknown_phrases = [
            "i don't know",
            "i don't have",
            "i cannot",
            "i can't",
            "not found",
            "doesn't exist",
            "não encontrei",
            "não existe",
            "não tenho",
            "não sei",
            "não há",
            "não possui",
            "não disponível",
            "não disponivel",
            "unable to",
            "cannot find",
            "no information",
            "sem informação"
        ]
        
        response_lower = response.lower()
        return any(phrase in response_lower for phrase in unknown_phrases)
    
    def _mentions_unknown_entities(self, prompt: str) -> bool:
        """Verifica se a pergunta menciona entidades que não existem no banco."""
        prompt_lower = prompt.lower()
        
        # Entidades que NÃO existem no banco
        unknown_entities = [
            "unidade", "unidades",
            "hospital", "hospitais",
            "paciente", "pacientes",
            "medico", "médico", "medicos", "médicos",
            "funcionario", "funcionário", "funcionarios", "funcionários",
            "usuario", "usuário", "usuarios", "usuários"
        ]
        
        # Tabelas disponíveis no banco
        available_tables = [
            "leito", "leitos",
            "atendimento", "atendimentos",
            "especialidade", "especialidades"
        ]
        
        # Verifica se menciona entidades desconhecidas E não menciona tabelas disponíveis
        mentions_unknown = any(entity in prompt_lower for entity in unknown_entities)
        mentions_available = any(table in prompt_lower for table in available_tables)
        
        return mentions_unknown and not mentions_available
    
    def _generate_not_found_response(self, prompt: str) -> SQLSuggestion:
        """Gera resposta especial quando a informação não está disponível."""
        prompt_lower = prompt.lower()
        
        # Detecta qual entidade foi mencionada
        mentioned_entity = None
        if "unidade" in prompt_lower or "unidades" in prompt_lower:
            mentioned_entity = "unidades"
        elif "hospital" in prompt_lower or "hospitais" in prompt_lower:
            mentioned_entity = "hospitais"
        elif "paciente" in prompt_lower:
            mentioned_entity = "pacientes"
        elif "medico" in prompt_lower or "médico" in prompt_lower:
            mentioned_entity = "médicos"
        elif "funcionario" in prompt_lower or "funcionário" in prompt_lower:
            mentioned_entity = "funcionários"
        
        # Retorna SQL que lista as tabelas disponíveis
        # O frontend vai detectar pelo comentário especial e mostrar mensagem apropriada
        sql = """
SELECT 
    'leitos' as tabela_disponivel, 
    'Informações sobre leitos hospitalares (UTI pediátrica, UTI adulto, enfermaria)' as descricao
UNION ALL
SELECT 
    'atendimentos' as tabela_disponivel,
    'Informações sobre procedimentos médicos realizados e valores faturados' as descricao
UNION ALL
SELECT 
    'especialidades' as tabela_disponivel,
    'Informações sobre especialidades médicas cadastradas' as descricao;
"""
        
        suggestions = self._generate_suggestions_based_on_context(prompt)
        
        return SQLSuggestion(
            sql=sql.strip(),
            comments=f"INFO_NAO_DISPONIVEL|entidade={mentioned_entity or 'informação solicitada'}|sugestoes={suggestions}",
            estimated_rows=3
        )
    
    def _generate_suggestions_based_on_context(self, prompt: str) -> str:
        """Gera sugestões de perguntas baseadas no contexto do banco."""
        prompt_lower = prompt.lower()
        suggestions = []
        
        # Se perguntou sobre unidades/hospitais, sugere perguntas sobre leitos
        if any(word in prompt_lower for word in ["unidade", "unidades", "hospital", "hospitais"]):
            suggestions.extend([
                "Quantos leitos temos cadastrados?",
                "Qual a taxa de ocupação da UTI pediátrica?",
                "Quantos leitos estão disponíveis?",
                "Quais especialidades estão cadastradas?"
            ])
        # Se perguntou sobre pacientes, sugere perguntas sobre atendimentos
        elif "paciente" in prompt_lower:
            suggestions.extend([
                "Quantos atendimentos foram realizados?",
                "Qual o total faturado?",
                "Qual a receita média por especialidade?",
                "Quais especialidades têm mais atendimentos?"
            ])
        # Se perguntou sobre médicos, sugere perguntas sobre especialidades
        elif any(word in prompt_lower for word in ["medico", "médico", "medicos", "médicos"]):
            suggestions.extend([
                "Quais especialidades estão cadastradas?",
                "Quantos atendimentos por especialidade?",
                "Qual a receita média por especialidade?"
            ])
        # Sugestões gerais baseadas no que está disponível
        else:
            suggestions.extend([
                "Quantos leitos temos cadastrados?",
                "Qual a taxa de ocupação da UTI pediátrica?",
                "Quantos leitos estão disponíveis?",
                "Qual o total faturado?",
                "Qual a receita média por especialidade?",
                "Quais especialidades estão cadastradas?"
            ])
        
        return "|".join(suggestions[:5])  # Limita a 5 sugestões
    
    def _generate_minimal_fallback(self, prompt: str) -> SQLSuggestion:
        """Fallback mínimo apenas quando LangChain não consegue gerar SQL."""
        prompt_lower = prompt.lower()
        print(f"[sql_agent] Fallback mínimo para: '{prompt}'")
        
        # Gera SQL mais específico baseado no prompt
        sql = None
        
        # Receita média por especialidade
        if any(word in prompt_lower for word in ["receita", "media", "média", "average"]) and any(word in prompt_lower for word in ["especialidade", "especialidades"]):
            sql = """
SELECT 
    e.nome as especialidade,
    AVG(a.valor) as receita_media
FROM atendimentos a
JOIN especialidades e ON a.especialidade_id = e.especialidade_id
GROUP BY e.especialidade_id, e.nome
ORDER BY receita_media DESC;
"""
        # Total faturado/receita
        elif any(word in prompt_lower for word in ["total", "soma", "sum", "faturado", "faturamento", "receita"]) and not any(word in prompt_lower for word in ["media", "média", "average"]):
            if any(word in prompt_lower for word in ["especialidade", "especialidades"]):
                sql = """
SELECT 
    e.nome as especialidade,
    SUM(a.valor) as total_faturado
FROM atendimentos a
JOIN especialidades e ON a.especialidade_id = e.especialidade_id
GROUP BY e.especialidade_id, e.nome
ORDER BY total_faturado DESC;
"""
            else:
                sql = "SELECT SUM(valor) as total_faturado FROM atendimentos;"
        # Taxa de ocupação
        elif any(word in prompt_lower for word in ["ocupacao", "ocupação", "taxa"]):
            if any(word in prompt_lower for word in ["pediatrica", "pediátrica"]):
                sql = """
-- Taxa de ocupação da UTI Pediátrica
SELECT 
    COUNT(*) FILTER (WHERE status = 'ocupado') as leitos_ocupados,
    COUNT(*) as total_leitos,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'ocupado') / NULLIF(COUNT(*), 0), 2) as taxa_ocupacao_percentual
FROM leitos 
WHERE setor = 'UTI_PEDIATRICA';
"""
            elif any(word in prompt_lower for word in ["adulto", "adulta"]):
                sql = """
-- Taxa de ocupação da UTI Adulto
SELECT 
    COUNT(*) FILTER (WHERE status = 'ocupado') as leitos_ocupados,
    COUNT(*) as total_leitos,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'ocupado') / NULLIF(COUNT(*), 0), 2) as taxa_ocupacao_percentual
FROM leitos 
WHERE setor = 'UTI_ADULTO';
"""
            else:
                sql = """
-- Taxa de ocupação por setor
SELECT 
    setor,
    COUNT(*) FILTER (WHERE status = 'ocupado') as leitos_ocupados,
    COUNT(*) as total_leitos,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'ocupado') / NULLIF(COUNT(*), 0), 2) as taxa_ocupacao_percentual
FROM leitos
GROUP BY setor
ORDER BY taxa_ocupacao DESC;
"""
        # Leitos disponíveis
        elif any(word in prompt_lower for word in ["disponivel", "disponíveis", "livre", "livres"]):
            sql = """
SELECT setor, tipo, COUNT(*) as leitos_disponiveis
FROM leitos
WHERE status = 'disponivel'
GROUP BY setor, tipo
ORDER BY leitos_disponiveis DESC;
"""
        # Fallback genérico por tabela
        elif any(word in prompt_lower for word in ["leito", "leitos", "uti", "enfermaria"]):
            sql = "SELECT * FROM leitos LIMIT 20;"
        elif any(word in prompt_lower for word in ["atendimento", "atendimentos", "procedimento", "procedimentos"]):
            sql = "SELECT * FROM atendimentos LIMIT 20;"
        elif any(word in prompt_lower for word in ["especialidade", "especialidades"]):
            sql = "SELECT * FROM especialidades LIMIT 20;"
        else:
            # Último recurso: mostra estrutura das tabelas disponíveis
            sql = """
SELECT 
    'leitos' as tabela, COUNT(*) as registros FROM leitos
UNION ALL
SELECT 
    'atendimentos' as tabela, COUNT(*) as registros FROM atendimentos
UNION ALL
SELECT 
    'especialidades' as tabela, COUNT(*) as registros FROM especialidades;
"""
        
        sql_final = sql.strip() if sql else "SELECT * FROM leitos LIMIT 20;"
        logger.info(f"[sql_agent] ✅ Fallback retornando SQL ({len(sql_final)} chars): {sql_final[:150]}...")
        print(f"[sql_agent] ✅ Fallback retornando SQL ({len(sql_final)} chars): {sql_final[:150]}...")
        
        return SQLSuggestion(
            sql=sql_final,
            comments=f"SQL fallback gerado baseado no prompt (LangChain não retornou SQL válido). Considere configurar OPENAI_API_KEY para usar IA completa.",
            estimated_rows=None
        )

    def validate(self, sql: str) -> dict:
        """Valida sintaxe SQL."""
        # Validação básica
        sql_upper = sql.upper().strip()
        
        # Remove comentários do início para validação
        lines = sql_upper.split('\n')
        sql_without_comments = '\n'.join(
            line for line in lines 
            if not line.strip().startswith('--')
        ).strip()
        
        # Bloqueia comandos perigosos
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
        for keyword in dangerous_keywords:
            if keyword in sql_without_comments:
                return {
                    "is_valid": False,
                    "errors": [f"Comando {keyword} não permitido por segurança"]
                }
        
        # Verifica se é SELECT (após remover comentários)
        if not sql_without_comments.startswith('SELECT'):
            return {
                "is_valid": False,
                "errors": ["Apenas queries SELECT são permitidas"]
            }
        
        return {"is_valid": True, "errors": []}

    async def execute(self, sql: str, approved: bool = False) -> SQLResult:
        """Executa SQL aprovado."""
        if not approved:
            raise ValueError("SQL deve ser aprovado antes da execução")
        
        # Valida SQL
        validation = self.validate(sql)
        if not validation["is_valid"]:
            raise ValueError(f"SQL inválido: {', '.join(validation['errors'])}")
        
        try:
            # Executa SQL no banco
            results = await db.execute_query(sql)
            
            return SQLResult(
                data=results,
                row_count=len(results),
                sql_executed=sql
            )
        except Exception as e:
            raise ValueError(f"Erro ao executar SQL: {str(e)}")
