"""Validate and convert Doccano JSONL annotations to BIO CoNLL."""

from __future__ import annotations

import argparse
from pathlib import Path

from sri_lankan_legal_nlp.annotation.export import export_conll


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--labels", type=Path, default=Path("data/annotation/labels.json"))
    args = parser.parse_args()
    export_conll(args.input, args.labels, args.output)
    print(f"Exported: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
