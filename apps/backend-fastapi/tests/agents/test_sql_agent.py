import pytest
from src.agents.sql_agent import SQLAgentService


def test_suggest_sql():
    """Testa sugestão de SQL baseada em prompt natural."""
    service = SQLAgentService()
    suggestion = service.suggest("calcular receita média por especialidade")
    assert "SELECT" in suggestion.sql
    assert suggestion.comments is not None


def test_validate_sql():
    """Testa validação de sintaxe SQL."""
    service = SQLAgentService()
    valid = service.validate("SELECT * FROM especialidades")
    assert valid.is_valid is True


def test_fallback_manual():
    """Testa que SQL manual pode ser usado mesmo sem sugestão."""
    service = SQLAgentService()
    manual_sql = "SELECT COUNT(*) FROM pacientes"
    result = service.execute(manual_sql, approved=True)
    assert result is not None
