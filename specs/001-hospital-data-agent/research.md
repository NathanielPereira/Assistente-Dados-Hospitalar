# Research — Assistente de Dados Hospitalar IA

## Decisão 1: LangChain SQLAgent + RAG desacoplados
- **Rationale**: SQLAgent lida com consultas NeonDB garantindo visibilidade total do SQL, enquanto pipelines RAG tratam documentos fictícios. Mantemos controles independentes para escalonar e auditar cada fonte.
- **Alternativas consideradas**:
  - **Agente único multimodal**: simplificaria orquestração, porém dificultaria auditoria separada de SQL e textos.
  - **Ferramenta manual (apenas SQL assistido)**: não atende requisito de combinar protocolos/documentos.

## Decisão 2: Híbrido Next.js + FastAPI
- **Rationale**: Next.js 14 oferece streaming e UI responsiva para chat; FastAPI é leve e integra bem com LangChain/Python 3.11, permitindo execução dos agentes perto dos dados.
- **Alternativas consideradas**:
  - **Stack full Python (FastAPI + template)**: reduziria contextos, mas prejudicaria experiência rica em streaming no frontend.
  - **Stack full Node (NestJS)**: complicaria uso de bibliotecas LangChain Python maduras.

## Decisão 3: Hospedagem Vercel / Render / NeonDB / AWS Free Tier
- **Rationale**: atende pedido explícito, cobre requisitos de demonstração e permite segregação de responsabilidades. NeonDB oferece branching fácil para ambientes e criptografia by default.
- **Alternativas consideradas**:
  - **Hospedagem self-hosted**: aumentaria esforço operacional e não aproveita tiers gratuitos.
  - **Um único provedor (ex.: AWS apenas)**: violaria requisito de demonstrar arquitetura híbrida.

## Decisão 4: Observabilidade com métricas/SLO e playbooks
- **Rationale**: Necessário para cumprir princípio de observabilidade; definimos dashboards (Grafana/Edge Config) e alertas Render/Vercel com circuit breakers e modo read-only.
- **Alternativas consideradas**:
  - **Logs apenas**: insuficiente para detectar falhas em tempo real.
  - **Ferramentas proprietárias pagas**: evitadas para manter custos baixos na demonstração.

## Decisão 5: Dados sintéticos e anonimização irreversível
- **Rationale**: Garante compliance LGPD/HIPAA em ambiente de demonstração; simplifica aprovação de uso de nuvem pública.
- **Alternativas consideradas**:
  - **Dados anonimizados reversíveis**: aumentaria risco e exigiria controles extras.
  - **Mock estático (JSON)**: não demonstraria SQL avançado.


