import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_export_audit_csv():
    """Testa exportação de auditoria em formato CSV."""
    response = client.get(
        "/v1/audit/exports",
        params={"session_id": "test-session", "format": "csv", "days": 7}
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    assert "session_id" in response.text


def test_export_audit_json():
    """Testa exportação de auditoria em formato JSON."""
    response = client.get(
        "/v1/audit/exports",
        params={"session_id": "test-session", "format": "json", "days": 7}
    )
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")
    data = response.json()
    assert "audit_entries" in data


def test_export_with_filters():
    """Testa exportação com filtros de usuário e período."""
    response = client.get(
        "/v1/audit/exports",
        params={
            "user_id": "user-123",
            "format": "json",
            "start_date": "2025-11-01",
            "end_date": "2025-11-20"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["audit_entries"], list)
