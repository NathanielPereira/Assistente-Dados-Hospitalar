<!--
Sync Impact Report
- Version change: 0.0.0 → 1.0.0 (adoção inicial da constituição)
- Princípios modificados: N/A → cinco princípios formais (Proteção de Dados, Auditoria, Evidências/Testes, Interoperabilidade, Observabilidade)
- Seções adicionadas: Padrões Técnicos Essenciais; Fluxo de Desenvolvimento e Qualidade
- Seções removidas: nenhuma
- Templates atualizados: ✅ .specify/templates/plan-template.md | ✅ .specify/templates/spec-template.md | ✅ .specify/templates/tasks-template.md
- Follow-up TODOs: nenhum
-->

# Constituição do Assistente de Dados para Hospitais

## Core Principles

### Princípio I — Proteção Integral de Dados Clínicos
- Todo dado pessoal ou sensível MUST permanecer criptografado em repouso (AES-256/GCM) e em trânsito (TLS 1.3 com mTLS quando possível).
- Pipelines MUST aplicar minimização de dados e mascaramento antes de persistir ou exportar informações.
- Toda feature MUST documentar controles LGPD/HIPAA (base legal, finalidade, retenção) antes de entrar em homologação.
*Racional*: hospitais dependem de confiança; qualquer violação de sigilo inviabiliza o produto.

### Princípio II — Auditoria Automatizada e Rastreamento Fim a Fim
- Cada transformação de dados MUST gerar eventos rastreáveis (ID de execução, hash de entrada/saída, operador).
- Logs de auditoria NÃO podem ser editados; armazenar em storage imutável com retenção ≥ 2 anos.
- Consultas provenientes de usuários finais MUST vincular-se a relatórios auditáveis exportáveis em CSV/JSON.
*Racional*: decisões clínicas e legais exigem trilha completa para contestação e melhoria contínua.

### Princípio III — Evidências e Testes Dirigindo Entregas
- Nenhum código segue para merge sem testes automatizados cobrindo dados sintéticos críticos e cenários reais anonimizados.
- Cada história MUST prover datasets de referência e métricas-alvo antes do desenvolvimento (testes falham primeiro).
- Deploys MUST incluir verificação automática de regressão estatística (drift e precisão) e testes de contrato.
*Racional*: resultados médicos precisam de prova quantitativa; confiança nasce de testes antes de código.

### Princípio IV — Interoperabilidade Modular Hospitalar
- Interfaces MUST ser publicadas como contratos versionados (FHIR/HL7 ou APIs REST JSON) com controle de compatibilidade.
- Serviços expostos devem permanecer modulares; dependências cruzadas exigem adaptadores explícitos e contratos de consumo.
- Toda alteração breaking requer plano de migração com período de convivência ≥ 2 ciclos de release.
*Racional*: hospitais usam ERPs heterogêneos; interoperabilidade previsível reduz riscos operacionais.

### Princípio V — Observabilidade e Resiliência Operacional
- Cada serviço MUST publicar métricas SLO (latência p95, throughput, disponibilidade) e alertas acionáveis.
- Feature flags e circuit breakers são obrigatórios para integrações externas; quedas devem degradar para modo read-only.
- Playbooks de recuperação precisam acompanhar toda entrega, com drills trimestrais documentados.
*Racional*: ambientes clínicos não toleram falhas silenciosas; precisamos detectar, isolar e recuperar rapidamente.

## Padrões Técnicos Essenciais

- Linguagens suportadas: Python ≥3.11 para pipelines e APIs, SQL padrão ANSI para consultas, e infra como código em Terraform.
- Segurança operacional: secrets via cofre central (ex.: Azure Key Vault), rotação automática ≤ 90 dias, MFA em toda automação humana.
- Dados: camadas bronze/prata/ouro obrigatórias com validações de schema (Great Expectations) e anonimização reversível apenas em cofres.
- Performance mínima: consultas interativas p95 < 2 s com até 5k registros; jobs batch precisam finalizar ≤ 30 min com janelas de 15 min de tolerância.
- Deploy: ambientes segregados (dev, homolog, produção) com pipelines GitOps acionados por tags versionadas.

## Fluxo de Desenvolvimento e Qualidade

1. Descoberta rápida documenta hipótese clínica, riscos de dados e critérios de auditoria antes de estimativas.
2. Pesquisa → especificação → plano precisam registrar como cada princípio será atendido; revisões negam entregas sem essa seção.
3. Pull requests exigem checklist automático: privacidade, rastreabilidade, testes, contratos e observabilidade.
4. Cada release inclui runbooks, dashboards e relatórios de auditoria validados; QA multiplica cenários com dados sintéticos seguros.
5. Revisões trimestrais avaliam métricas de SLO/SLA, incidentes e aderência às políticas; ações corretivas viram tarefas priorizadas.

## Governance

- Esta constituição prevalece sobre qualquer guia local; conflitos devem ser resolvidos atualizando este documento.
- Emendas requerem proposta escrita, análise de impacto e aprovação de responsáveis clínico, segurança e engenharia.
- Versionamento segue SemVer: MAJOR para mudanças incompatíveis, MINOR para novos princípios/seções, PATCH para ajustes pontuais.
- Revisões de conformidade ocorrem a cada release; violações bloqueiam deploy até criação de plano corretivo.
- Registros oficiais ficam em `.specify/memory/constitution.md`; agentes devem consultar antes de gerar planos, especificações e tarefas.

**Version**: 1.0.0 | **Ratified**: 2025-11-20 | **Last Amended**: 2025-11-20
