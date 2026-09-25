"""Convert a completed Label Studio export into canonical annotation JSONL."""

from __future__ import annotations

import argparse
from pathlib import Path

from sri_lankan_legal_nlp.annotation.label_studio import convert_label_studio_file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--task-map",
        type=Path,
        default=Path("data/annotation/label_studio_pilot_tasks.json"),
        help="Generated task file used to recover IDs from older Label Studio imports",
    )
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Skip unsubmitted/cancelled tasks instead of failing",
    )
    parser.add_argument(
        "--use-latest-annotation",
        action="store_true",
        help="Use the latest revision only when one annotator saved multiple active revisions",
    )
    args = parser.parse_args()
    count = convert_label_studio_file(
        args.input,
        args.output,
        reference_path=args.task_map,
        allow_incomplete=args.allow_incomplete,
        use_latest_annotation=args.use_latest_annotation,
    )
    print(f"Converted {count} completed tasks to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
