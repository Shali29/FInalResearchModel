"""Merge canonical annotation JSONL files while rejecting duplicate task IDs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument(
        "--default-consensus-status",
        default="single_annotator_targeted_gap_annotation",
        help="Status assigned only to input rows that do not already declare one",
    )
    args = parser.parse_args()
    merged: dict[str, dict] = {}
    for input_path in args.inputs:
        for line in input_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row["id"] in merged:
                raise ValueError(f"Duplicate task ID across corpora: {row['id']}")
            if "consensus_status" not in row:
                row["consensus_status"] = args.default_consensus_status
            merged[row["id"]] = row
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        for task_id in sorted(merged):
            stream.write(json.dumps(merged[task_id], ensure_ascii=False) + "\n")
    print(f"Merged {len(merged)} unique tasks into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
