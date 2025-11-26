"""Integration tests for end-to-end smart detection flow."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

# Note: These tests assume FastAPI app is available
# They will be fully functional after integration is complete (T050-T057)


@pytest.mark.asyncio
class TestSmartDetectionFlow:
    """End-to-end integration tests for smart detection."""
    
    async def test_unanswerable_question_returns_smart_response(self):
        """
        T045: GIVEN: User asks about non-existent entity (protocols)
        WHEN: GET /v1/chat/stream?prompt="Quais protocolos?"
        THEN: Returns SSE stream with [SMART_RESPONSE], explanation, suggestions, [DONE]
        """
        from src.api.main import app
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/v1/chat/stream",
                params={
                    "session_id": "test-123",
                    "prompt": "Quais protocolos de isolamento estão cadastrados?"
                }
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
            
            # Parse SSE stream
            lines = response.text.strip().split("\n")
            data_lines = [line.replace("data: ", "") for line in lines if line.startswith("data:")]
            
            # Verify smart response markers
            assert "[SMART_RESPONSE]" in data_lines
            assert "[DONE]" in data_lines
            
            # Verify explanation
            assert any("não está disponível" in line for line in data_lines)
            
            # Verify suggestions
            assert any("Sugestões:" in line for line in data_lines)
            suggestions = [line for line in data_lines if line.strip().startswith("•")]
            assert len(suggestions) == 3
    
    async def test_answerable_question_proceeds_normally(self):
        """
        T046: GIVEN: User asks about existing entity (leitos)
        WHEN: GET /v1/chat/stream?prompt="Quantos leitos?"
        THEN: Proceeds with normal SQL generation (no smart response)
        """
        from src.api.main import app
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/v1/chat/stream",
                params={
                    "session_id": "test-456",
                    "prompt": "Quantos leitos estão disponíveis?"
                }
            )
            
            assert response.status_code == 200
            
            lines = response.text.strip().split("\n")
            data_lines = [line.replace("data: ", "") for line in lines if line.startswith("data:")]
            
            # Should NOT have smart response marker
            assert "[SMART_RESPONSE]" not in data_lines
            
            # Should have SQL execution or results
            assert any("Executando SQL" in line or "SELECT" in line for line in data_lines) or \
                   any("Dados da consulta" in line for line in data_lines)
            
            # Must end with [DONE]
            assert "[DONE]" in data_lines
    
    async def test_partial_match_shows_warning(self):
        """
        T047: GIVEN: User asks about mixed entities (leitos + protocolos)
        WHEN: GET /v1/chat/stream?prompt="Quantos leitos e protocolos?"
        THEN: Returns [PARTIAL_MATCH] marker and warning message
        """
        from src.api.main import app
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/v1/chat/stream",
                params={
                    "session_id": "test-789",
                    "prompt": "Quantos leitos e protocolos temos?"
                }
            )
            
            assert response.status_code == 200
            
            lines = response.text.strip().split("\n")
            data_lines = [line.replace("data: ", "") for line in lines if line.startswith("data:")]
            
            # Should have partial match indicator
            assert "[PARTIAL_MATCH]" in data_lines or any("⚠️" in line for line in data_lines)
            
            # Should mention both found and not found entities
            text = " ".join(data_lines).lower()
            assert "leitos" in text
            assert "protocolos" in text or "não disponível" in text

