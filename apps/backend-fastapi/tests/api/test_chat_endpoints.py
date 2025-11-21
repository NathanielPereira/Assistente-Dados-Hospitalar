import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_create_chat_session():
    """Contrato: POST /v1/chat/sessions deve criar sessão e retornar ID."""
    response = client.post("/v1/chat/sessions", json={"user_id": "test-user"})
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert "created_at" in data


def test_stream_chat_response():
    """Contrato: POST /v1/chat/stream deve retornar SSE com chunks."""
    # Primeiro cria sessão
    session_resp = client.post("/v1/chat/sessions", json={"user_id": "test-user"})
    session_id = session_resp.json()["session_id"]
    
    # Depois testa stream
    response = client.post(
        f"/v1/chat/stream",
        json={"session_id": session_id, "prompt": "teste"},
        headers={"Accept": "text/event-stream"}
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
