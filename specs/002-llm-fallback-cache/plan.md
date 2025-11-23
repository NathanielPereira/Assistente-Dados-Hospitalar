# Implementation Plan: Sistema de Fallback e Cache de Respostas para LLM

**Branch**: `002-llm-fallback-cache` | **Date**: 2025-01-21 | **Spec**: [specs/002-llm-fallback-cache/spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-llm-fallback-cache/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementar sistema de fallback de APIs de LLM gratuitas e cache de respostas conhecidas para garantir continuidade de serviço e maximizar número de perguntas por mês. O sistema deve detectar automaticamente falhas, alternar entre múltiplos provedores gratuitos (Google Gemini, Anthropic Claude, Hugging Face, OpenRouter), rotacionar requisições para distribuir limites gratuitos, manter cache de perguntas/respostas conhecidas e gerar automaticamente novas entradas de cache com validação. Entrega resiliência operacional, reduz dependência de APIs pagas e maximiza uso de limites gratuitos disponíveis.

## Technical Context

**Language/Version**: Python 3.11 (backend FastAPI), mantendo compatibilidade com LangChain 1.0  
**Primary Dependencies**: LangChain (suporte multi-provider), langchain-google-genai (prioridade 1), langchain-anthropic (prioridade 2), langchain-huggingface (prioridade 3), langchain-openai para OpenRouter (prioridade 4), FastAPI, pydantic para validação, SQLAlchemy/psycopg3 para persistência de cache  
**Storage**: Arquivo JSON/YAML para cache inicial, opcionalmente PostgreSQL (tabela `response_cache`) para cache persistente, mantendo NeonDB existente  
**Testing**: pytest + pytest-asyncio, testes de integração para fallback de APIs, testes unitários para correspondência de perguntas  
**Target Platform**: Backend FastAPI em Render Standard (Docker), compatível com ambiente local Windows dev  
**Project Type**: Extensão do backend FastAPI existente, módulo de fallback e cache  
**Performance Goals**: Detecção de falha de API <2s, resposta de cache <500ms, busca de correspondência <100ms para até 100 perguntas  
**Constraints**: Manter compatibilidade com código existente, não quebrar funcionalidades atuais, suportar múltiplas APIs sem aumentar significativamente dependências, cache deve ser opcional (sistema funciona sem cache)  
**Scale/Scope**: Suportar até 100 perguntas em cache inicialmente, 4 provedores de LLM gratuitos configuráveis (Google Gemini, Anthropic, Hugging Face, OpenRouter), cache pode crescer até 10MB antes de limpeza automática. Sistema deve rotacionar entre provedores para maximizar uso de limites gratuitos (estimativa: ~2000-5000 perguntas/mês combinando todos os provedores)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Proteção Integral de Dados Clínicos**: Cache não armazena dados sensíveis de pacientes diretamente, apenas perguntas e respostas agregadas. SQL executado pode conter dados, mas são tratados conforme políticas de mascaramento existentes. Cache é criptografado em repouso (AES-256) se armazenado em banco. ✅
- **Auditoria Automatizada e Rastreamento**: Todas as entradas de cache são registradas com timestamp, origem (LLM usado, cache, fallback), e uso é auditado. Uso do cache vs LLM é rastreável. ✅
- **Evidências e Testes Dirigindo Entregas**: Validação automática de respostas antes de adicionar ao cache garante qualidade. Testes independentes para cada user story, incluindo testes de fallback e correspondência de perguntas. ✅
- **Interoperabilidade Modular**: Sistema de fallback permite integração com múltiplos provedores de LLM sem alterar interfaces principais. Cache é um módulo isolado que pode ser desabilitado. ✅
- **Observabilidade e Resiliência Operacional**: Detecção automática de falhas de API e alternância para fallbacks garante disponibilidade. Métricas de uso do cache, taxa de acerto, e status de cada provedor de LLM devem ser observáveis. ✅

## Project Structure

### Documentation (this feature)

```text
specs/002-llm-fallback-cache/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
apps/backend-fastapi/
├── src/services/
│   ├── llm_service.py           # Modificado: suporte multi-provider + fallback
│   ├── cache_service.py          # Novo: gerenciamento de cache de respostas
│   └── question_matcher.py       # Novo: correspondência semântica de perguntas
├── src/domain/
│   ├── llm_provider.py           # Novo: abstração de provedor de LLM
│   └── cache_entry.py            # Novo: modelo de entrada de cache
├── src/api/routes/
│   └── chat.py                   # Modificado: integração com cache e fallback
├── data/
│   └── response_cache.json       # Novo: arquivo de cache inicial (exemplos)
└── tests/
    ├── test_llm_fallback.py     # Novo: testes de fallback
    ├── test_cache_service.py     # Novo: testes de cache
    └── test_question_matcher.py # Novo: testes de correspondência
```

**Structure Decision**: Extensão modular do backend existente. Novo serviço `cache_service.py` gerencia cache isoladamente. `llm_service.py` é estendido para suportar múltiplos provedores com fallback automático. `question_matcher.py` fornece correspondência semântica simples. Cache inicial em JSON para facilitar configuração manual, com opção de migrar para PostgreSQL se necessário.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

