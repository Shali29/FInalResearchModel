"""Create a cleaned annotation copy while preserving raw exports."""

from __future__ import annotations

import argparse
from pathlib import Path

from sri_lankan_legal_nlp.annotation.normalize import normalize_file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("log", type=Path)
    parser.add_argument("annotator_key", choices=["annotator_1", "annotator_2", "targeted_gap"])
    parser.add_argument(
        "--corrections",
        type=Path,
        default=Path("configs/annotation_corrections.yaml"),
    )
    args = parser.parse_args()
    normalize_file(args.input, args.output, args.log, args.corrections, args.annotator_key)
    print(f"Normalized copy written to {args.output}; audit log written to {args.log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
