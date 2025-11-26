"""Service for detecting and caching database schema metadata."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.config import settings
from src.domain.schema_info import SchemaInfo, TableInfo, ColumnInfo

logger = logging.getLogger(__name__)


class SchemaDetectorService:
    """
    Service for detecting PostgreSQL schema and caching it in memory.
    
    Uses cache-first architecture with configurable TTL (default 1 hour).
    Thread-safe using asyncio.Lock for cache writes.
    Implements degraded mode: uses stale cache on DB failures.
    """
    
    # Class-level cache (shared across all instances)
    _cache: Optional[SchemaInfo] = None
    _cache_timestamp: Optional[datetime] = None
    _refresh_lock: asyncio.Lock = asyncio.Lock()
    _ttl: timedelta = timedelta(seconds=settings.SCHEMA_CACHE_TTL_SECONDS)
    
    @classmethod
    async def get_schema(cls, db=None) -> SchemaInfo:
        """
        Get cached schema, refresh if expired.
        
        Args:
            db: Database connection (optional, uses global if not provided)
            
        Returns:
            SchemaInfo with current database schema
            
        Raises:
            Exception: Only if cache is empty and detection fails
        """
        now = datetime.utcnow()
        
        # Fast path: cache valid, no lock needed
        if cls._cache and cls._cache_timestamp:
            age = now - cls._cache_timestamp
            if age < cls._ttl:
                logger.debug(f"Schema cache hit (age: {age.total_seconds():.1f}s)")
                return cls._cache
        
        # Slow path: cache expired or empty, acquire lock for refresh
        async with cls._refresh_lock:
            # Double-check: another request might have refreshed while waiting
            if cls._cache and cls._cache_timestamp:
                age = now - cls._cache_timestamp
                if age < cls._ttl:
                    logger.debug(f"Schema cache hit after lock (age: {age.total_seconds():.1f}s)")
                    return cls._cache
            
            # Refresh cache
            try:
                logger.info("Refreshing schema cache...")
                
                # Get database connection
                if db is None:
                    from src.database import db as global_db
                    db = global_db
                
                new_schema = await cls._detect_schema(db)
                cls._cache = new_schema
                cls._cache_timestamp = now
                
                logger.info(f"Schema cache refreshed: {len(new_schema.tables)} tables, {new_schema.total_columns} columns")
                return new_schema
                
            except Exception as e:
                logger.error(f"Schema detection failed: {e}")
                
                # Degraded mode: return stale cache if available
                if cls._cache:
                    age = now - cls._cache_timestamp if cls._cache_timestamp else timedelta(seconds=0)
                    logger.warning(
                        f"Using stale schema cache (age: {age.total_seconds():.1f}s) "
                        f"due to detection failure"
                    )
                    return cls._cache
                
                # No cache available, must fail
                logger.critical("Schema detection failed and no cache available")
                raise
    
    @classmethod
    async def _detect_schema(cls, db) -> SchemaInfo:
        """
        Detect database schema using information_schema.
        
        Uses optimized single-query approach from research.md.
        
        Args:
            db: Database connection
            
        Returns:
            SchemaInfo with detected schema
        """
        # Optimized single JOIN query from research.md
        query = """
        SELECT 
            t.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.ordinal_position,
            pgd.description AS column_description
        FROM information_schema.tables t
        JOIN information_schema.columns c 
            ON t.table_name = c.table_name 
            AND t.table_schema = c.table_schema
        LEFT JOIN pg_catalog.pg_statio_all_tables AS st 
            ON t.table_name = st.relname
        LEFT JOIN pg_catalog.pg_description pgd 
            ON pgd.objoid = st.relid 
            AND pgd.objsubid = c.ordinal_position
        WHERE t.table_schema = 'public'
            AND t.table_type = 'BASE TABLE'
        ORDER BY t.table_name, c.ordinal_position;
        """
        
        rows = await db.execute_query(query)
        return cls._parse_query_results(rows)
    
    @classmethod
    def _parse_query_results(cls, rows: List[Dict]) -> SchemaInfo:
        """
        Parse information_schema query results into SchemaInfo.
        
        Args:
            rows: Query results from information_schema
            
        Returns:
            SchemaInfo with parsed data
        """
        # Group columns by table
        tables_dict: Dict[str, List[ColumnInfo]] = {}
        
        for row in rows:
            table_name = row["table_name"]
            
            column = ColumnInfo(
                name=row["column_name"],
                type=row["data_type"],
                nullable=(row["is_nullable"] == "YES"),
                description=row.get("column_description")
            )
            
            if table_name not in tables_dict:
                tables_dict[table_name] = []
            
            tables_dict[table_name].append(column)
        
        # Create TableInfo objects
        tables = []
        for table_name, columns in tables_dict.items():
            table = TableInfo(
                name=table_name,
                columns=columns,
                description=None,  # Could be enhanced to query table comments
                row_count=None  # Could be enhanced to query table statistics
            )
            tables.append(table)
        
        return SchemaInfo(
            tables=tables,
            last_updated=datetime.utcnow(),
            version="1.0.0"
        )
    
    @classmethod
    async def start_health_check(cls, interval_seconds: int = 300):
        """
        Start background task to periodically refresh schema cache.
        
        Args:
            interval_seconds: How often to check/refresh (default 5 minutes)
        """
        logger.info(f"Starting schema health check (interval: {interval_seconds}s)")
        
        while True:
            try:
                await asyncio.sleep(interval_seconds)
                
                # Check if cache is close to expiring
                if cls._cache_timestamp:
                    age = datetime.utcnow() - cls._cache_timestamp
                    time_to_expiry = cls._ttl - age
                    
                    # Refresh proactively if < 10% TTL remaining
                    if time_to_expiry < cls._ttl * 0.1:
                        logger.info("Proactively refreshing schema cache")
                        await cls.get_schema()
                        
            except asyncio.CancelledError:
                logger.info("Schema health check cancelled")
                break
            except Exception as e:
                logger.error(f"Schema health check error: {e}")
    
    @classmethod
    def get_cache_age(cls) -> Optional[timedelta]:
        """
        Get age of current cache.
        
        Returns:
            timedelta since last refresh, or None if no cache
        """
        if cls._cache_timestamp:
            return datetime.utcnow() - cls._cache_timestamp
        return None
    
    @classmethod
    def clear_cache(cls):
        """Clear the schema cache (useful for testing)."""
        cls._cache = None
        cls._cache_timestamp = None
        logger.info("Schema cache cleared")

