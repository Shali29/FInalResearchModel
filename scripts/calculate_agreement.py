"""Calculate exact-span F1 and token Cohen's kappa for two annotators."""

from __future__ import annotations

import argparse
from pathlib import Path

from sri_lankan_legal_nlp.annotation.agreement_report import write_agreement_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("annotator_1", type=Path)
    parser.add_argument("annotator_2", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    write_agreement_report(args.annotator_1, args.annotator_2, args.output)
    print(f"Agreement report written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
