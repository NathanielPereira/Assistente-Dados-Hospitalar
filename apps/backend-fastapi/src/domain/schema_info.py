"""Domain models for database schema representation."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ColumnInfo(BaseModel):
    """Metadata for a single database column."""
    
    name: str = Field(
        description="Column name as it appears in the database"
    )
    type: str = Field(
        description="PostgreSQL data type (e.g., 'integer', 'varchar', 'timestamp')"
    )
    nullable: bool = Field(
        description="Whether column allows NULL values"
    )
    description: Optional[str] = Field(
        default=None,
        description="Column description from PostgreSQL comments (if available)"
    )
    
    @property
    def is_numeric(self) -> bool:
        """Check if column is numeric type."""
        numeric_types = {"integer", "bigint", "smallint", "decimal", "numeric", "real", "double precision"}
        return self.type.lower() in numeric_types
    
    @property
    def is_text(self) -> bool:
        """Check if column is text type."""
        text_types = {"varchar", "text", "char", "character varying"}
        return self.type.lower() in text_types or self.type.lower().startswith("varchar")
    
    @property
    def is_temporal(self) -> bool:
        """Check if column is date/time type."""
        temporal_types = {"date", "timestamp", "time", "interval", "timestamptz"}
        return self.type.lower() in temporal_types or "timestamp" in self.type.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "created_at",
                "type": "timestamp with time zone",
                "nullable": False,
                "description": "Record creation timestamp"
            }
        }


class TableInfo(BaseModel):
    """Metadata for a single database table."""
    
    name: str = Field(
        description="Table name as it appears in the database"
    )
    columns: List[ColumnInfo] = Field(
        description="All columns in this table",
        min_length=1  # Table must have at least one column
    )
    description: Optional[str] = Field(
        default=None,
        description="Table description from PostgreSQL comments (if available)"
    )
    row_count: Optional[int] = Field(
        default=None,
        description="Approximate number of rows (cached, may be stale)",
        ge=0
    )
    
    # Computed properties
    @property
    def column_count(self) -> int:
        """Number of columns in this table."""
        return len(self.columns)
    
    @property
    def nullable_columns(self) -> List[str]:
        """Names of columns that allow NULL."""
        return [col.name for col in self.columns if col.nullable]
    
    @property
    def numeric_columns(self) -> List[str]:
        """Names of numeric columns (for aggregation suggestions)."""
        numeric_types = {"integer", "bigint", "smallint", "decimal", "numeric", "real", "double precision"}
        return [col.name for col in self.columns if col.type.lower() in numeric_types]
    
    # Methods
    def get_column(self, name: str) -> Optional[ColumnInfo]:
        """Find column by name (case-insensitive).
        
        Args:
            name: Column name to search for
            
        Returns:
            ColumnInfo if found, None otherwise
        """
        name_lower = name.lower()
        for column in self.columns:
            if column.name.lower() == name_lower:
                return column
        return None
    
    def has_status_column(self) -> bool:
        """Check if table has a column indicating status/state."""
        status_keywords = {"status", "estado", "situacao", "ativo"}
        for column in self.columns:
            if any(keyword in column.name.lower() for keyword in status_keywords):
                return True
        return False
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "atendimentos",
                "columns": [
                    {"name": "id", "type": "integer", "nullable": False},
                    {"name": "paciente_id", "type": "integer", "nullable": False},
                    {"name": "data", "type": "date", "nullable": False},
                    {"name": "valor", "type": "decimal", "nullable": True}
                ],
                "description": "Patient appointments and consultations",
                "row_count": 5420
            }
        }


class SchemaInfo(BaseModel):
    """Complete database schema metadata."""
    
    tables: List[TableInfo] = Field(
        description="All database tables in the public schema"
    )
    last_updated: datetime = Field(
        description="Timestamp when schema was last refreshed from database"
    )
    version: str = Field(
        default="1.0.0",
        description="Schema version identifier (for cache invalidation)"
    )
    
    # Computed properties
    @property
    def table_count(self) -> int:
        """Total number of tables."""
        return len(self.tables)
    
    @property
    def total_columns(self) -> int:
        """Total number of columns across all tables."""
        return sum(len(table.columns) for table in self.tables)
    
    # Methods
    def get_table(self, name: str) -> Optional[TableInfo]:
        """Find table by name (case-insensitive).
        
        Args:
            name: Table name to search for
            
        Returns:
            TableInfo if found, None otherwise
        """
        name_lower = name.lower()
        for table in self.tables:
            if table.name.lower() == name_lower:
                return table
        return None
    
    def get_all_entities(self) -> List[str]:
        """Get all table names as potential entities.
        
        Returns:
            List of table names in original case
        """
        return [table.name for table in self.tables]
    
    def get_all_columns(self) -> List[str]:
        """Get all column names in 'table.column' format.
        
        Returns:
            List of fully qualified column names
        """
        result = []
        for table in self.tables:
            for column in table.columns:
                result.append(f"{table.name}.{column.name}")
        return result
    
    def find_similar_tables(self, term: str, threshold: float = 0.70) -> List[tuple[str, float]]:
        """Find tables with names similar to the given term.
        
        Args:
            term: Search term
            threshold: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of (table_name, similarity_score) tuples, sorted by score descending
        """
        from difflib import SequenceMatcher
        
        results = []
        term_lower = term.lower()
        
        for table in self.tables:
            score = SequenceMatcher(None, term_lower, table.name.lower()).ratio()
            if score >= threshold:
                results.append((table.name, score))
        
        return sorted(results, key=lambda x: x[1], reverse=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "tables": [
                    {
                        "name": "leitos",
                        "columns": [
                            {"name": "id", "type": "integer", "nullable": False},
                            {"name": "numero", "type": "varchar", "nullable": False},
                            {"name": "status", "type": "varchar", "nullable": True}
                        ],
                        "description": "Hospital beds and their status",
                        "row_count": 150
                    }
                ],
                "last_updated": "2024-11-26T10:00:00Z",
                "version": "1.0.0"
            }
        }

