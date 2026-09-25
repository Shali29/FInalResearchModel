"""Validate Doccano-style NER annotations before model use."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sri_lankan_legal_nlp.annotation.common import normalized_span


def validate_annotation_rows(
    rows: list[dict[str, Any]], allowed_labels: set[str], allow_overlaps: bool = False
) -> list[str]:
    """Return human-readable errors; an empty list means validation passed."""
    errors: list[str] = []
    seen_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=1):
        task_id = str(row.get("id", f"row-{row_number}"))
        if task_id in seen_ids:
            errors.append(f"{task_id}: duplicate task ID")
        seen_ids.add(task_id)
        text = row.get("text")
        if not isinstance(text, str):
            errors.append(f"{task_id}: text must be a string")
            continue
        spans: list[tuple[int, int, str]] = []
        for raw_span in row.get("label", []):
            try:
                start, end, label = normalized_span(raw_span)
            except ValueError as exc:
                errors.append(f"{task_id}: {exc}")
                continue
            if label not in allowed_labels:
                errors.append(f"{task_id}: unknown label {label!r}")
            if start < 0 or end > len(text) or start >= end:
                errors.append(
                    f"{task_id}: invalid offsets [{start}, {end}) for text length {len(text)}"
                )
                continue
            if text[start:end].strip() != text[start:end]:
                errors.append(f"{task_id}: span [{start}, {end}) includes boundary whitespace")
            spans.append((start, end, label))
        spans.sort()
        if not allow_overlaps:
            for previous, current in zip(spans, spans[1:], strict=False):
                if current[0] < previous[1]:
                    errors.append(f"{task_id}: overlapping spans {previous} and {current}")
    return errors


def validate_annotation_file(path: Path, labels_path: Path) -> list[str]:
    """Validate one UTF-8 JSONL export against the configured label list."""
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    labels = set(json.loads(labels_path.read_text(encoding="utf-8")))
    return validate_annotation_rows(rows, labels)
