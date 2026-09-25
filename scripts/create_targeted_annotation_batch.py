"""Create a blank targeted batch for under-supported language/entity cue groups."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    annotation = root / "data" / "annotation"
    tasks = {
        row["id"]: row
        for row in (
            json.loads(line)
            for line in (annotation / "doccano_enriched_pilot_tasks.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line
        )
    }
    progress = list(
        csv.DictReader((annotation / "enriched_annotation_progress.csv").open(encoding="utf-8-sig"))
    )
    targets = {
        "en:fundamental_right": 10,
        "si:fundamental_right": 10,
        "si:temporal": 10,
    }
    rng = random.Random(2026)
    selected: list[tuple[dict, str]] = []
    for group, count in targets.items():
        candidates = [
            row["task_id"]
            for row in progress
            if row["selection_cue_group"] == group and row["shared_subset"] == "no"
        ]
        rng.shuffle(candidates)
        selected.extend((tasks[task_id], group) for task_id in candidates[:count])
    label_studio = [
        {
            "id": task["id"],
            "data": {
                "research_task_id": task["id"],
                "text": task["text"],
                **task["meta"],
            },
        }
        for task, _ in selected
    ]
    (annotation / "label_studio_targeted_gap_tasks.json").write_text(
        json.dumps(label_studio, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (annotation / "targeted_gap_progress.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "task_id",
                "selection_cue_group",
                "language",
                "source_file",
                "pdf_page_number",
                "annotation_status",
                "notes",
            ],
        )
        writer.writeheader()
        for task, group in selected:
            writer.writerow(
                {
                    "task_id": task["id"],
                    "selection_cue_group": group,
                    "language": task["meta"]["language"],
                    "source_file": task["meta"]["source_file"],
                    "pdf_page_number": task["meta"]["pdf_page_number"],
                    "annotation_status": "not_started",
                }
            )
    print(f"Created {len(selected)} blank targeted tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
