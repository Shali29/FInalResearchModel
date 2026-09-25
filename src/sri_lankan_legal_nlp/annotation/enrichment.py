"""Select entity-enriched tasks using auditable cues without assigning labels."""

from __future__ import annotations

import csv
import json
import random
import re
from pathlib import Path
from typing import Any


def select_enriched_tasks(
    tasks: list[dict[str, Any]],
    cues: dict[str, dict[str, str]],
    per_group: int,
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Select unique tasks per language/cue group while leaving annotations empty."""
    rng = random.Random(seed)
    buckets: dict[str, list[dict[str, Any]]] = {}
    for language, language_cues in cues.items():
        for group, pattern in language_cues.items():
            key = f"{language}:{group}"
            matches = [
                task
                for task in tasks
                if task["meta"]["language"] == language
                and re.search(pattern, task["text"], flags=re.IGNORECASE)
            ]
            rng.shuffle(matches)
            buckets[key] = matches

    selected: list[dict[str, Any]] = []
    assigned_group: dict[str, str] = {}
    used: set[str] = set()
    for key in sorted(buckets, key=lambda name: len(buckets[name])):
        available = [task for task in buckets[key] if task["id"] not in used]
        chosen = available[:per_group]
        if len(chosen) < per_group:
            raise ValueError(
                f"Enrichment group {key} has only {len(chosen)} unique tasks; "
                f"requested {per_group}. Reduce the configured quota."
            )
        for task in chosen:
            used.add(task["id"])
            assigned_group[task["id"]] = key
            selected.append(task)
    return selected, assigned_group


def write_enriched_outputs(
    output: Path,
    tasks: list[dict[str, Any]],
    groups: dict[str, str],
    seed: int,
) -> None:
    """Write Doccano, Label Studio, audit, and shared-subset artifacts."""
    with (output / "doccano_enriched_pilot_tasks.jsonl").open(
        "w", encoding="utf-8", newline="\n"
    ) as stream:
        for task in tasks:
            stream.write(json.dumps(task, ensure_ascii=False) + "\n")
    label_studio = [
        {
            "id": task["id"],
            "data": {
                "research_task_id": task["id"],
                "text": task["text"],
                **task["meta"],
            },
        }
        for task in tasks
    ]
    (output / "label_studio_enriched_pilot_tasks.json").write_text(
        json.dumps(label_studio, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    by_group: dict[str, list[dict[str, Any]]] = {}
    for task in tasks:
        by_group.setdefault(groups[task["id"]], []).append(task)
    rng = random.Random(seed)
    shared: list[dict[str, Any]] = []
    for group in sorted(by_group):
        shared.extend(rng.sample(by_group[group], min(5, len(by_group[group]))))
    shared_ids = {task["id"] for task in shared}
    shared_label_studio = [item for item in label_studio if item["id"] in shared_ids]
    (output / "label_studio_enriched_shared_tasks.json").write_text(
        json.dumps(shared_label_studio, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    fields = [
        "task_id",
        "language",
        "document_type",
        "source_file",
        "pdf_page_number",
        "selection_cue_group",
        "shared_subset",
        "annotator_1_status",
        "annotator_2_status",
        "adjudication_status",
        "notes",
    ]
    with (output / "enriched_annotation_progress.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for task in tasks:
            is_shared = task["id"] in shared_ids
            writer.writerow(
                {
                    "task_id": task["id"],
                    "language": task["meta"]["language"],
                    "document_type": task["meta"]["document_type"],
                    "source_file": task["meta"]["source_file"],
                    "pdf_page_number": task["meta"]["pdf_page_number"],
                    "selection_cue_group": groups[task["id"]],
                    "shared_subset": "yes" if is_shared else "no",
                    "annotator_1_status": "not_started",
                    "annotator_2_status": "not_started" if is_shared else "not_required",
                    "adjudication_status": "not_started" if is_shared else "not_required",
                }
            )
