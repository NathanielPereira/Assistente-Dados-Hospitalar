#!/usr/bin/env python3
"""Gera dataset de demonstração com sessões de exemplo."""

import json
from datetime import datetime, timedelta
from uuid import uuid4


def generate_demo_dataset():
    """Gera dataset de auditoria para demonstração."""
    sessions = [
        {
            "session_id": str(uuid4()),
            "user_id": "consultor-clinico-001",
            "prompt": "Qual taxa de ocupação da UTI pediátrica e qual protocolo aplicar?",
            "sql_executed": "SELECT COUNT(*) as ocupados FROM leitos WHERE setor = 'UTI_PEDIATRICA'",
            "documents_cited": ["protocolo-uti-pediatrica-v2.1.pdf"],
            "legal_basis": "Consentimento para demonstração (fictício)",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
        },
        {
            "session_id": str(uuid4()),
            "user_id": "analista-dados-001",
            "prompt": "calcular receita média por especialidade",
            "sql_executed": "SELECT e.nome, AVG(a.valor) as receita_media FROM especialidades e JOIN atendimentos a ON a.especialidade_id = e.id GROUP BY e.id, e.nome",
            "documents_cited": [],
            "legal_basis": "Análise operacional (fictício)",
            "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
        },
        {
            "session_id": str(uuid4()),
            "user_id": "oficial-compliance-001",
            "prompt": "exportar auditoria últimos 7 dias",
            "sql_executed": None,
            "documents_cited": [],
            "legal_basis": "Auditoria interna (fictício)",
            "timestamp": datetime.utcnow().isoformat(),
        },
    ]
    
    output = {
        "total_sessions": len(sessions),
        "unique_users": len(set(s["user_id"] for s in sessions)),
        "audit_entries": sessions,
        "generated_at": datetime.utcnow().isoformat(),
    }
    
    with open("shared/docs/demo-assets/demo-audit-dataset.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Dataset gerado: {len(sessions)} sessões")
    return output


if __name__ == "__main__":
    generate_demo_dataset()
