"""Audit grouped cross-validation support for any canonical annotation JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from sri_lankan_legal_nlp.data.splitting import feasibility_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--config", type=Path, default=Path("configs/ner_config.yaml"))
    args = parser.parse_args()
    rows = [
        json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line
    ]
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    report = feasibility_report(
        rows,
        config["annotation"]["labels"],
        int(config["splitting"]["development_cross_validation_folds"]),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
