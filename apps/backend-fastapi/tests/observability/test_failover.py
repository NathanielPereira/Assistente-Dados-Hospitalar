import pytest
from src.observability.feature_flags import FeatureFlags, flags


def test_read_only_mode_activation():
    """Testa ativação de modo read-only via feature flag."""
    original = flags.read_only_mode
    flags.read_only_mode = True
    
    # Verifica que sistema está em modo degradado
    assert flags.read_only_mode is True
    
    # Restaura
    flags.read_only_mode = original


def test_circuit_breaker_trigger():
    """Testa que circuit breaker dispara alertas quando ativado."""
    from src.observability.circuit_breaker import CircuitBreaker
    
    breaker = CircuitBreaker("neondb", failure_threshold=3)
    
    # Simula falhas
    for _ in range(3):
        breaker.record_failure()
    
    # Verifica que breaker está aberto
    assert breaker.is_open() is True
    assert breaker.should_alert() is True


def test_alert_generation():
    """Testa geração de alertas quando modo degradado é ativado."""
    from src.observability.alerting import AlertManager
    
    manager = AlertManager()
    alert = manager.create_alert(
        severity="HIGH",
        message="Sistema em modo degradado",
        component="neondb"
    )
    
    assert alert.severity == "HIGH"
    assert "degradado" in alert.message.lower()
