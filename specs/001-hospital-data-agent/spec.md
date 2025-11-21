# Feature Specification: Assistente de Dados Hospitalar IA

**Feature Branch**: `001-hospital-data-agent`  
**Created**: 2025-11-20  
**Status**: Draft  
**Input**: User description: "Assistente de Dados para Hospitais com LangChain SQLAgent + RAG, Next.js (frontend streaming no Vercel), FastAPI (Render), PostgreSQL NeonDB, conectores para documentos fictícios hospitalares, compliance LGPD/HIPAA, observabilidade obrigatória, demostrar SQL avançado e arquitetura híbrida Node+Python"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Consulta Clínica Unificada (Priority: P1)

Um consultor clínico precisa obter respostas em linguagem natural combinando dados estruturados do hospital (ex.: leitos, estoque, indicadores) com conhecimento contextual de protocolos e documentos internos fictícios. Ele interage via chat e recebe respostas com streaming, trechos citados e SQL executado para auditoria.

**Why this priority**: Entrega o MVP que demonstra valor imediato: transformar dados dispersos em decisões clínicas rápidas e rastreáveis.

**Independent Test**: Simular consulta sobre disponibilidade de leitos e diretrizes de isolamento; validar que o chat responde em tempo real, mostra SQL executado e cita documentos relevantes sem depender de outras histórias.

**Acceptance Scenarios**:

1. **Given** o consultor acessa o chat autenticado, **When** pergunta “Qual taxa de ocupação da UTI pediátrica e qual protocolo aplicar?”, **Then** o sistema streama resposta com percentual atual calculado via SQL e links para o protocolo correspondente.
2. **Given** a pergunta requer múltiplas fontes, **When** a resposta é exibida, **Then** o painel mostra os trechos dos documentos consultados e o SQL utilizado, permitindo auditoria.

---

### User Story 2 - Analista SQL com Assistência Inteligente (Priority: P2)

Analistas de dados precisam escrever consultas SQL complexas sobre o PostgreSQL operacional, com ajuda para entender o esquema, validar sintaxe e receber interpretação textual dos resultados, mantendo controle manual antes de executar.

**Why this priority**: Demonstra a profundidade técnica em SQL avançado e LangChain, permitindo usos além de perguntas em linguagem natural.

**Independent Test**: Carregar uma solicitação de dashboard financeiro, gerar sugestões de SQL, editar manualmente e rodar com pré-visualização dos resultados e diagnóstico automático.

**Acceptance Scenarios**:

1. **Given** o analista seleciona tabelas relevantes, **When** pede sugestões para calcular receita média por especialidade, **Then** recebe uma consulta comentada e pode aprovar/ajustar antes da execução.
2. **Given** o analista executa o SQL aprovado, **When** os resultados retornam, **Then** o sistema gera resumos em linguagem natural, salva o SQL e inclui o hash da execução na trilha de auditoria.

---

### User Story 3 - Oficial de Compliance e Operações Confiáveis (Priority: P3)

Um responsável por compliance precisa verificar se consultas e respostas do agente seguem LGPD/HIPAA, permanecem observáveis e podem ser reproduzidas em auditorias externas, inclusive por meio de um painel dedicado de observabilidade operacional.

**Why this priority**: Sustenta confiança institucional, garante atendimento aos princípios de proteção de dados, auditoria e observabilidade.

**Independent Test**: Solicitar histórico de interações dos últimos 7 dias, verificar criptografia de campos sensíveis e simular incidente com relatório automático contendo métricas de disponibilidade e alertas.

**Acceptance Scenarios**:

1. **Given** o oficial acessa o painel de conformidade, **When** filtra eventos por usuário e período, **Then** obtém logs imutáveis com IDs das execuções, SQL utilizado e justificativa legal de tratamento de dados.
2. **Given** ocorre falha simulada em consultas externas, **When** o modo de degradação é acionado, **Then** o painel mostra alertas, métricas SLO e recomendações do playbook com carimbos de tempo para auditoria.
3. **Given** o time de operação abre o Painel de Observabilidade, **When** consulta o ambiente de demonstração, **Then** enxerga uptime, latência p95 e status de cada integração (chat, SQL, RAG) com indicação visual caso algum circuito esteja degradado.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Perguntas que referenciam pacientes específicos devem ser bloqueadas e substituídas por orientação genérica, registrando o evento como tentativa proibida.
- Se o banco NeonDB estiver indisponível, o agente precisa comunicar indisponibilidade, operar apenas com cache/knowledge base e disparar alerta para SRE.
- Quando documentos RAG possuem informações conflitantes, o agente deve citar ambas as fontes e apontar o conflito em vez de escolher arbitrariamente.
- Consultas SQL que retornam volumes acima do limite seguro (ex.: >10k linhas) exigem confirmação explícita e paginação automática.
- Solicitações de documentos classificados como “RESTRITO_DEMO” por usuários sem papel autorizado devem ser negadas com mensagem segura e registro de tentativa.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: O agente MUST oferecer chat em linguagem natural com streaming contínuo, citando dados estruturados e fontes documentais em cada resposta.
- **FR-002**: Toda resposta MUST incluir o SQL executado, métricas principais e links para trechos dos documentos consultados.
- **FR-003**: Usuários tipo analista MUST conseguir gerar, revisar e aprovar consultas SQL sugeridas automaticamente antes da execução.
- **FR-004**: O sistema MUST validar permissões e bases legais LGPD/HIPAA para cada pergunta, bloqueando tentativas de identificar pacientes.
- **FR-005**: Logs de auditoria MUST registrar ID da execução, hash da entrada, hash do resultado, usuário e justificativa de tratamento.
- **FR-006**: A plataforma MUST manter camadas distintas de dados (bronze/prata/ouro) com tabelas físicas separadas, chaves de criptografia AES-256 por camada, TLS 1.3 em todo tráfego e validações automáticas de mascaramento via Great Expectations.
- **FR-007**: Em caso de falha externa, o agente MUST entrar em modo degradado read-only e notificar operadores com alertas e métricas SLO.
- **FR-008**: Cada interação MUST gerar relatórios exportáveis (CSV/JSON) com perguntas, evidências e indicadores, permitindo demonstrações.
- **FR-009**: O sistema MUST expor um painel dedicado de observabilidade (UI independente) exibindo uptime em tempo real, latência p95, taxa de sucesso de cada integração (chat, SQL, RAG, exports) e status do modo degradado para cada ambiente.
- **FR-010**: Bases documentais fictícias MUST ser catalogadas com metadados obrigatórios (origem, versão, data, classificação de sigilo, proprietário) e políticas de acesso por papel (consultor, analista, compliance) auditáveis.

### Key Entities *(include if feature involves data)*

- **QuerySession**: Representa cada interação de chat e/ou execução SQL; armazena pergunta, SQL aprovado, resultados resumidos, IDs de auditoria, status de modo degradado.
- **DocumentCorpus**: Coleção versionada de documentos hospitalares fictícios com metadados (tipo, sigilo, fonte, hash, proprietário, versão) usados pelo mecanismo RAG e vinculados a políticas de acesso baseadas em papéis.
- **AuditEntry**: Registro imutável com timestamp, usuário, base legal, hashes de entrada/saída e links para QuerySession e DocumentCorpus utilizados.
- **DataConnectivityProfile**: Configurações aprovadas para acessar bancos NeonDB (credenciais segregadas, escopo de tabelas, SLAs), incluindo políticas de cache.
- **ObservabilitySnapshot**: Representa a coleta das métricas expostas no painel (uptime, latência p95, taxa de sucesso e status de circuit breaker) com histórico para cada ambiente.

## Conformidade Constitucional *(preencha obrigatoriamente)*

| Princípio | Evidência nesta especificação |
|-----------|------------------------------|
| Proteção Integral de Dados Clínicos | FR-004, FR-006 e Edge Cases definem bloqueios a PII, criptografia ponta a ponta e justificativas LGPD/HIPAA. |
| Auditoria Automatizada e Rastreamento | FR-002, FR-005, Key Entities (AuditEntry) e histórias 2/3 exigem trilhas imutáveis com hashes e exportações. |
| Evidências e Testes Dirigindo Entregas | User Stories requerem datasets de referência (SQL + documentos), FR-003/FR-008 exigem validação e relatórios repetíveis. |
| Interoperabilidade Modular Hospitalar | FR-001, FR-009 e Story 2 determinam contratos claros entre chat, SQL e conectores de dados/documentos versionados. |
| Observabilidade e Resiliência Operacional | FR-007, FR-009 e Story 3 definem SLOs, alertas, modo degradado, painel dedicado e playbooks de recuperação auditáveis. |

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 90% das perguntas P1 recebem primeira sentença em ≤2 s e resposta completa em ≤8 s com citações e SQL exibidos.
- **SC-002**: Analistas aprovam/ajustam consultas sugeridas em ≤3 iterações, reduzindo em 50% o tempo médio para gerar relatórios complexos.
- **SC-003**: 100% das interações registram auditoria exportável (CSV/JSON) com hash verificável e justificativa legal em até 30 s após execução.
- **SC-004**: Painel de observabilidade mantém disponibilidade ≥99% e latência p95 <2 s para leituras de dados em ambiente demonstrativo durante testes.

## Assumptions & Dependencies

- Bases hospitalares e documentos utilizados são fictícios ou anonimizados, autorizados para demonstração pública.
- Usuários já contam com autenticação corporativa existente; este projeto apenas consome tokens de sessão validados.
- Ambientes de hospedagem (Vercel, Render, NeonDB, camada gratuita AWS) estão aprovados para dados fictícios e seguem limites de uso definidos.
