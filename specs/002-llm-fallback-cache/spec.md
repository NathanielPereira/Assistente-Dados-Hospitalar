# Feature Specification: Sistema de Fallback e Cache de Respostas para LLM

**Feature Branch**: `002-llm-fallback-cache`  
**Created**: 2025-01-21  
**Status**: Draft  
**Input**: User description: "Meus creditos com a OPENAI da api acabou, o programa não está respondendo nada, para cada pergunta que voce tem como exemplo, crie um arquivo que o assistente entenda essa pergunta e já saiba qual é a resposta, já que para esse registro ele já tem o resultado correto, e para novas perguntas, ele precisa ter consciencia de saber se a resposta está correta ou não, preciso de un documento que se autogenere com novas perguntas e com respostas CORRETAS imprescindivelmente conforme analise do bot, mas primeiro, organize como fazer para voltar a funcionar com outra api ou de alguma outra forma"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Continuidade de Serviço com Fallback de API (Priority: P1)

Um usuário do sistema precisa continuar recebendo respostas mesmo quando a API principal de LLM (OpenAI) está indisponível ou sem créditos. O sistema deve automaticamente detectar a falha e alternar para uma API alternativa ou usar respostas em cache pré-configuradas.

**Why this priority**: Garante que o sistema continue funcional mesmo quando há problemas com provedores externos, mantendo a disponibilidade do serviço.

**Independent Test**: Desabilitar a chave da API OpenAI e verificar que o sistema automaticamente detecta a falha, tenta APIs alternativas e, se necessário, usa respostas em cache para perguntas conhecidas, retornando respostas válidas sem interrupção do serviço.

**Acceptance Scenarios**:

1. **Given** a API OpenAI está indisponível ou sem créditos, **When** um usuário faz uma pergunta, **Then** o sistema detecta a falha automaticamente, tenta APIs alternativas configuradas (ex: Anthropic Claude, Google Gemini, Ollama local) e retorna resposta válida.
2. **Given** todas as APIs externas estão indisponíveis, **When** um usuário faz uma pergunta que existe no cache de respostas conhecidas, **Then** o sistema retorna a resposta em cache imediatamente com indicação de que é uma resposta pré-configurada.
3. **Given** todas as APIs externas estão indisponíveis, **When** um usuário faz uma pergunta nova que não existe no cache, **Then** o sistema informa que a funcionalidade de IA está temporariamente indisponível e oferece alternativas (ex: consultar SQL Workbench diretamente).

---

### User Story 2 - Cache de Perguntas e Respostas Conhecidas (Priority: P1)

Um administrador precisa configurar respostas pré-definidas para perguntas comuns do sistema, garantindo que essas respostas sejam sempre retornadas corretamente mesmo sem acesso a LLM externo.

**Why this priority**: Permite que o sistema funcione com perguntas frequentes mesmo sem LLM, garantindo respostas corretas e consistentes para casos de uso comuns.

**Independent Test**: Criar um arquivo de configuração com perguntas exemplo (ex: "Qual a taxa de ocupação da UTI pediátrica?") e suas respostas correspondentes, verificar que o sistema identifica a pergunta e retorna a resposta correta sem consultar LLM.

**Acceptance Scenarios**:

1. **Given** existe um arquivo de cache com perguntas e respostas conhecidas, **When** um usuário faz uma pergunta que corresponde a uma entrada no cache (com tolerância a variações de linguagem), **Then** o sistema identifica a correspondência e retorna a resposta do cache imediatamente.
2. **Given** uma pergunta no cache requer execução de SQL, **When** o sistema retorna a resposta do cache, **Then** o SQL correspondente é executado e os dados atualizados são incluídos na resposta.
3. **Given** uma pergunta tem múltiplas variações possíveis, **When** o sistema recebe uma variação, **Then** ele identifica a pergunta base correspondente usando correspondência semântica ou palavras-chave.

---

### User Story 3 - Geração Automática de Cache com Validação (Priority: P2)

O sistema precisa automaticamente gerar novas entradas de cache quando recebe perguntas novas, executando a análise correta e validando que a resposta gerada está correta antes de adicionar ao cache.

**Why this priority**: Permite que o sistema aprenda e expanda seu conhecimento base sem intervenção manual, mas com garantias de qualidade.

**Independent Test**: Fazer uma pergunta nova quando o LLM está disponível, verificar que o sistema gera SQL correto, executa, valida os resultados e adiciona a pergunta/resposta ao cache apenas se a validação passar.

**Acceptance Scenarios**:

1. **Given** o sistema recebe uma pergunta nova e o LLM está disponível, **When** o sistema gera SQL e executa a consulta, **Then** o sistema valida que o SQL retornou resultados válidos e que a resposta faz sentido antes de adicionar ao cache.
2. **Given** o sistema adiciona uma nova entrada ao cache, **When** a entrada é salva, **Then** ela inclui a pergunta original, variações identificadas, SQL executado, resposta gerada e metadados de validação (timestamp, confiança, etc.).
3. **Given** o sistema detecta que uma resposta gerada pode estar incorreta (ex: SQL retorna 0 resultados quando deveria retornar dados), **When** a validação falha, **Then** o sistema não adiciona ao cache e registra o evento para revisão manual.

---

### Edge Cases

- Perguntas que são muito similares mas têm intenções diferentes (ex: "quantos leitos?" vs "quantos leitos disponíveis?") devem ser tratadas como entradas separadas no cache.
- Quando o cache tem uma resposta mas os dados do banco mudaram significativamente, o sistema deve executar o SQL novamente e atualizar a resposta mesmo usando o cache.
- Perguntas com parâmetros dinâmicos (ex: "qual a ocupação da UTI [X]?") devem ser tratadas como templates que podem ser preenchidos com diferentes valores.
- Se o arquivo de cache ficar muito grande (>10MB), o sistema deve implementar estratégia de limpeza (ex: remover entradas antigas ou menos usadas).
- Perguntas que requerem dados em tempo real não devem ser cacheadas, ou o cache deve indicar claramente que os dados podem estar desatualizados.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST detectar automaticamente quando a API OpenAI está indisponível ou sem créditos e alternar para APIs alternativas configuradas (Anthropic Claude, Google Gemini, Ollama local, ou outras).
- **FR-002**: O sistema MUST manter um arquivo de cache (JSON/YAML) com perguntas conhecidas e suas respostas correspondentes, incluindo SQL executado e metadados.
- **FR-003**: O sistema MUST identificar perguntas que correspondem a entradas no cache usando correspondência semântica ou palavras-chave, com tolerância a variações de linguagem.
- **FR-004**: Quando uma pergunta corresponde a uma entrada no cache, o sistema MUST executar o SQL correspondente para obter dados atualizados antes de retornar a resposta.
- **FR-005**: O sistema MUST validar que respostas geradas automaticamente estão corretas antes de adicioná-las ao cache (verificar SQL válido, resultados não vazios quando esperado, formato correto).
- **FR-006**: O sistema MUST gerar automaticamente novas entradas de cache quando recebe perguntas novas e o LLM está disponível, incluindo a pergunta original, SQL gerado, resposta e metadados de validação.
- **FR-007**: O sistema MUST permitir configuração de múltiplas APIs de LLM como fallback, com ordem de prioridade configurável.
- **FR-008**: O sistema MUST indicar claramente quando uma resposta vem do cache vs quando foi gerada em tempo real pelo LLM.
- **FR-009**: O sistema MUST suportar templates de perguntas com parâmetros dinâmicos (ex: "qual a ocupação da UTI [SETOR]?") que podem ser preenchidos com diferentes valores.
- **FR-010**: O sistema MUST implementar estratégia de limpeza do cache quando o arquivo ficar muito grande, removendo entradas antigas ou menos usadas.
- **FR-011**: Perguntas que requerem dados em tempo real MUST ser marcadas no cache como "não cacheável" ou o cache MUST indicar claramente que os dados podem estar desatualizados.

### Key Entities *(include if feature involves data)*

- **CachedQuestion**: Representa uma pergunta conhecida no cache, contendo a pergunta original, variações possíveis, SQL correspondente, resposta esperada e metadados (timestamp, confiança, uso).
- **LLMProvider**: Representa um provedor de LLM configurado, contendo tipo (OpenAI, Anthropic, Google, Ollama), configurações de API, ordem de prioridade e status de disponibilidade.
- **CacheEntry**: Representa uma entrada completa no cache, incluindo pergunta, SQL, resposta, validação e metadados de uso.
- **ValidationResult**: Representa o resultado da validação de uma resposta gerada, contendo status (válido/inválido), razões da validação e nível de confiança.

## Conformidade Constitucional *(preencha obrigatoriamente)*

| Princípio | Evidência nesta especificação |
|-----------|------------------------------|
| Proteção Integral de Dados Clínicos | Cache não armazena dados sensíveis de pacientes, apenas perguntas e respostas agregadas. SQL executado pode conter dados, mas são tratados conforme políticas de mascaramento existentes. |
| Auditoria Automatizada e Rastreamento | Todas as entradas de cache são registradas com timestamp e origem. Uso do cache é auditado para rastreabilidade. |
| Evidências e Testes Dirigindo Entregas | Validação automática de respostas antes de adicionar ao cache garante qualidade. Testes independentes para cada user story. |
| Interoperabilidade Modular Hospitalar | Sistema de fallback permite integração com múltiplos provedores de LLM sem alterar interfaces principais. |
| Observabilidade e Resiliência Operacional | Detecção automática de falhas de API e alternância para fallbacks garante disponibilidade. Métricas de uso do cache e taxa de acerto devem ser observáveis. |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sistema mantém disponibilidade de 99%+ mesmo quando APIs principais estão indisponíveis, usando fallbacks ou cache.
- **SC-002**: 90%+ das perguntas comuns (definidas como perguntas feitas mais de 3 vezes) são respondidas em menos de 500ms usando cache.
- **SC-003**: 95%+ das respostas geradas automaticamente e adicionadas ao cache passam na validação de correção antes de serem salvas.
- **SC-004**: Sistema detecta falhas de API em menos de 2 segundos e alterna para fallback automaticamente sem intervenção manual.
- **SC-005**: Cache suporta pelo menos 100 perguntas conhecidas sem degradação de performance na busca de correspondências.
- **SC-006**: Taxa de falsos positivos na correspondência de perguntas (perguntas diferentes identificadas como iguais) é menor que 5%.

## Assumptions

- APIs alternativas (Anthropic, Google Gemini, Ollama) estarão disponíveis ou podem ser configuradas pelo usuário.
- Perguntas comuns podem ser identificadas através de análise de histórico de uso ou configuração manual inicial.
- Validação de respostas pode ser feita através de verificação de SQL válido, resultados não vazios quando esperado, e formato de resposta consistente.
- Cache pode ser armazenado em arquivo JSON/YAML local ou em banco de dados, dependendo da implementação.
- Sistema existente já possui mecanismo de execução de SQL e geração de respostas que pode ser reutilizado.

## Dependencies

- Sistema de execução de SQL existente (já implementado)
- Sistema de geração de respostas existente (já implementado)
- Configuração de variáveis de ambiente para múltiplas APIs de LLM
- Biblioteca para correspondência semântica ou processamento de linguagem natural para identificar perguntas similares

## Out of Scope

- Implementação de modelos de LLM próprios (sistema usa APIs externas ou Ollama local)
- Sistema de aprendizado de máquina avançado para melhorar correspondência de perguntas (usa correspondência simples ou semântica básica)
- Interface de administração para gerenciar cache manualmente (pode ser adicionado em iterações futuras)
- Sistema de versionamento de cache (entradas são atualizadas, não versionadas)

