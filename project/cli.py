#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from orchestrator.pipeline import run


def main() -> None:
    parser = argparse.ArgumentParser(description="IADT — Análise de diagramas de arquitetura")
    parser.add_argument("file", help="Caminho para o diagrama (.png, .jpg, .jpeg, .pdf)")
    parser.add_argument("--output", "-o", help="Diretório de saída (padrão: runs/<nome-arquivo>)")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Erro: arquivo não encontrado: {file_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Processando: {file_path}")
    try:
        result = run(file_path, output_dir=args.output)
    except Exception as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"\nValidação: {result.validation}")
    print(f"Tempo total: {result.elapsed_s}s")
    print(f"\nArtefatos gerados:")
    for name, path in result.artifacts.items():
        print(f"  {name}: {path}")

    if not result.success:
        sys.exit(2)


if __name__ == "__main__":
    main()
