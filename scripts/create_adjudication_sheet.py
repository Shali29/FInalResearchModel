"""Create a CSV worksheet for human resolution of annotation disagreements."""

from __future__ import annotations

import argparse
from pathlib import Path

from sri_lankan_legal_nlp.annotation.adjudication import write_adjudication_sheet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("annotator_1", type=Path)
    parser.add_argument("annotator_2", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    count = write_adjudication_sheet(args.annotator_1, args.annotator_2, args.output)
    print(f"Wrote {args.output} with {count} disputed span decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
