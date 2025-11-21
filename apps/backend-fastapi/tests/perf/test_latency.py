import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_chat_streaming_latency():
    """Valida que streaming inicia em ≤2s (SC-001)."""
    start = time.perf_counter()
    response = client.post(
        "/v1/chat/stream",
        json={"session_id": "test", "prompt": "teste"},
        headers={"Accept": "text/event-stream"}
    )
    first_chunk_time = time.perf_counter() - start
    
    assert first_chunk_time < 2.0, f"Streaming iniciou em {first_chunk_time:.2f}s (meta: <2s)"


def test_sql_execution_latency():
    """Valida que SQL executa em ≤5s para até 10k linhas."""
    start = time.perf_counter()
    response = client.post(
        "/v1/sql/execute",
        json={"sql": "SELECT * FROM atendimentos LIMIT 10000", "approved": True}
    )
    execution_time = time.perf_counter() - start
    
    assert execution_time < 5.0, f"SQL executou em {execution_time:.2f}s (meta: <5s)"


def test_audit_export_latency():
    """Valida que exporto de auditoria é gerado em ≤30s (SC-003)."""
    start = time.perf_counter()
    response = client.get(
        "/v1/audit/exports",
        params={"format": "json", "days": 7}
    )
    export_time = time.perf_counter() - start
    
    assert export_time < 30.0, f"Exporto gerado em {export_time:.2f}s (meta: <30s)"


def test_p95_latency_under_threshold():
    """Valida que latência p95 está abaixo de 2s (SC-004)."""
    from src.observability.metrics import chat_metrics
    
    # Simula múltiplas requisições
    for _ in range(100):
        start = time.perf_counter()
        client.post("/v1/chat/sessions", json={"user_id": "test"})
        chat_metrics.record(start)
    
    p95 = chat_metrics.p95_latency()
    assert p95 < 2.0, f"Latência p95: {p95:.2f}s (meta: <2s)"
