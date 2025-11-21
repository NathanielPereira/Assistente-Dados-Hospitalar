#!/usr/bin/env python3
"""Seed de dados fictícios para NeonDB (bronze/prata/ouro).
Preenche tabelas de leitos, estoque e indicadores clínicos.
"""

import argparse
from pathlib import Path


def main(env: str) -> None:
    print(f"[seed] Carregando dados sintéticos para ambiente {env}...")
    # TODO: conectar via psycopg e executar statements


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="dev")
    args = parser.parse_args()
    main(args.env)
