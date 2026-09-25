"""Create a balanced blank expansion corpus without generating entity labels."""

from __future__ import annotations

import csv
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read UTF-8 JSONL records."""
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    annotation = root / "data" / "annotation"
    config = yaml.safe_load((root / "configs" / "ner_config.yaml").read_text(encoding="utf-8"))
    seed = int(config["project"]["random_seed"])
    rng = random.Random(seed + 420)
    all_tasks = read_jsonl(annotation / "doccano_tasks.jsonl")
    existing = read_jsonl(root / "data" / "processed" / "provisional_combined_corpus.jsonl")
    used_ids = {str(row["id"]) for row in existing}
    used_parents = {str(row["meta"].get("parent_record_id", row["id"])) for row in existing}
    cues = config["preparation"]["enrichment_cues"]
    targets = {
        "si:fundamental_right": 25,
        "en:fundamental_right": 45,
        "en:offense": 44,
        "en:penalty": 44,
        "en:constitutional_body": 44,
        "si:offense": 44,
        "si:penalty": 44,
        "si:constitutional_body": 44,
        "en:temporal": 43,
        "si:temporal": 43,
    }
    candidates: dict[str, list[dict[str, Any]]] = {}
    for language, groups in cues.items():
        for entity_group, pattern in groups.items():
            key = f"{language}:{entity_group}"
            values = [
                task
                for task in all_tasks
                if task["id"] not in used_ids
                and task["meta"]["language"] == language
                and re.search(pattern, task["text"], flags=re.IGNORECASE)
            ]
            rng.shuffle(values)
            candidates[key] = values

    selected: list[tuple[dict[str, Any], str]] = []
    selected_ids: set[str] = set()
    selected_parents: set[str] = set(used_parents)
    for group in sorted(candidates, key=lambda key: len(candidates[key])):
        chosen: list[dict[str, Any]] = []
        for task in candidates[group]:
            parent = str(task["meta"].get("parent_record_id", task["id"]))
            if task["id"] in selected_ids or parent in selected_parents:
                continue
            chosen.append(task)
            selected_ids.add(str(task["id"]))
            selected_parents.add(parent)
            if len(chosen) == targets[group]:
                break
        if len(chosen) != targets[group]:
            raise ValueError(
                f"Only {len(chosen)} unique-parent tasks available for {group}; "
                f"required {targets[group]}."
            )
        selected.extend((task, group) for task in chosen)

    by_group: dict[str, list[str]] = defaultdict(list)
    for task, group in selected:
        by_group[group].append(str(task["id"]))
    shared_ids: set[str] = set()
    for index, (_group, task_ids) in enumerate(sorted(by_group.items())):
        count = 9 if index < 4 else 8
        shared_ids.update(rng.sample(task_ids, count))

    label_studio = [
        {
            "id": task["id"],
            "data": {
                "research_task_id": task["id"],
                "text": task["text"],
                "selection_cue_group": group,
                **task["meta"],
            },
        }
        for task, group in selected
    ]
    output = annotation / "expansion"
    output.mkdir(parents=True, exist_ok=True)
    (output / "label_studio_expansion_all.json").write_text(
        json.dumps(label_studio, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    shared = [task for task in label_studio if str(task["id"]) in shared_ids]
    (output / "label_studio_expansion_shared.json").write_text(
        json.dumps(shared, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for index in range(0, len(label_studio), 100):
        part = label_studio[index : index + 100]
        (output / f"label_studio_expansion_part_{index // 100 + 1:02d}.json").write_text(
            json.dumps(part, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    fields = [
        "task_id",
        "selection_cue_group",
        "language",
        "document_type",
        "source_file",
        "pdf_page_number",
        "shared_subset",
        "annotator_1_status",
        "annotator_2_status",
        "adjudication_status",
        "notes",
    ]
    with (output / "expansion_progress.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for task, group in selected:
            is_shared = str(task["id"]) in shared_ids
            writer.writerow(
                {
                    "task_id": task["id"],
                    "selection_cue_group": group,
                    "language": task["meta"]["language"],
                    "document_type": task["meta"]["document_type"],
                    "source_file": task["meta"]["source_file"],
                    "pdf_page_number": task["meta"]["pdf_page_number"],
                    "shared_subset": "yes" if is_shared else "no",
                    "annotator_1_status": "not_started",
                    "annotator_2_status": "not_started" if is_shared else "not_required",
                    "adjudication_status": "not_started" if is_shared else "not_required",
                }
            )

    manifest = {
        "random_seed": seed + 420,
        "selection_method": "language/entity cue enrichment; cues are not labels",
        "labels_generated": False,
        "task_count": len(label_studio),
        "shared_subset_count": len(shared),
        "shared_subset_fraction": len(shared) / len(label_studio),
        "unique_parent_count": len(
            {task["data"].get("parent_record_id", task["id"]) for task in label_studio}
        ),
        "overlap_with_existing_task_ids": len(selected_ids & used_ids),
        "group_counts": dict(sorted(Counter(group for _, group in selected).items())),
        "language_counts": dict(
            sorted(Counter(task["meta"]["language"] for task, _ in selected).items())
        ),
        "document_type_counts": dict(
            sorted(Counter(task["meta"]["document_type"] for task, _ in selected).items())
        ),
        "annotation_status": "blank_pending_human_annotation",
    }
    (output / "expansion_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
