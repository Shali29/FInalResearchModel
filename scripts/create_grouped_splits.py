"""Create leakage-safe provisional NER splits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sri_lankan_legal_nlp.data.grouped_splits import create_grouped_splits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    print(json.dumps(create_grouped_splits(args.input, args.output, args.seed), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
