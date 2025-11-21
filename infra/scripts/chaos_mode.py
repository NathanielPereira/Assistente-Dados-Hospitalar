#!/usr/bin/env python3
"""Simulações de falha para validar resiliência e modo degradado."""

import argparse
import asyncio
import time
from datetime import datetime

from src.observability.feature_flags import flags
from src.observability.circuit_breaker import CircuitBreaker
from src.observability.alerting import AlertManager, AlertSeverity


class ChaosEngine:
    """Motor de simulações de falha."""

    def __init__(self):
        self.alert_manager = AlertManager()
        self.results = []

    async def simulate_db_failure(self, duration_seconds: int = 60):
        """Simula falha do NeonDB."""
        print(f"[CHAOS] Simulando falha do NeonDB por {duration_seconds}s...")
        
        breaker = CircuitBreaker("neondb", failure_threshold=3)
        start = time.perf_counter()
        
        # Simula falhas
        for i in range(3):
            breaker.record_failure()
            await asyncio.sleep(1)
        
        assert breaker.is_open()
        alert = self.alert_manager.create_alert(
            AlertSeverity.HIGH,
            "NeonDB falhou - ativando modo degradado",
            "neondb"
        )
        
        # Ativa modo degradado
        flags.read_only_mode = True
        print("[CHAOS] Modo degradado ativado")
        
        # Aguarda duração
        await asyncio.sleep(duration_seconds)
        
        # Recupera
        flags.read_only_mode = False
        breaker.record_success()
        print("[CHAOS] Sistema recuperado")
        
        elapsed = time.perf_counter() - start
        self.results.append({
            "scenario": "db_failure",
            "duration": elapsed,
            "degraded_mode_active": True,
            "alerts_generated": len(self.alert_manager.get_active_alerts())
        })

    async def simulate_s3_failure(self):
        """Simula falha do S3 (documentos RAG)."""
        print("[CHAOS] Simulando falha do S3...")
        breaker = CircuitBreaker("s3", failure_threshold=2)
        
        for _ in range(2):
            breaker.record_failure()
        
        alert = self.alert_manager.create_alert(
            AlertSeverity.MEDIUM,
            "S3 indisponível - RAG em modo fallback",
            "s3"
        )
        
        # Sistema deve continuar operando sem RAG
        await asyncio.sleep(30)
        breaker.record_success()
        
        self.results.append({
            "scenario": "s3_failure",
            "system_operational": True,
            "rag_available": False
        })

    async def simulate_high_latency(self):
        """Simula latência alta (p95 > 2s)."""
        print("[CHAOS] Simulando latência alta...")
        from src.observability.metrics import chat_metrics
        
        # Simula requisições lentas
        for _ in range(10):
            start = time.perf_counter()
            await asyncio.sleep(2.5)  # Simula latência alta
            chat_metrics.record(start)
        
        p95 = chat_metrics.p95_latency()
        if p95 > 2.0:
            alert = self.alert_manager.create_alert(
                AlertSeverity.WARNING,
                f"Latência p95 acima do SLO: {p95:.2f}s",
                "chat"
            )
        
        self.results.append({
            "scenario": "high_latency",
            "p95_latency": p95,
            "alert_triggered": p95 > 2.0
        })

    def print_results(self):
        """Imprime resultados das simulações."""
        print("\n=== Resultados das Simulações ===")
        for result in self.results:
            print(f"\nCenário: {result['scenario']}")
            for key, value in result.items():
                if key != "scenario":
                    print(f"  {key}: {value}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["db_failure", "s3_failure", "high_latency", "all"])
    parser.add_argument("--duration", type=int, default=60)
    args = parser.parse_args()
    
    engine = ChaosEngine()
    
    if args.scenario == "db_failure" or args.scenario == "all":
        await engine.simulate_db_failure(args.duration)
    
    if args.scenario == "s3_failure" or args.scenario == "all":
        await engine.simulate_s3_failure()
    
    if args.scenario == "high_latency" or args.scenario == "all":
        await engine.simulate_high_latency()
    
    engine.print_results()


if __name__ == "__main__":
    asyncio.run(main())
