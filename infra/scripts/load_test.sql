-- Testes de carga para validar SLOs
-- Objetivo: verificar que consultas completam em ≤5s para até 10k linhas

-- Teste 1: Consulta simples (deve ser < 1s)
SELECT COUNT(*) FROM pacientes;

-- Teste 2: JOIN médio (deve ser < 2s)
SELECT 
    e.nome,
    COUNT(a.id) as total_atendimentos
FROM especialidades e
LEFT JOIN atendimentos a ON a.especialidade_id = e.id
GROUP BY e.id, e.nome;

-- Teste 3: Agregação complexa (deve ser < 5s)
SELECT 
    DATE_TRUNC('month', a.data_atendimento) as mes,
    COUNT(DISTINCT a.paciente_id) as pacientes_unicos,
    AVG(a.valor) as receita_media
FROM atendimentos a
WHERE a.data_atendimento >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY mes
ORDER BY mes DESC;

-- Teste 4: Volume grande (10k linhas, deve ser < 5s com LIMIT)
SELECT * FROM atendimentos 
ORDER BY data_atendimento DESC 
LIMIT 10000;
