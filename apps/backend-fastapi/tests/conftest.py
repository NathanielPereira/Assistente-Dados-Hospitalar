"""Test fixtures para Smart Response Detection."""

from __future__ import annotations

import pytest
from datetime import datetime
from typing import Dict

from src.domain.schema_info import SchemaInfo, TableInfo, ColumnInfo


@pytest.fixture
def sample_schema() -> SchemaInfo:
    """Typical hospital database schema for testing."""
    return SchemaInfo(
        tables=[
            TableInfo(
                name="leitos",
                columns=[
                    ColumnInfo(name="id", type="integer", nullable=False),
                    ColumnInfo(name="numero", type="varchar", nullable=False),
                    ColumnInfo(name="status", type="varchar", nullable=True),
                ],
                description="Hospital beds",
                row_count=150
            ),
            TableInfo(
                name="atendimentos",
                columns=[
                    ColumnInfo(name="id", type="integer", nullable=False),
                    ColumnInfo(name="paciente_id", type="integer", nullable=False),
                    ColumnInfo(name="data", type="date", nullable=False),
                    ColumnInfo(name="valor", type="decimal", nullable=True),
                ],
                description="Patient appointments",
                row_count=5420
            ),
            TableInfo(
                name="especialidades",
                columns=[
                    ColumnInfo(name="id", type="integer", nullable=False),
                    ColumnInfo(name="nome", type="varchar", nullable=False),
                ],
                description="Medical specialties",
                row_count=25
            ),
        ],
        last_updated=datetime.utcnow(),
        version="1.0.0"
    )


@pytest.fixture
def synonyms_dict() -> Dict[str, str]:
    """Common synonym mappings for testing."""
    return {
        "camas": "leitos",
        "cama": "leitos",
        "quartos": "leitos",
        "consultas": "atendimentos",
        "consulta": "atendimentos",
        "doutores": "especialidades",
        "médicos": "especialidades",
    }


@pytest.fixture
def answerable_questions():
    """Test questions that SHOULD be answerable with the sample schema."""
    return [
        ("Quantos leitos estão disponíveis?", ["leitos"], 0.90),
        ("Qual a receita média por atendimento?", ["atendimentos"], 0.85),
        ("Quais especialidades estão cadastradas?", ["especialidades"], 0.95),
        ("Quantas camas temos?", ["leitos"], 0.80),  # Via synonym
    ]


@pytest.fixture
def unanswerable_questions():
    """Test questions that should NOT be answerable with the sample schema."""
    return [
        ("Qual protocolo aplicar para isolamento?", ["protocolo", "isolamento"], 0.0),
        ("Quanto custa o medicamento Xanax?", ["medicamento", "xanax"], 0.0),
        ("Qual o estoque de EPIs?", ["estoque", "epis"], 0.0),
    ]


@pytest.fixture
def partial_match_questions():
    """Test questions with some entities found, others not."""
    return [
        ("Quantos leitos e protocolos temos?", ["leitos", "protocolos"], 0.50),
        ("Listar atendimentos e medicamentos", ["atendimentos", "medicamentos"], 0.50),
    ]


@pytest.fixture
def ambiguous_questions():
    """Test questions that are too vague to extract entities."""
    return [
        ("O que você sabe?", [], 0.0),
        ("Me ajuda", [], 0.0),
        ("Informações", [], 0.0),
    ]


# TODO: Add database connection fixture after Phase 2 domain models
# @pytest.fixture
# async def db_connection():
#     """Async database connection for integration tests."""
#     pass

