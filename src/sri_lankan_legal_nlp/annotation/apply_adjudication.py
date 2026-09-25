"""Apply reviewed adjudication decisions without overwriting source annotations."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


def _jsonl(path: Path) -> dict[str, dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return {row["id"]: row for row in rows}


def apply_adjudication(
    first_path: Path,
    second_path: Path,
    decisions_path: Path,
    output_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    """Apply complete CSV decisions and retain their pending-human-approval provenance."""
    first, second = _jsonl(first_path), _jsonl(second_path)
    decisions = list(csv.DictReader(decisions_path.open(encoding="utf-8-sig", newline="")))
    by_task: dict[str, list[dict[str, str]]] = {}
    for row in decisions:
        by_task.setdefault(row["task_id"], []).append(row)
    output: list[dict[str, Any]] = []
    action_counts = {"keep": 0, "delete": 0, "modify": 0}
    errors: list[str] = []
    pending_human = any(
        "pending" in row["adjudicator"].lower() or "pending" in row["notes"].lower()
        for row in decisions
        if row["agreement_status"] == "disputed"
    )
    for task_id in sorted(set(first) & set(second)):
        left, right = first[task_id], second[task_id]
        if left["text"] != right["text"]:
            errors.append(f"{task_id}: annotator text mismatch")
            continue
        spans: set[tuple[int, int, str]] = set()
        for row in by_task.get(task_id, []):
            if row["agreement_status"] == "agreed":
                spans.add((int(row["start"]), int(row["end"]), row["label"]))
                continue
            action = row["adjudication_action"].strip().lower()
            if action not in action_counts:
                errors.append(f"{task_id}: invalid or missing action {action!r}")
                continue
            action_counts[action] += 1
            if action == "delete":
                continue
            try:
                start, end = int(row["adjudicated_start"]), int(row["adjudicated_end"])
            except ValueError:
                errors.append(f"{task_id}: {action} requires integer adjudicated offsets")
                continue
            label = row["adjudicated_label"].strip()
            stated_text = row["adjudicated_span_text"]
            actual_text = left["text"][start:end]
            if start < 0 or start >= end or end > len(left["text"]):
                errors.append(f"{task_id}: invalid adjudicated offsets [{start}, {end})")
            elif actual_text != stated_text:
                errors.append(
                    f"{task_id}: adjudicated text mismatch at [{start}, {end}): "
                    f"{stated_text!r} != {actual_text!r}"
                )
            elif not label:
                errors.append(f"{task_id}: {action} requires an adjudicated label")
            else:
                spans.add((start, end, label))
        output.append(
            {
                "id": task_id,
                "text": left["text"],
                "label": [list(span) for span in sorted(spans)],
                "meta": left.get("meta", {}),
                "consensus_status": (
                    "ai_assisted_adjudication_pending_human_approval"
                    if pending_human
                    else "human_adjudicated"
                ),
            }
        )
    if errors:
        raise ValueError("Adjudication validation failed:\n" + "\n".join(errors[:100]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in output:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    manifest = {
        "decision_file": str(decisions_path),
        "decision_file_sha256": hashlib.sha256(decisions_path.read_bytes()).hexdigest(),
        "decision_rows": len(decisions),
        "actions": action_counts,
        "task_count": len(output),
        "verification_status": ("pending_human_approval" if pending_human else "human_adjudicated"),
        "output_file": str(output_path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
