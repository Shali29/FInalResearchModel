"""Convert Label Studio JSON exports into the project's canonical span format."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _active_annotations(task: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in task.get("annotations", []) if not item.get("was_cancelled", False)]


def _identity(data: dict[str, Any]) -> tuple[Any, ...]:
    """Build an exact provenance key for recovering IDs from older imports."""
    return (
        data.get("parent_record_id"),
        data.get("source_start"),
        data.get("source_end"),
        data.get("text"),
    )


def task_id_map(reference_path: Path) -> dict[tuple[Any, ...], str]:
    """Load stable research IDs from a generated Label Studio task file."""
    tasks = json.loads(reference_path.read_text(encoding="utf-8-sig"))
    mapping: dict[tuple[Any, ...], str] = {}
    for task in tasks:
        data = task.get("data", {})
        task_id = data.get("research_task_id") or task.get("id")
        if isinstance(task_id, str):
            mapping[_identity(data)] = task_id
    return mapping


def convert_label_studio_rows(
    tasks: list[dict[str, Any]],
    fallback_ids: dict[tuple[Any, ...], str] | None = None,
    allow_incomplete: bool = False,
    use_latest_annotation: bool = False,
) -> list[dict[str, Any]]:
    """Convert tasks with exactly one submitted annotation into Doccano-style rows."""
    converted: list[dict[str, Any]] = []
    errors: list[str] = []
    for position, task in enumerate(tasks, start=1):
        data = task.get("data", {})
        task_id = data.get("research_task_id")
        if not task_id and fallback_ids:
            task_id = fallback_ids.get(_identity(data))
        text = data.get("text")
        if not isinstance(task_id, str) or not task_id:
            errors.append(f"Export row {position}: missing data.research_task_id")
            continue
        if not isinstance(text, str):
            errors.append(f"{task_id}: missing text")
            continue
        annotations = _active_annotations(task)
        if not annotations and allow_incomplete:
            continue
        if len(annotations) > 1 and use_latest_annotation:
            annotators = {str(item.get("completed_by")) for item in annotations}
            if len(annotators) != 1:
                errors.append(
                    f"{task_id}: cannot select latest revision across multiple annotators"
                )
                continue
            annotations = [
                max(
                    annotations,
                    key=lambda item: str(item.get("updated_at") or item.get("created_at") or ""),
                )
            ]
        if len(annotations) != 1:
            errors.append(f"{task_id}: expected one active annotation, found {len(annotations)}")
            continue
        spans: list[list[Any]] = []
        for result in annotations[0].get("result", []):
            if result.get("type") != "labels":
                continue
            value = result.get("value", {})
            labels = value.get("labels", [])
            if len(labels) != 1:
                errors.append(f"{task_id}: an entity result must contain exactly one label")
                continue
            start, end = value.get("start"), value.get("end")
            if not isinstance(start, int) or not isinstance(end, int):
                errors.append(f"{task_id}: entity result has invalid offsets")
                continue
            spans.append([start, end, labels[0]])
        metadata = {
            key: value for key, value in data.items() if key not in {"research_task_id", "text"}
        }
        converted.append({"id": task_id, "text": text, "label": sorted(spans), "meta": metadata})
    if errors:
        raise ValueError("Label Studio conversion failed:\n" + "\n".join(errors[:100]))
    return converted


def convert_label_studio_file(
    input_path: Path,
    output_path: Path,
    reference_path: Path | None = None,
    allow_incomplete: bool = False,
    use_latest_annotation: bool = False,
) -> int:
    """Convert one UTF-8 Label Studio JSON export and return its task count."""
    tasks = json.loads(input_path.read_text(encoding="utf-8-sig"))
    if not isinstance(tasks, list):
        raise ValueError("Label Studio export must be a JSON list")
    fallback_ids = task_id_map(reference_path) if reference_path else None
    rows = convert_label_studio_rows(tasks, fallback_ids, allow_incomplete, use_latest_annotation)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(rows)
