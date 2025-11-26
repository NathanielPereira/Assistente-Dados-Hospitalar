"""Contract tests to ensure no breaking changes to chat API."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestChatAPIBackwardCompatibility:
    """Ensure no breaking changes to existing API."""
    
    async def test_existing_sse_format_still_works(self):
        """
        T048: GIVEN: Existing client expects 'data:' prefix lines
        WHEN: Answerable question is asked
        THEN: Response format matches existing contract
        """
        from src.api.main import app
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/v1/chat/stream",
                params={"session_id": "test", "prompt": "Quantos leitos?"}
            )
            
            lines = response.text.strip().split("\n")
            
            # All lines should start with 'data:' (SSE format)
            non_empty_lines = [line for line in lines if line.strip()]
            for line in non_empty_lines:
                assert line.startswith("data:"), f"Line doesn't start with 'data:': {line}"
            
            # Must end with [DONE]
            data_lines = [line.replace("data: ", "") for line in lines if line.startswith("data:")]
            assert "[DONE]" in data_lines
    
    async def test_old_clients_can_ignore_new_markers(self):
        """
        T049: GIVEN: Old client ignores unknown SSE event types
        WHEN: Smart response includes new markers like [SMART_RESPONSE]
        THEN: Client can still parse response by ignoring unknown markers
        """
        from src.api.main import app
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/v1/chat/stream",
                params={"session_id": "test", "prompt": "Quais protocolos?"}
            )
            
            lines = response.text.strip().split("\n")
            data_lines = [line for line in lines if line.startswith("data:")]
            
            # Verify all markers are just data lines (not event types)
            assert all(":" in line for line in data_lines)  # 'data:' prefix
            
            # No 'event:' lines introduced (would break old clients)
            event_lines = [line for line in lines if line.startswith("event:")]
            assert len(event_lines) == 0, "No event: lines should be introduced"

