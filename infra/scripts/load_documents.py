#!/usr/bin/env python3
"""Carrega documentos fictícios para o bucket S3 compatível e registra metadados."""

import argparse
from pathlib import Path


def main(source: Path, bucket: str) -> None:
    print(f"[docs] Lendo {source} e enviando para {bucket} com metadados de sigilo...")
    # TODO: implementar upload e catalogação


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--bucket", required=True)
    args = parser.parse_args()
    main(args.source, args.bucket)
