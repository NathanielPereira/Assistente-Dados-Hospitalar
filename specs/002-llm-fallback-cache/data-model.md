# Data Model: Sistema de Fallback e Cache de Respostas para LLM

**Feature**: 002-llm-fallback-cache  
**Date**: 2025-01-21

## Entities

### LLMProvider

Representa um provedor de LLM configurado no sistema.

**Fields**:
- `provider_id` (string, PK): Identificador único do provedor (ex: "openai", "anthropic", "google", "ollama")
- `provider_type` (enum): Tipo do provedor (OPENAI, ANTHROPIC, GOOGLE, OLLAMA)
- `api_key` (string, optional): Chave de API (criptografada em repouso)
- `api_url` (string, optional): URL base da API (para Ollama local)
- `priority` (integer): Ordem de prioridade (1 = mais prioritário)
- `enabled` (boolean): Se o provedor está habilitado
- `status` (enum): Status atual (AVAILABLE, UNAVAILABLE, RATE_LIMITED, ERROR)
- `last_health_check` (timestamp): Última verificação de saúde
- `consecutive_failures` (integer): Número de falhas consecutivas (para circuit breaker)
- `circuit_breaker_open` (boolean): Se o circuit breaker está aberto (desabilitado)
- `circuit_breaker_opened_at` (timestamp, optional): Quando o circuit breaker foi aberto

**Validation Rules**:
- `priority` deve ser único entre provedores habilitados
- `api_key` obrigatório para OPENAI, ANTHROPIC, GOOGLE
- `api_url` obrigatório para OLLAMA
- `consecutive_failures` >= 0

**State Transitions**:
- AVAILABLE → UNAVAILABLE: Após falha de API
- UNAVAILABLE → AVAILABLE: Após sucesso de health check
- AVAILABLE → RATE_LIMITED: Após erro 429
- Qualquer → ERROR: Após erro crítico
- Qualquer → Circuit breaker aberto: Após 3 falhas consecutivas
- Circuit breaker aberto → Fechado: Após 5 minutos sem tentativas

**Relationships**:
- Um LLMProvider pode ter múltiplas CacheEntry (quando usado para gerar cache)

---

### CacheEntry

Representa uma entrada no cache de perguntas e respostas conhecidas.

**Fields**:
- `entry_id` (UUID, PK): Identificador único da entrada
- `question` (string): Pergunta original
- `variations` (array[string]): Variações conhecidas da pergunta
- `keywords` (array[string]): Palavras-chave para correspondência rápida
- `sql` (string): SQL correspondente à pergunta
- `response_template` (string): Template de resposta (pode conter placeholders)
- `requires_realtime` (boolean): Se a resposta requer dados em tempo real
- `created_at` (timestamp): Quando a entrada foi criada
- `last_used` (timestamp): Última vez que foi usada
- `usage_count` (integer): Número de vezes que foi usada
- `confidence` (float): Nível de confiança (0.0 a 1.0)
- `validated` (boolean): Se passou na validação
- `validation_metadata` (JSON, optional): Metadados da validação (razões, erros, etc.)
- `provider_used` (string, optional): Provedor de LLM usado para gerar esta entrada

**Validation Rules**:
- `question` não pode estar vazio
- `sql` deve ser SQL válido (validado antes de salvar)
- `confidence` entre 0.0 e 1.0
- `usage_count` >= 0
- `variations` e `keywords` podem estar vazios mas não null

**State Transitions**:
- Criada → Validada: Após passar validação automática
- Validada → Invalidada: Se validação manual detectar erro
- Qualquer → Atualizada: Quando SQL é re-executado e dados mudam

**Relationships**:
- CacheEntry pode referenciar LLMProvider (quando gerada por LLM)

---

### ValidationResult

Representa o resultado da validação de uma resposta gerada.

**Fields**:
- `validation_id` (UUID, PK): Identificador único da validação
- `entry_id` (UUID, FK): Referência à CacheEntry validada
- `status` (enum): Status da validação (PASSED, FAILED, WARNING)
- `sql_valid` (boolean): Se SQL é válido
- `sql_error` (string, optional): Erro de SQL se houver
- `results_not_empty` (boolean): Se resultados não estão vazios quando esperado
- `response_format_valid` (boolean): Se formato da resposta está correto
- `response_errors` (array[string], optional): Erros encontrados na resposta
- `confidence_score` (float): Score de confiança calculado (0.0 a 1.0)
- `validated_at` (timestamp): Quando foi validada
- `validator_version` (string): Versão do validador usado

**Validation Rules**:
- `status` deve ser consistente com flags booleanas (PASSED = todos true)
- `confidence_score` entre 0.0 e 1.0

**Relationships**:
- ValidationResult pertence a uma CacheEntry

---

## Data Storage

### JSON Cache File (Initial)

**Location**: `apps/backend-fastapi/data/response_cache.json`

**Structure**:
```json
{
  "version": "1.0",
  "last_updated": "2025-01-21T10:00:00Z",
  "entries": [
    {
      "entry_id": "uuid",
      "question": "...",
      "variations": [...],
      "keywords": [...],
      "sql": "...",
      "response_template": "...",
      "requires_realtime": false,
      "metadata": {
        "created_at": "...",
        "last_used": "...",
        "usage_count": 0,
        "confidence": 0.95,
        "validated": true,
        "provider_used": "openai"
      }
    }
  ]
}
```

### PostgreSQL Table (Optional, Future)

**Table**: `response_cache`

**Schema**:
```sql
CREATE TABLE response_cache (
    entry_id UUID PRIMARY KEY,
    question TEXT NOT NULL,
    variations TEXT[],
    keywords TEXT[],
    sql TEXT NOT NULL,
    response_template TEXT NOT NULL,
    requires_realtime BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    confidence FLOAT CHECK (confidence >= 0.0 AND confidence <= 1.0),
    validated BOOLEAN DEFAULT FALSE,
    validation_metadata JSONB,
    provider_used VARCHAR(50),
    INDEX idx_keywords USING GIN(keywords),
    INDEX idx_question USING GIN(to_tsvector('portuguese', question))
);
```

---

## Relationships Summary

```
LLMProvider (1) ──< (many) CacheEntry
CacheEntry (1) ──< (many) ValidationResult
```

---

## Data Flow

1. **Cache Lookup**:
   - Usuário faz pergunta → QuestionMatcher busca no cache → Retorna CacheEntry se encontrada

2. **Cache Generation**:
   - LLM gera resposta → Validação cria ValidationResult → Se válido, cria CacheEntry

3. **Provider Fallback**:
   - Tenta LLMProvider[priority=1] → Se falha, tenta LLMProvider[priority=2] → Continua até sucesso ou esgotar opções

4. **Health Check**:
   - Periodicamente testa cada LLMProvider → Atualiza status → Abre circuit breaker se necessário

---

## Constraints and Business Rules

- Apenas uma CacheEntry pode ter a mesma `question` exata (duplicatas são atualizadas)
- `keywords` devem ser normalizados (lowercase, sem acentos opcionais)
- `sql` deve ser validado antes de salvar (sintaxe e execução de teste)
- Cache não pode exceder 10MB (limpeza automática de entradas antigas)
- Circuit breaker reabre automaticamente após 5 minutos
- Health check roda a cada 30 segundos para cada provedor habilitado

