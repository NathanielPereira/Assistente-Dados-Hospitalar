# 🏥 Assistente de Dados Hospitalar - Explicação Completa

## O que é este projeto?

Um **assistente inteligente de dados** desenvolvido para hospitais que combina:
- **Inteligência Artificial** (LangChain + SQLAgent)
- **Acesso a dados estruturados** (PostgreSQL/NeonDB)
- **Busca em documentos** (RAG - Retrieval Augmented Generation)
- **Compliance total** (LGPD/HIPAA)

## 🎯 Problema que resolve

Em hospitais, profissionais precisam de informações que estão espalhadas:
- Dados estruturados no banco (leitos, estoque, atendimentos)
- Documentos e protocolos (PDFs, manuais, diretrizes)
- Relatórios e análises

**Antes:** Profissionais precisavam:
- Saber SQL para consultar o banco
- Saber onde estão os documentos
- Combinar informações manualmente
- Perder tempo em tarefas repetitivas

**Agora:** Profissionais podem:
- Fazer perguntas em português: *"Qual a taxa de ocupação da UTI pediátrica e qual protocolo aplicar?"*
- Receber resposta combinando dados + documentos automaticamente
- Ver o SQL executado e documentos citados (transparência total)
- Tudo rastreado para auditoria

## 💡 Funcionalidades Principais

### 1. 💬 Chat Clínico Unificado (US1)

**Para quem:** Consultores clínicos, médicos, enfermeiros

**O que faz:**
- Você faz uma pergunta em português
- Sistema busca no banco de dados (via SQL gerado automaticamente)
- Sistema busca em documentos relevantes (via RAG)
- Combina tudo e responde em tempo real com streaming
- Mostra SQL executado e cita documentos (para você verificar)

**Exemplo:**
```
Você: "Qual a taxa de ocupação da UTI pediátrica e qual protocolo aplicar?"

Sistema:
- Busca no banco: SELECT COUNT(*) FROM leitos WHERE setor = 'UTI_PEDIATRICA'
- Busca documentos: protocolo-uti-pediatrica-v2.1.pdf
- Responde: "A UTI pediátrica está com 85% de ocupação. O protocolo X deve ser aplicado..."
- Mostra SQL executado e link para o documento
```

### 2. 🔧 SQL Workbench Assistido (US2)

**Para quem:** Analistas de dados, gestores, equipe de TI

**O que faz:**
- Você descreve o que quer em português
- Sistema sugere SQL automaticamente (comentado e explicado)
- Você pode editar antes de executar
- Sistema executa e gera resumo textual dos resultados
- Tudo rastreado para auditoria

**Exemplo:**
```
Você: "calcular receita média por especialidade"

Sistema sugere:
-- Calcula receita média por especialidade
SELECT e.nome, AVG(a.valor) as receita_media
FROM especialidades e
JOIN atendimentos a ON a.especialidade_id = e.id
GROUP BY e.id, e.nome;

Você revisa, aprova e executa.
Sistema retorna resultados + resumo: "15 especialidades encontradas, receita média de R$ 1.234,56"
```

### 3. 📋 Painel de Compliance (US3)

**Para quem:** Oficiais de compliance, auditores, DPO (Data Protection Officer)

**O que faz:**
- Visualiza todas as interações do sistema
- Filtra por usuário, período, tipo de ação
- Exporta trilhas de auditoria em CSV/JSON
- Verifica bases legais (LGPD/HIPAA)
- Rastreia quem acessou o quê e quando

**Por que é importante:**
- Hospitais são obrigados a manter trilhas de auditoria
- LGPD exige rastreabilidade de acesso a dados pessoais
- HIPAA (EUA) exige logs imutáveis
- Este painel permite exportar tudo para auditorias externas

### 4. 📊 Observability Control Room (US3)

**Para quem:** Equipe de TI, SRE (Site Reliability Engineering)

**O que faz:**
- Monitora saúde do sistema em tempo real
- Mostra uptime, latência, status das integrações
- Detecta falhas e ativa modo degradado automaticamente
- Gera alertas quando algo está errado

**Por que é importante:**
- Em hospitais, sistema não pode ficar offline
- Precisa detectar problemas antes que afetem usuários
- Modo degradado permite continuar operando mesmo com falhas parciais

## 🔒 Segurança e Compliance

### Proteção de Dados
- ✅ Criptografia ponta a ponta (AES-256 + TLS 1.3)
- ✅ Mascaramento automático de dados sensíveis (CPF, RG, etc)
- ✅ Bloqueio de tentativas de identificar pacientes específicos
- ✅ Camadas de dados segregadas (bronze/prata/ouro)

### Auditoria
- ✅ Todas as interações geram logs imutáveis
- ✅ Hashes verificáveis de entrada/saída
- ✅ Exportos em CSV/JSON para auditorias externas
- ✅ Retenção de 2 anos (conforme LGPD)

### Observabilidade
- ✅ Métricas SLO (Service Level Objectives)
- ✅ Alertas automáticos
- ✅ Modo degradado em caso de falhas
- ✅ Playbooks de recuperação

## 🛠️ Tecnologias

### Frontend
- **Next.js 14** - Framework React com App Router
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Estilização

### Backend
- **FastAPI** - Framework Python moderno e rápido
- **LangChain** - Framework para aplicações com LLM
- **SQLAgent** - Agente que gera e executa SQL automaticamente
- **RAG** - Retrieval Augmented Generation (busca em documentos)

### Infraestrutura
- **NeonDB** - PostgreSQL serverless
- **S3** - Armazenamento de documentos
- **Redis** - Cache e sessões
- **Vercel** - Hospedagem frontend
- **Render** - Hospedagem backend

## 📊 Arquitetura

```
┌─────────────────┐
│   Frontend      │  Next.js (Vercel)
│   (Next.js)     │  └─ Chat UI
│                 │  └─ SQL Workbench
│                 │  └─ Compliance Panel
│                 │  └─ Observability
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│   Backend       │  FastAPI (Render)
│   (Python)      │  └─ LangChain SQLAgent
│                 │  └─ RAG Pipeline
│                 │  └─ Audit Logger
│                 │  └─ Compliance API
└────────┬────────┘
         │
    ┌────┴────┬──────────┬────────┐
    │         │          │        │
┌───▼───┐ ┌──▼──┐  ┌────▼───┐ ┌─▼──┐
│NeonDB │ │ S3  │  │ Redis  │ │LLM │
│(SQL)  │ │(Docs)│  │(Cache) │ │API │
└───────┘ └─────┘  └────────┘ └────┘
```

## 🚀 Como usar

### 1. Chat Clínico
1. Acesse `/chat`
2. Digite sua pergunta em português
3. Receba resposta em tempo real
4. Veja SQL executado e documentos citados

### 2. SQL Workbench
1. Acesse `/sql-workbench`
2. Descreva o que você quer consultar
3. Revise o SQL sugerido
4. Aprove e execute
5. Veja resultados e resumo

### 3. Compliance
1. Acesse `/compliance`
2. Filtre por usuário/período
3. Visualize todas as interações
4. Exporte em CSV/JSON

### 4. Observability
1. Acesse `/observability`
2. Veja métricas em tempo real
3. Monitore saúde do sistema
4. Verifique status das integrações

## ⚠️ Importante

- **Dados fictícios:** Este projeto usa apenas dados sintéticos para demonstração
- **Não é produção:** É um MVP demonstrativo das capacidades técnicas
- **Compliance real:** Em produção, precisaria de validações adicionais

## 📚 Documentação Técnica

- [Especificação Completa](specs/001-hospital-data-agent/spec.md)
- [Plano de Implementação](specs/001-hospital-data-agent/plan.md)
- [Tarefas](specs/001-hospital-data-agent/tasks.md)
- [Guia de Testes](TESTING.md)
- [Setup](SETUP.md)

