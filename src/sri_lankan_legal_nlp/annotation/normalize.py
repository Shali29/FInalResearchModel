"""Apply logged, non-destructive boundary normalization to annotation exports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def normalize_file(
    input_path: Path,
    output_path: Path,
    log_path: Path,
    corrections_path: Path,
    annotator_key: str,
) -> None:
    """Trim whitespace, remove empty spans, and apply researcher-confirmed corrections."""
    rows = [
        json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line
    ]
    corrections = yaml.safe_load(corrections_path.read_text(encoding="utf-8"))[annotator_key]
    drop = {
        task_id: {tuple(span) for span in spans}
        for task_id, spans in corrections.get("drop_spans", {}).items()
    }
    replacements = corrections.get("replace_spans", {})
    actions: list[dict[str, Any]] = []
    for row in rows:
        task_id = row["id"]
        spans = [tuple(span) for span in row.get("label", [])]
        replacement = replacements.get(task_id, {})
        remove = {tuple(span) for span in replacement.get("remove", [])}
        spans = [
            span for span in spans if span not in drop.get(task_id, set()) and span not in remove
        ]
        for span in drop.get(task_id, set()) | remove:
            actions.append({"task_id": task_id, "action": "remove_confirmed_span", "span": span})
        spans.extend(tuple(span) for span in replacement.get("add", []))
        for span in replacement.get("add", []):
            actions.append({"task_id": task_id, "action": "add_confirmed_span", "span": span})

        normalized: list[list[Any]] = []
        for start, end, label in spans:
            original = (start, end, label)
            while start < end and row["text"][start].isspace():
                start += 1
            while end > start and row["text"][end - 1].isspace():
                end -= 1
            if start >= end:
                actions.append(
                    {"task_id": task_id, "action": "remove_empty_span", "span": original}
                )
                continue
            if (start, end, label) != original:
                actions.append(
                    {
                        "task_id": task_id,
                        "action": "trim_boundary_whitespace",
                        "before": original,
                        "after": (start, end, label),
                    }
                )
            normalized.append([start, end, label])
        row["label"] = sorted(normalized)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    log_path.write_text(json.dumps(actions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
