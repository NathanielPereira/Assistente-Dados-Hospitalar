from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

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
                    
                    Exemplos de queries:
                    - Taxa de ocupação da UTI pediátrica: SELECT COUNT(*) FILTER (WHERE status = 'ocupado') as ocupados, COUNT(*) as total, ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'ocupado') / COUNT(*), 2) as taxa_ocupacao FROM leitos WHERE setor = 'UTI_PEDIATRICA';
                    - Leitos disponíveis: SELECT setor, COUNT(*) as leitos_disponiveis FROM leitos WHERE status = 'disponivel' GROUP BY setor;
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
        # SEMPRE tenta usar LangChain primeiro se disponível
        if self.sql_agent:
            try:
                print(f"[sql_agent] Gerando SQL com LangChain SQLAgent para: '{prompt}'")
                
                # Melhora o prompt com contexto adicional
                enhanced_prompt = self._enhance_prompt(prompt)
                
                # Invoca o SQLAgent do LangChain
                result = await self.sql_agent.ainvoke({"input": enhanced_prompt})
                
                # O resultado do SQLAgent pode vir em diferentes formatos
                # Tenta extrair o SQL de várias formas
                sql = None
                
                if isinstance(result, dict):
                    # Pode ter 'output', 'answer', 'result', etc.
                    sql = result.get("output") or result.get("answer") or result.get("result") or result.get("sql")
                elif isinstance(result, str):
                    sql = result
                else:
                    # Tenta converter para string
                    sql = str(result)
                
                print(f"[sql_agent] Resposta do LangChain (tipo: {type(result)}): {str(sql)[:500]}...")
                
                # Extrai SQL limpo da resposta
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
                    print(f"[sql_agent] Tentando fallback mínimo...")
                    # Fallback mínimo apenas se LangChain não retornou SQL válido
                    return self._generate_minimal_fallback(prompt)
                    
            except Exception as e:
                print(f"[sql_agent] ERRO ao gerar SQL com LangChain: {e}")
                import traceback
                traceback.print_exc()
                print(f"[sql_agent] Usando fallback mínimo devido ao erro...")
                # Fallback mínimo apenas em caso de erro
                return self._generate_minimal_fallback(prompt)
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
            "NUNCA use SELECT * a menos que seja absolutamente necessário."
        )
        
        # Adiciona contexto específico baseado na pergunta
        context_hints = []
        
        if any(word in prompt_lower for word in ["ocupacao", "ocupação", "taxa"]):
            context_hints.append(
                "IMPORTANTE: Para taxa de ocupação, calcule: "
                "COUNT(*) FILTER (WHERE status = 'ocupado') as ocupados, "
                "COUNT(*) as total, "
                "ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'ocupado') / COUNT(*), 2) as taxa_ocupacao"
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

    def _generate_minimal_fallback(self, prompt: str) -> SQLSuggestion:
        """Fallback mínimo apenas quando LangChain não consegue gerar SQL."""
        prompt_lower = prompt.lower()
        print(f"[sql_agent] Fallback mínimo para: '{prompt}'")
        
        # Apenas casos muito específicos e críticos
        # A maioria das perguntas deve ser tratada pelo LangChain
        
        # Fallback mínimo: apenas tenta inferir a tabela correta
        # O LangChain deve fazer todo o trabalho de interpretação e geração de SQL
        if any(word in prompt_lower for word in ["leito", "leitos", "uti", "ocupacao", "ocupação", "enfermaria"]):
            sql = "SELECT * FROM leitos LIMIT 20;"
        elif any(word in prompt_lower for word in ["atendimento", "atendimentos", "procedimento", "procedimentos", "faturamento", "faturado", "receita"]):
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
        
        return SQLSuggestion(
            sql=sql.strip(),
            comments=f"SQL fallback mínimo (LangChain não disponível ou falhou). Considere configurar OPENAI_API_KEY para usar IA completa.",
            estimated_rows=None
        )

    def validate(self, sql: str) -> dict:
        """Valida sintaxe SQL."""
        # Validação básica
        sql_upper = sql.upper().strip()
        
        # Bloqueia comandos perigosos
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper and not sql_upper.startswith('--'):
                return {
                    "is_valid": False,
                    "errors": [f"Comando {keyword} não permitido por segurança"]
                }
        
        # Verifica se é SELECT
        if not sql_upper.startswith('SELECT'):
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
