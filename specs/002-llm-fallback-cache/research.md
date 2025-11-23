# Research: Sistema de Fallback e Cache de Respostas para LLM

**Feature**: 002-llm-fallback-cache  
**Date**: 2025-01-21

## Research Tasks

### 1. APIs Alternativas de LLM Compatíveis com LangChain

**Task**: Pesquisar APIs de LLM alternativas compatíveis com LangChain que podem ser usadas como fallback quando OpenAI está indisponível.

**Findings**:

**Decision**: Suportar múltiplas APIs gratuitas como fallbacks principais, priorizando aquelas com melhor integração LangChain e limites mais generosos: Google Gemini (via langchain-google-genai), Anthropic Claude (via langchain-anthropic), Hugging Face Inference API (via langchain-huggingface), e OpenRouter (via langchain-openai com endpoint customizado).

**Rationale**:
- **Google Gemini**: Plano gratuito generoso, excelente integração com LangChain, boa qualidade de respostas SQL, sem necessidade de cartão de crédito inicialmente
- **Anthropic Claude**: Plano gratuito disponível, API estável, boa qualidade de respostas SQL, suporte oficial no LangChain
- **Hugging Face Inference API**: 30.000 caracteres/mês gratuitos, múltiplos modelos disponíveis, integração via LangChain, útil para diversificar provedores
- **OpenRouter**: 50 requests/dia gratuitos (ou 1000/dia com $10 mínimo), acesso a múltiplos modelos através de uma única API, útil como último fallback

**Alternatives Considered**:
- **Ollama**: Requer máquina local, não adequado para ambiente cloud
- **Cohere**: Boa qualidade mas menos integração com LangChain, limites mais restritivos
- **Azure OpenAI**: Requer conta Azure paga, mais complexo de configurar
- **Clarifai**: 1000 calls/mês pode ser insuficiente para uso intensivo

**Implementation Notes**:
- LangChain fornece abstração `BaseLanguageModel` que permite trocar provedores facilmente
- Cada provedor requer chave de API diferente (GOOGLE_API_KEY, ANTHROPIC_API_KEY, HUGGINGFACE_API_KEY, OPENROUTER_API_KEY)
- Ordem de prioridade configurável via variável de ambiente para maximizar uso de limites gratuitos
- Sistema deve rotacionar entre provedores para distribuir carga e evitar esgotar limites de um único provedor

---

### 2. Estratégias de Correspondência Semântica de Perguntas

**Task**: Pesquisar métodos para identificar quando uma pergunta do usuário corresponde a uma entrada no cache, tolerando variações de linguagem.

**Findings**:

**Decision**: Usar combinação de correspondência por palavras-chave (keywords) e similaridade de texto simples (diferença de Levenshtein ou similaridade de Jaccard) para correspondência inicial. Para correspondência mais avançada, usar embeddings locais (sentence-transformers) se disponível.

**Rationale**:
- **Correspondência por palavras-chave**: Rápida (<10ms), suficiente para perguntas muito similares, não requer dependências externas
- **Similaridade de texto**: Captura variações de ordem e palavras sinônimas, ainda rápido (<50ms)
- **Embeddings locais**: Mais preciso mas requer modelo local (~400MB), útil apenas se correspondência simples falhar frequentemente

**Alternatives Considered**:
- **LLM para correspondência**: Muito lento e caro, derrota o propósito do cache
- **Elasticsearch/Solr**: Overhead desnecessário para 100 perguntas
- **Vector databases**: Complexidade excessiva para MVP

**Implementation Notes**:
- Começar com correspondência simples (keywords + Levenshtein)
- Se taxa de falsos positivos >5%, adicionar embeddings locais como camada adicional
- Cache deve incluir lista de palavras-chave e variações conhecidas para cada pergunta

---

### 3. Validação Automática de Respostas Geradas

**Task**: Pesquisar métodos para validar automaticamente se uma resposta gerada pelo LLM está correta antes de adicionar ao cache.

**Findings**:

**Decision**: Implementar validação em camadas:
1. **Validação de SQL**: Verificar que SQL é válido (sintaxe), executa sem erro, retorna resultados quando esperado
2. **Validação de resultados**: Verificar que resultados não estão vazios quando deveriam ter dados, formato correto (números, datas, etc.)
3. **Validação de resposta**: Verificar que resposta textual não está vazia, tem formato consistente, não contém erros óbvios

**Rationale**:
- Validação em camadas permite detectar diferentes tipos de erros
- Validação de SQL é crítica pois SQL inválido quebra o sistema
- Validação de resultados previne cache de respostas vazias ou incorretas
- Validação de resposta textual garante qualidade mínima

**Alternatives Considered**:
- **LLM para validação**: Muito lento e caro, circular (precisaria de outro LLM)
- **Testes manuais**: Não escala, não é automático
- **Validação apenas de SQL**: Insuficiente, não detecta respostas incorretas

**Implementation Notes**:
- Validação deve ser rápida (<1s) para não impactar UX
- Falhas de validação devem ser logadas para análise manual
- Cache só é atualizado se todas as validações passarem

---

### 4. Estrutura de Dados para Cache de Perguntas/Respostas

**Task**: Pesquisar formato e estrutura de dados adequados para armazenar cache de perguntas e respostas.

**Findings**:

**Decision**: Usar JSON como formato inicial para cache, com estrutura hierárquica que permite busca eficiente e extensão futura. Opcionalmente migrar para PostgreSQL (tabela `response_cache`) se cache crescer muito.

**Rationale**:
- **JSON**: Fácil de editar manualmente, não requer migração de banco, suficiente para até 100 perguntas (~1-2MB)
- **PostgreSQL**: Melhor para busca complexa, suporta índices, adequado para cache grande (>100 perguntas)
- Estrutura JSON permite migração fácil para PostgreSQL depois

**Structure Decision**:
```json
{
  "version": "1.0",
  "entries": [
    {
      "id": "uuid",
      "question": "pergunta original",
      "variations": ["variação 1", "variação 2"],
      "keywords": ["palavra1", "palavra2"],
      "sql": "SELECT ...",
      "response_template": "template de resposta",
      "requires_realtime": false,
      "metadata": {
        "created_at": "timestamp",
        "last_used": "timestamp",
        "usage_count": 0,
        "confidence": 0.95,
        "validated": true
      }
    }
  ]
}
```

**Alternatives Considered**:
- **YAML**: Mais legível mas parsing mais lento
- **SQLite**: Overhead desnecessário para cache pequeno
- **Redis**: Volátil, não adequado para cache persistente

**Implementation Notes**:
- Cache JSON deve ser carregado na memória na inicialização
- Atualizações devem ser escritas de forma atômica (write temp + rename)
- Backup automático antes de atualizações

---

### 5. Detecção Automática de Falhas de API

**Task**: Pesquisar métodos para detectar automaticamente quando uma API de LLM está indisponível ou sem créditos.

**Findings**:

**Decision**: Implementar health check periódico (a cada 30s) e detecção reativa em tempo real:
- **Health check periódico**: Testa cada provedor com query simples
- **Detecção reativa**: Captura exceções de API (401 Unauthorized, 429 Rate Limit, 500 Server Error, timeout)
- **Circuit breaker**: Desabilita provedor após N falhas consecutivas, reabilita após período

**Rationale**:
- Health check periódico previne tentativas desnecessárias em APIs indisponíveis
- Detecção reativa responde imediatamente a falhas durante uso
- Circuit breaker previne sobrecarga e melhora performance

**Alternatives Considered**:
- **Apenas detecção reativa**: Não previne tentativas em APIs já conhecidas como indisponíveis
- **Health check muito frequente**: Sobrecarrega APIs, custos desnecessários
- **Sem circuit breaker**: Continua tentando APIs indisponíveis, degrada performance

**Implementation Notes**:
- Health check deve usar query mínima (ex: "test") para reduzir custos
- Circuit breaker: desabilita após 3 falhas consecutivas, reabilita após 5 minutos
- Status de cada provedor deve ser observável (métricas)

---

## Summary of Decisions

1. **APIs de Fallback**: Google Gemini, Anthropic Claude, Hugging Face, OpenRouter (todas APIs gratuitas via LangChain)
2. **Correspondência de Perguntas**: Keywords + similaridade de texto (Levenshtein/Jaccard), embeddings opcionais
3. **Validação de Respostas**: Camadas (SQL válido, resultados não vazios, resposta formatada)
4. **Formato de Cache**: JSON inicial, PostgreSQL opcional para escala
5. **Detecção de Falhas**: Health check periódico + detecção reativa + circuit breaker
6. **Estratégia de Rotação**: Distribuir requisições entre provedores para maximizar uso de limites gratuitos

## Open Questions Resolved

- ✅ Qual formato de cache usar? → JSON inicial, PostgreSQL opcional
- ✅ Como detectar falhas de API? → Health check + reativo + circuit breaker
- ✅ Como validar respostas? → Validação em camadas (SQL, resultados, resposta)
- ✅ Quais APIs alternativas? → Google Gemini, Anthropic Claude, Hugging Face, OpenRouter (todas gratuitas)
- ✅ Como corresponder perguntas? → Keywords + similaridade de texto

## Dependencies Identified

- `langchain-google-genai`: Para suporte a Google Gemini (prioridade 1 - melhor limite gratuito)
- `langchain-anthropic`: Para suporte a Anthropic Claude (prioridade 2)
- `langchain-huggingface`: Para suporte a Hugging Face Inference API (prioridade 3)
- `langchain-openai`: Para suporte a OpenRouter via endpoint customizado (prioridade 4)
- `python-Levenshtein` ou `difflib`: Para similaridade de texto (biblioteca padrão)
- `sentence-transformers` (opcional): Para embeddings locais se necessário

## Limites de APIs Gratuitas (2025)

- **Google Gemini**: ~15 RPM (requests per minute), sem limite mensal claro no plano gratuito
- **Anthropic Claude**: Limite baseado em créditos mensais no plano gratuito
- **Hugging Face**: 30.000 caracteres/mês no plano gratuito
- **OpenRouter**: 50 requests/dia no plano gratuito (ou 1000/dia com $10 mínimo)

**Estratégia de Maximização**:
- Rotacionar entre provedores para distribuir carga
- Priorizar cache para perguntas frequentes
- Usar Google Gemini como primário (melhor limite)
- Monitorar uso de cada provedor para evitar esgotar limites

## Performance Considerations

- Cache em memória após carregamento inicial (<100ms)
- Busca de correspondência <100ms para 100 perguntas
- Health check de APIs <2s total (paralelo)
- Validação de resposta <1s

