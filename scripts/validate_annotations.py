"""Validate a Doccano JSONL export before corpus conversion."""

from __future__ import annotations

import argparse
from pathlib import Path

from sri_lankan_legal_nlp.annotation.validation import validate_annotation_file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--labels", type=Path, default=Path("data/annotation/labels.json"))
    args = parser.parse_args()
    errors = validate_annotation_file(args.input, args.labels)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Validation passed: {args.input}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
