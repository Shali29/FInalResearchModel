"""Apply a completed adjudication CSV to two clean annotation files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sri_lankan_legal_nlp.annotation.apply_adjudication import apply_adjudication


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("annotator_1", type=Path)
    parser.add_argument("annotator_2", type=Path)
    parser.add_argument("decisions", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest = apply_adjudication(
        args.annotator_1, args.annotator_2, args.decisions, args.output, args.manifest
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
