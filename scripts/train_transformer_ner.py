"""Train one Phase 6 transformer without accessing the final test set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sri_lankan_legal_nlp.ner.transformer import train_transformer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/ner_config.yaml"))
    parser.add_argument("--model", required=True)
    args = parser.parse_args()
    print(json.dumps(train_transformer(args.config, args.model), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
