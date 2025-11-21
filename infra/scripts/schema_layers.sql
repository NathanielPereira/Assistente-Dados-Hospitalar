-- Estruturas físicas bronze/prata/ouro
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS prata;
CREATE SCHEMA IF NOT EXISTS ouro;

-- Schema público para tabelas principais
CREATE SCHEMA IF NOT EXISTS public;

-- Tabela de sessões de chat
CREATE TABLE IF NOT EXISTS public.query_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    prompt TEXT,
    response_hash VARCHAR(64)
);

-- Tabela de sessões SQL
CREATE TABLE IF NOT EXISTS public.sql_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    suggested_sql TEXT,
    approved_sql TEXT,
    executed_at TIMESTAMP WITH TIME ZONE,
    result_hash VARCHAR(64),
    audit_entry_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de auditoria
CREATE TABLE IF NOT EXISTS public.audit_entries (
    entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID,
    user_id VARCHAR(255) NOT NULL,
    prompt TEXT,
    sql_executed TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    legal_basis VARCHAR(255),
    input_hash VARCHAR(64),
    output_hash VARCHAR(64)
);

-- Tabela de leitos (dados fictícios)
CREATE TABLE IF NOT EXISTS public.leitos (
    leito_id SERIAL PRIMARY KEY,
    setor VARCHAR(100) NOT NULL,
    numero VARCHAR(20) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'disponivel',
    tipo VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(setor, numero)
);

-- Tabela de especialidades (dados fictícios)
CREATE TABLE IF NOT EXISTS public.especialidades (
    especialidade_id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de atendimentos (dados fictícios)
CREATE TABLE IF NOT EXISTS public.atendimentos (
    atendimento_id SERIAL PRIMARY KEY,
    especialidade_id INTEGER REFERENCES public.especialidades(especialidade_id),
    valor DECIMAL(10, 2),
    data_atendimento DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_query_sessions_user_id ON public.query_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_query_sessions_created_at ON public.query_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_entries_session_id ON public.audit_entries(session_id);
CREATE INDEX IF NOT EXISTS idx_audit_entries_user_id ON public.audit_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_entries_timestamp ON public.audit_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_leitos_setor ON public.leitos(setor);
CREATE INDEX IF NOT EXISTS idx_leitos_status ON public.leitos(status);
CREATE INDEX IF NOT EXISTS idx_atendimentos_especialidade ON public.atendimentos(especialidade_id);

-- Dados fictícios iniciais
INSERT INTO public.especialidades (nome, descricao) VALUES
    ('Cardiologia', 'Especialidade médica focada no coração'),
    ('Pediatria', 'Especialidade médica para crianças'),
    ('Ortopedia', 'Especialidade médica para ossos e articulações'),
    ('Neurologia', 'Especialidade médica para sistema nervoso'),
    ('Oncologia', 'Especialidade médica para tratamento de câncer')
ON CONFLICT (nome) DO NOTHING;

-- Leitos fictícios
INSERT INTO public.leitos (setor, numero, status, tipo) VALUES
    ('UTI_PEDIATRICA', 'UTI-P-01', 'ocupado', 'UTI'),
    ('UTI_PEDIATRICA', 'UTI-P-02', 'ocupado', 'UTI'),
    ('UTI_PEDIATRICA', 'UTI-P-03', 'disponivel', 'UTI'),
    ('UTI_ADULTO', 'UTI-A-01', 'ocupado', 'UTI'),
    ('UTI_ADULTO', 'UTI-A-02', 'disponivel', 'UTI'),
    ('ENFERMARIA', 'ENF-01', 'ocupado', 'ENFERMARIA'),
    ('ENFERMARIA', 'ENF-02', 'ocupado', 'ENFERMARIA'),
    ('ENFERMARIA', 'ENF-03', 'disponivel', 'ENFERMARIA')
ON CONFLICT (setor, numero) DO NOTHING;

-- Atendimentos fictícios
INSERT INTO public.atendimentos (especialidade_id, valor, data_atendimento) VALUES
    (1, 500.00, CURRENT_DATE - INTERVAL '1 day'),
    (1, 600.00, CURRENT_DATE),
    (2, 300.00, CURRENT_DATE - INTERVAL '2 days'),
    (2, 350.00, CURRENT_DATE),
    (3, 800.00, CURRENT_DATE - INTERVAL '1 day'),
    (4, 1200.00, CURRENT_DATE)
ON CONFLICT DO NOTHING;
