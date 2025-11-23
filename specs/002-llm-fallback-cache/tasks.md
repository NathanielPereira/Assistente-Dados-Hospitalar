# Tasks: Sistema de Fallback e Cache de Respostas para LLM

**Input**: Design documents de `/specs/002-llm-fallback-cache/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.yaml, quickstart.md  
**Tests**: Inclusos para validar fallback de APIs, cache e correspondência de perguntas.  
**Organização**: Tarefas agrupadas por história de usuário para permitir implementação e testes independentes.

## Verificações Constitucionais (preencher antes de distribuir tarefas)

- [ ] Dados clínicos protegidos: confirmar que T004, T005, T006 cobrem que cache não armazena dados sensíveis e SQL é tratado conforme políticas existentes.
- [ ] Auditoria: garantir que T007, T015, T020 registrem uso de cache e provedores de LLM usados.
- [ ] Evidências/Testes: assegurar que T008, T009, T010, T011 tenham suites de teste definidas antes da implementação.
- [ ] Interoperabilidade: validar que T002, T003 permitam múltiplos provedores sem alterar interfaces principais.
- [ ] Observabilidade/Resiliência: confirmar que T012, T013, T014 entregam métricas de cache, status de provedores e circuit breakers.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Configurar dependências e estrutura básica para suporte multi-provider.

- [ ] T001 Criar estrutura de diretórios `apps/backend-fastapi/data/` para arquivo de cache JSON e `apps/backend-fastapi/src/services/` para novos serviços.
- [ ] T002 Instalar dependências LangChain multi-provider em `apps/backend-fastapi/pyproject.toml`: `langchain-google-genai`, `langchain-anthropic`, `langchain-huggingface`, `langchain-openai`.
- [ ] T003 Atualizar `apps/backend-fastapi/src/config.py` para suportar variáveis de ambiente de múltiplos provedores: `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`, `HUGGINGFACE_API_KEY`, `OPENROUTER_API_KEY`, `LLM_PROVIDER_PRIORITY`, `LLM_ROTATION_STRATEGY`.
- [ ] T004 Criar arquivo de cache inicial `apps/backend-fastapi/data/response_cache.json` com estrutura JSON vazia e exemplo de entrada conforme data-model.md.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implementar modelos de domínio e abstrações base necessárias para todas as user stories.

- [ ] T005 [P] Criar modelo `LLMProvider` em `apps/backend-fastapi/src/domain/llm_provider.py` com campos: provider_id, provider_type, api_key, priority, enabled, status, last_health_check, consecutive_failures, circuit_breaker_open, circuit_breaker_opened_at conforme data-model.md.
- [ ] T006 [P] Criar modelo `CacheEntry` em `apps/backend-fastapi/src/domain/cache_entry.py` com campos: entry_id, question, variations, keywords, sql, response_template, requires_realtime, created_at, last_used, usage_count, confidence, validated, validation_metadata, provider_used conforme data-model.md.
- [ ] T007 [P] Criar modelo `ValidationResult` em `apps/backend-fastapi/src/domain/validation_result.py` com campos: validation_id, entry_id, status, sql_valid, sql_error, results_not_empty, response_format_valid, response_errors, confidence_score, validated_at, validator_version conforme data-model.md.
- [ ] T008 Criar testes unitários para modelos de domínio em `apps/backend-fastapi/tests/domain/test_llm_provider.py`, `test_cache_entry.py`, `test_validation_result.py` validando regras de negócio e transições de estado.

---

## Phase 3: User Story 1 - Continuidade de Serviço com Fallback de API (Priority: P1) 🎯 MVP

**Goal**: Sistema detecta automaticamente falhas de API e alterna entre múltiplos provedores gratuitos, garantindo disponibilidade mesmo quando APIs principais estão indisponíveis.  
**Independent Test**: Desabilitar chave da API OpenAI, fazer pergunta no chat, verificar que sistema detecta falha automaticamente, tenta Google Gemini, Anthropic, Hugging Face e OpenRouter em sequência, retorna resposta válida sem interrupção do serviço.

### Tests para US1 (obrigatórios)

- [ ] T009 [P] [US1] Escrever testes de integração `apps/backend-fastapi/tests/test_llm_fallback.py` validando detecção de falha, alternância entre provedores, circuit breaker e health check periódico.
- [ ] T010 [P] [US1] Criar testes unitários `apps/backend-fastapi/tests/services/test_llm_service_fallback.py` cobrindo inicialização de múltiplos provedores, seleção por prioridade e rotação.

### Implementação US1

- [ ] T011 [US1] Estender `LLMService` em `apps/backend-fastapi/src/services/llm_service.py` para suportar múltiplos provedores: adicionar método `_initialize_providers()` que carrega configurações de ambiente e cria instâncias LangChain para cada provedor configurado.
- [ ] T012 [US1] Implementar health check periódico em `apps/backend-fastapi/src/services/llm_service.py`: método `_health_check_providers()` que testa cada provedor a cada 30 segundos com query simples, atualiza status e abre circuit breaker após 3 falhas consecutivas.
- [ ] T013 [US1] Implementar circuit breaker em `apps/backend-fastapi/src/services/llm_service.py`: lógica que desabilita provedor após N falhas, reabilita após 5 minutos, atualiza `circuit_breaker_open` e `circuit_breaker_opened_at` em `LLMProvider`.
- [ ] T014 [US1] Implementar detecção reativa de falhas em `apps/backend-fastapi/src/services/llm_service.py`: método `_handle_provider_error()` que captura exceções (401, 429, 500, timeout), atualiza `consecutive_failures` e alterna para próximo provedor.
- [ ] T015 [US1] Implementar seleção de provedor com fallback em `apps/backend-fastapi/src/services/llm_service.py`: método `get_llm()` modificado para tentar provedores por ordem de prioridade, usar rotação round-robin se configurado, retornar primeiro disponível ou None se todos falharem.
- [ ] T016 [US1] Implementar rotação entre provedores em `apps/backend-fastapi/src/services/llm_service.py`: método `_rotate_providers()` que distribui requisições entre provedores habilitados conforme `LLM_ROTATION_STRATEGY` (round_robin, least_used, priority).
- [ ] T017 [US1] Integrar fallback no endpoint de chat em `apps/backend-fastapi/src/api/routes/chat.py`: modificar `generate()` para usar `LLMService.get_llm()` que agora retorna provedor disponível ou None, tratar caso de todos indisponíveis retornando mensagem apropriada.
- [ ] T018 [P] [US1] Adicionar métricas de observabilidade em `apps/backend-fastapi/src/observability/metrics.py`: contadores de uso por provedor, taxa de falha, tempo de resposta por provedor, status de circuit breakers.
- [ ] T019 [P] [US1] Criar endpoint de status de provedores em `apps/backend-fastapi/src/api/routes/chat.py` ou novo arquivo `llm.py`: `GET /v1/llm/providers` retornando lista de provedores com status, limites usados, circuit breaker status conforme contracts/api.yaml.

---

## Phase 4: User Story 2 - Cache de Perguntas e Respostas Conhecidas (Priority: P1) 🎯 MVP

**Goal**: Sistema identifica perguntas conhecidas no cache e retorna respostas pré-configuradas instantaneamente, executando SQL atualizado quando necessário.  
**Independent Test**: Criar arquivo `response_cache.json` com pergunta exemplo "Qual a taxa de ocupação da UTI pediátrica?", fazer pergunta similar no chat, verificar que sistema identifica correspondência e retorna resposta do cache em <500ms sem consultar LLM.

### Tests para US2 (obrigatórios)

- [ ] T020 [P] [US2] Escrever testes unitários `apps/backend-fastapi/tests/services/test_cache_service.py` validando carregamento de cache JSON, busca de correspondência, atualização de metadados de uso.
- [ ] T021 [P] [US2] Criar testes de correspondência `apps/backend-fastapi/tests/services/test_question_matcher.py` validando correspondência por keywords, similaridade de texto (Levenshtein/Jaccard), variações de linguagem, falsos positivos <5%.

### Implementação US2

- [ ] T022 [US2] Implementar `CacheService` em `apps/backend-fastapi/src/services/cache_service.py`: classe que carrega `response_cache.json` na inicialização, mantém cache em memória, fornece métodos `load_cache()`, `save_cache()`, `get_entry(question)`, `update_usage(entry_id)`.
- [ ] T023 [US2] Implementar `QuestionMatcher` em `apps/backend-fastapi/src/services/question_matcher.py`: classe com métodos `match(question, cache_entries)` que usa correspondência por keywords primeiro, depois similaridade de texto (Levenshtein ou Jaccard), retorna melhor correspondência com confidence score.
- [ ] T024 [US2] Implementar correspondência por keywords em `apps/backend-fastapi/src/services/question_matcher.py`: método `_match_by_keywords()` que normaliza pergunta e keywords (lowercase, remove acentos opcional), calcula overlap de keywords, retorna correspondência se overlap >70%.
- [ ] T025 [US2] Implementar correspondência por similaridade de texto em `apps/backend-fastapi/src/services/question_matcher.py`: método `_match_by_similarity()` que usa `difflib.SequenceMatcher` ou `python-Levenshtein` para calcular similaridade, retorna correspondência se similaridade >0.8.
- [ ] T026 [US2] Integrar cache no fluxo de chat em `apps/backend-fastapi/src/api/routes/chat.py`: modificar `generate()` para buscar no cache antes de consultar LLM, se encontrado executar SQL correspondente para dados atualizados, retornar resposta do cache com indicação de origem.
- [ ] T027 [US2] Implementar execução de SQL do cache em `apps/backend-fastapi/src/api/routes/chat.py`: quando cache entry encontrada, executar `sql` correspondente usando `db.execute_query()`, preencher `response_template` com resultados, incluir flag `from_cache=True` na resposta.
- [ ] T028 [US2] Atualizar metadados de uso do cache em `apps/backend-fastapi/src/services/cache_service.py`: método `increment_usage(entry_id)` que atualiza `last_used`, incrementa `usage_count`, persiste alterações em `response_cache.json` de forma atômica (write temp + rename).
- [ ] T029 [P] [US2] Criar endpoint de busca de correspondência em `apps/backend-fastapi/src/api/routes/chat.py` ou novo arquivo `cache.py`: `POST /v1/cache/match` que recebe pergunta e retorna correspondência encontrada com confidence conforme contracts/api.yaml.
- [ ] T030 [P] [US2] Criar endpoint de estatísticas do cache em `apps/backend-fastapi/src/api/routes/cache.py`: `GET /v1/cache/stats` retornando total_entries, cache_hit_rate, total_requests, cache_size_bytes conforme contracts/api.yaml.

---

## Phase 5: User Story 3 - Geração Automática de Cache com Validação (Priority: P2)

**Goal**: Sistema gera automaticamente novas entradas de cache quando recebe perguntas novas, validando que resposta está correta antes de adicionar ao cache.  
**Independent Test**: Fazer pergunta nova quando LLM disponível, verificar que sistema gera SQL correto, executa consulta, valida resultados (SQL válido, não vazio, formato correto), adiciona ao cache apenas se validação passar, inclui metadados completos.

### Tests para US3 (obrigatórios)

- [ ] T031 [P] [US3] Escrever testes de validação `apps/backend-fastapi/tests/services/test_cache_validation.py` validando validação de SQL, validação de resultados não vazios, validação de formato de resposta, rejeição de entradas inválidas.
- [ ] T032 [P] [US3] Criar testes de geração automática `apps/backend-fastapi/tests/services/test_cache_generation.py` validando criação de entrada após validação bem-sucedida, inclusão de metadados, persistência em JSON.

### Implementação US3

- [ ] T033 [US3] Implementar validador de respostas em `apps/backend-fastapi/src/services/cache_service.py`: classe `ResponseValidator` com métodos `validate_sql(sql)`, `validate_results(results, expected_not_empty)`, `validate_response_format(response)`, retorna `ValidationResult` com status e confidence_score.
- [ ] T034 [US3] Implementar validação de SQL em `apps/backend-fastapi/src/services/cache_service.py`: método `_validate_sql()` que verifica sintaxe básica (começa com SELECT, não contém comandos perigosos), executa query de teste, captura erros, retorna `sql_valid` e `sql_error`.
- [ ] T035 [US3] Implementar validação de resultados em `apps/backend-fastapi/src/services/cache_service.py`: método `_validate_results()` que verifica se resultados não estão vazios quando esperado, valida formato (números, datas), retorna `results_not_empty` e `response_errors`.
- [ ] T036 [US3] Implementar validação de formato de resposta em `apps/backend-fastapi/src/services/cache_service.py`: método `_validate_response_format()` que verifica resposta não está vazia, tem formato consistente, não contém erros óbvios, retorna `response_format_valid`.
- [ ] T037 [US3] Implementar cálculo de confidence score em `apps/backend-fastapi/src/services/cache_service.py`: método `_calculate_confidence()` que combina resultados das validações (SQL válido=0.4, resultados não vazios=0.3, formato válido=0.3), retorna score 0.0-1.0.
- [ ] T038 [US3] Integrar geração automática no fluxo de chat em `apps/backend-fastapi/src/api/routes/chat.py`: após LLM gerar resposta válida, executar validação completa, se passar criar `CacheEntry` com pergunta original, SQL gerado, resposta, metadados, adicionar ao cache.
- [ ] T039 [US3] Implementar identificação de variações em `apps/backend-fastapi/src/services/question_matcher.py`: método `identify_variations(question)` que extrai keywords principais, gera variações comuns (ex: "taxa de ocupação" → "ocupação", "taxa"), adiciona à entrada de cache.
- [ ] T040 [US3] Persistir nova entrada no cache em `apps/backend-fastapi/src/services/cache_service.py`: método `add_entry(cache_entry)` que valida entrada, gera UUID, adiciona à lista em memória, persiste em `response_cache.json` de forma atômica, atualiza `last_updated`.
- [ ] T041 [US3] Implementar logging de falhas de validação em `apps/backend-fastapi/src/services/cache_service.py`: quando validação falha, registrar evento com `ValidationResult` completo, pergunta original, SQL gerado, razões da falha para revisão manual posterior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Melhorias finais, otimizações e funcionalidades complementares.

- [ ] T042 Implementar estratégia de limpeza do cache em `apps/backend-fastapi/src/services/cache_service.py`: método `cleanup_cache()` que verifica tamanho do arquivo, se >10MB remove entradas antigas (última uso >30 dias) ou menos usadas (usage_count <3), mantém pelo menos 50 entradas mais usadas.
- [ ] T043 Implementar suporte a templates de perguntas em `apps/backend-fastapi/src/services/question_matcher.py`: método `match_template(question)` que identifica placeholders como [SETOR], [ESPECIALIDADE], preenche com valores extraídos da pergunta, busca template correspondente no cache.
- [ ] T044 Adicionar flag `requires_realtime` no fluxo de cache em `apps/backend-fastapi/src/api/routes/chat.py`: quando entrada tem `requires_realtime=True`, sempre executar SQL mesmo usando cache, indicar claramente que dados podem estar desatualizados se SQL falhar.
- [ ] T045 Implementar backup automático do cache em `apps/backend-fastapi/src/services/cache_service.py`: antes de cada atualização, criar backup com timestamp `response_cache.json.backup.YYYYMMDDHHMMSS`, manter últimos 5 backups, limpar backups antigos.
- [ ] T046 Adicionar endpoints de gerenciamento de cache em `apps/backend-fastapi/src/api/routes/cache.py`: `GET /v1/cache/entries` (listar), `POST /v1/cache/entries` (adicionar manual), `GET /v1/cache/entries/{entry_id}` (detalhes), `DELETE /v1/cache/entries/{entry_id}` (remover) conforme contracts/api.yaml.
- [ ] T047 Implementar monitoramento de limites de APIs em `apps/backend-fastapi/src/services/llm_service.py`: rastrear uso diário/mensal por provedor, alertar quando próximo do limite (ex: 80% usado), rotacionar automaticamente para outro provedor quando limite atingido.
- [ ] T048 Adicionar documentação de uso em `apps/backend-fastapi/README.md`: seção explicando como configurar múltiplas APIs, como funciona fallback, como adicionar perguntas ao cache manualmente, como monitorar uso.
- [ ] T049 Criar script de migração de cache para PostgreSQL (opcional) em `apps/backend-fastapi/scripts/migrate_cache_to_db.py`: lê `response_cache.json`, cria tabela `response_cache` se não existir, importa entradas, valida integridade.

---

## Dependencies & Execution Order

### Story Dependencies

- **US1** pode ser implementada independentemente (não requer cache)
- **US2** requer US1 parcialmente (precisa de LLMService para fallback quando cache não encontra)
- **US3** requer US2 (precisa de cache funcionando para adicionar entradas)

### Recommended Execution Order

1. **MVP**: US1 completo → Sistema funcional com fallback de APIs
2. **MVP+**: US1 + US2 → Sistema funcional com cache básico
3. **Completo**: US1 + US2 + US3 → Sistema completo com geração automática

### Parallel Opportunities

- T005, T006, T007 podem ser feitos em paralelo (modelos independentes)
- T009, T010 podem ser feitos em paralelo (testes diferentes)
- T020, T021 podem ser feitos em paralelo (testes diferentes)
- T022, T023 podem ser feitos em paralelo (serviços independentes)
- T024, T025 podem ser feitos em paralelo (métodos diferentes)
- T031, T032 podem ser feitos em paralelo (testes diferentes)
- T033, T034, T035, T036 podem ser feitos em paralelo (métodos de validação independentes)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Fase 1 MVP**: Implementar apenas US1 (Fallback de APIs)
- T001-T004 (Setup)
- T005-T008 (Foundational)
- T009-T019 (US1 completo)

**Resultado**: Sistema continua funcionando mesmo quando OpenAI está indisponível, alternando entre APIs gratuitas configuradas.

### Incremental Delivery

1. **Iteração 1**: US1 (Fallback) - 2-3 dias
2. **Iteração 2**: US2 (Cache básico) - 2-3 dias  
3. **Iteração 3**: US3 (Geração automática) - 2-3 dias
4. **Iteração 4**: Polish & Otimizações - 1-2 dias

**Total estimado**: 7-11 dias de desenvolvimento

---

## Task Summary

- **Total Tasks**: 49
- **Setup Tasks**: 4 (T001-T004)
- **Foundational Tasks**: 4 (T005-T008)
- **US1 Tasks**: 11 (T009-T019)
- **US2 Tasks**: 9 (T020-T030)
- **US3 Tasks**: 11 (T031-T041)
- **Polish Tasks**: 8 (T042-T049)
- **Parallel Opportunities**: 15+ tarefas podem ser executadas em paralelo

## Independent Test Criteria

- **US1**: Desabilitar OpenAI, fazer pergunta, verificar fallback automático e resposta válida
- **US2**: Criar cache com pergunta exemplo, fazer pergunta similar, verificar resposta do cache em <500ms
- **US3**: Fazer pergunta nova, verificar geração de cache após validação bem-sucedida

