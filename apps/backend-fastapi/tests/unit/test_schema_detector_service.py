"""Unit tests for SchemaDetectorService."""

from __future__ import annotations

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.domain.schema_info import SchemaInfo, TableInfo, ColumnInfo


@pytest.mark.asyncio
class TestSchemaDetectorService:
    """Test suite for SchemaDetectorService."""
    
    async def test_detect_schema_from_database(self, sample_schema):
        """
        T009: GIVEN: Connected PostgreSQL database with known schema
        WHEN: detect_schema() is called
        THEN: Returns SchemaInfo with all public tables and columns
        """
        # Import here to avoid circular imports during test collection
        from src.services.schema_detector_service import SchemaDetectorService
        
        # Mock database connection
        mock_db = AsyncMock()
        mock_db.fetch_all = AsyncMock(return_value=[
            {
                "table_name": "leitos",
                "column_name": "id",
                "data_type": "integer",
                "is_nullable": "NO",
                "column_description": None
            },
            {
                "table_name": "leitos",
                "column_name": "numero",
                "data_type": "varchar",
                "is_nullable": "NO",
                "column_description": None
            },
            {
                "table_name": "leitos",
                "column_name": "status",
                "data_type": "varchar",
                "is_nullable": "YES",
                "column_description": None
            }
        ])
        
        schema = await SchemaDetectorService._detect_schema(mock_db)
        
        assert isinstance(schema, SchemaInfo)
        assert len(schema.tables) > 0
        assert schema.last_updated is not None
        assert schema.version == "1.0.0"
        
        # Verify table structure
        leitos_table = schema.get_table("leitos")
        assert leitos_table is not None
        assert len(leitos_table.columns) >= 3
    
    async def test_cache_returns_same_instance_within_ttl(self, sample_schema):
        """
        T010: GIVEN: Schema cached with TTL = 1 hour
        WHEN: get_schema() called twice within TTL
        THEN: Returns same cached instance (no database query)
        """
        from src.services.schema_detector_service import SchemaDetectorService
        
        # Reset cache for test isolation
        SchemaDetectorService._cache = None
        SchemaDetectorService._cache_timestamp = None
        
        # Mock the _detect_schema method
        with patch.object(SchemaDetectorService, '_detect_schema', return_value=sample_schema) as mock_detect:
            schema1 = await SchemaDetectorService.get_schema()
            schema2 = await SchemaDetectorService.get_schema()
            
            # Should only call _detect_schema once (cached on second call)
            assert mock_detect.call_count == 1
            assert schema1 is schema2
            assert SchemaDetectorService._cache_timestamp is not None
    
    async def test_cache_refreshes_after_ttl_expiration(self, sample_schema):
        """
        T011: GIVEN: Schema cached but TTL expired
        WHEN: get_schema() is called
        THEN: Refreshes cache from database
        """
        from src.services.schema_detector_service import SchemaDetectorService
        
        # Reset cache
        SchemaDetectorService._cache = None
        SchemaDetectorService._cache_timestamp = None
        SchemaDetectorService._ttl = timedelta(seconds=1)  # Short TTL for testing
        
        with patch.object(SchemaDetectorService, '_detect_schema', return_value=sample_schema) as mock_detect:
            schema1 = await SchemaDetectorService.get_schema()
            assert mock_detect.call_count == 1
            
            # Wait for TTL to expire
            await asyncio.sleep(1.1)
            
            schema2 = await SchemaDetectorService.get_schema()
            
            # Should call _detect_schema twice (cache expired)
            assert mock_detect.call_count == 2
            assert schema1 is not schema2  # Different instances
            assert schema2.last_updated > schema1.last_updated
    
    async def test_graceful_degradation_on_db_failure(self, sample_schema):
        """
        T012: GIVEN: Database connection fails
        AND: Valid stale cache exists
        WHEN: get_schema() is called
        THEN: Returns stale cache (degraded mode)
        AND: Logs warning but does not raise exception
        """
        from src.services.schema_detector_service import SchemaDetectorService
        
        # Pre-populate cache with valid schema
        SchemaDetectorService._cache = sample_schema
        SchemaDetectorService._cache_timestamp = datetime.utcnow()
        
        # Mock database failure
        with patch.object(SchemaDetectorService, '_detect_schema', side_effect=Exception("DB connection failed")):
            # Should return stale cache without raising
            schema = await SchemaDetectorService.get_schema()
            
            assert schema is sample_schema
            # Note: In real implementation, this should log a warning
    
    async def test_concurrent_cache_refresh_uses_lock(self, sample_schema):
        """
        T013: GIVEN: Cache expired
        AND: 10 concurrent requests
        WHEN: All requests call get_schema() simultaneously
        THEN: Only ONE database query is executed (lock prevents duplicate work)
        """
        from src.services.schema_detector_service import SchemaDetectorService
        
        # Reset cache to force refresh
        SchemaDetectorService._cache = None
        SchemaDetectorService._cache_timestamp = None
        
        call_count = 0
        
        async def mock_detect_with_delay(*args):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate slow DB query
            return sample_schema
        
        with patch.object(SchemaDetectorService, '_detect_schema', side_effect=mock_detect_with_delay):
            # Launch 10 concurrent requests
            tasks = [SchemaDetectorService.get_schema() for _ in range(10)]
            results = await asyncio.gather(*tasks)
            
            # All results should be the same instance
            assert all(r is results[0] for r in results)
            
            # Only 1 DB query should have been made (lock prevented duplicates)
            assert call_count == 1


# Additional helper tests for internal methods

@pytest.mark.asyncio
class TestSchemaDetectorHelpers:
    """Tests for SchemaDetectorService helper methods."""
    
    async def test_parse_schema_query_results(self):
        """Test parsing of information_schema query results into SchemaInfo."""
        from src.services.schema_detector_service import SchemaDetectorService
        
        # Mock query results
        mock_rows = [
            {
                "table_name": "leitos",
                "column_name": "id",
                "data_type": "integer",
                "is_nullable": "NO",
                "column_description": None
            },
            {
                "table_name": "leitos",
                "column_name": "status",
                "data_type": "varchar",
                "is_nullable": "YES",
                "column_description": "Status do leito"
            },
            {
                "table_name": "atendimentos",
                "column_name": "id",
                "data_type": "integer",
                "is_nullable": "NO",
                "column_description": None
            }
        ]
        
        schema = SchemaDetectorService._parse_query_results(mock_rows)
        
        assert isinstance(schema, SchemaInfo)
        assert len(schema.tables) == 2  # leitos and atendimentos
        
        leitos = schema.get_table("leitos")
        assert leitos is not None
        assert len(leitos.columns) == 2
        
        status_col = leitos.get_column("status")
        assert status_col is not None
        assert status_col.nullable is True
        assert status_col.description == "Status do leito"

