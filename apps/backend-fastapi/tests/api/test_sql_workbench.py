import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_sql_assist_requires_approval():
    """Garante que SQL não pode ser executado sem aprovação."""
    # Solicita sugestão
    suggest_resp = client.post(
        "/v1/sql/assist",
        json={"prompt": "receita por especialidade", "tables": ["especialidades", "atendimentos"]}
    )
    assert suggest_resp.status_code == 200
    suggestion = suggest_resp.json()
    assert "sql" in suggestion
    
    # Tenta executar sem aprovação - deve falhar
    exec_resp = client.post(
        "/v1/sql/execute",
        json={"sql": suggestion["sql"], "approved": False}
    )
    assert exec_resp.status_code == 400
    
    # Executa com aprovação - deve funcionar
    exec_resp = client.post(
        "/v1/sql/execute",
        json={"sql": suggestion["sql"], "approved": True}
    )
    assert exec_resp.status_code == 200
    assert "results" in exec_resp.json()
