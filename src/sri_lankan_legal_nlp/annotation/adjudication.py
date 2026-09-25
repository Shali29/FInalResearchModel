"""Create a human adjudication worksheet from two canonical annotation files."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from sri_lankan_legal_nlp.annotation.common import normalized_span


def _rows(path: Path) -> dict[str, dict[str, Any]]:
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return {record["id"]: record for record in records}


def write_adjudication_sheet(first_path: Path, second_path: Path, output_path: Path) -> int:
    """Write one row per agreed or disputed exact span and return disagreement count."""
    first, second = _rows(first_path), _rows(second_path)
    shared = sorted(set(first) & set(second))
    fields = [
        "task_id",
        "language",
        "document_type",
        "source_file",
        "pdf_page_number",
        "start",
        "end",
        "span_text",
        "label",
        "annotator_1",
        "annotator_2",
        "agreement_status",
        "adjudicated_start",
        "adjudicated_end",
        "adjudicated_span_text",
        "adjudicated_label",
        "adjudication_action",
        "adjudicator",
        "adjudication_date",
        "notes",
    ]
    disagreements = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for task_id in shared:
            left, right = first[task_id], second[task_id]
            if left["text"] != right["text"]:
                raise ValueError(f"Text mismatch for {task_id}")
            left_spans = {normalized_span(span) for span in left.get("label", [])}
            right_spans = {normalized_span(span) for span in right.get("label", [])}
            for start, end, label in sorted(left_spans | right_spans):
                in_left, in_right = (
                    (start, end, label) in left_spans,
                    (start, end, label) in right_spans,
                )
                agreed = in_left and in_right
                if not agreed:
                    disagreements += 1
                meta = left.get("meta", {})
                writer.writerow(
                    {
                        "task_id": task_id,
                        "language": meta.get("language", ""),
                        "document_type": meta.get("document_type", ""),
                        "source_file": meta.get("source_file", ""),
                        "pdf_page_number": meta.get("pdf_page_number", ""),
                        "start": start,
                        "end": end,
                        "span_text": left["text"][start:end],
                        "label": label,
                        "annotator_1": "yes" if in_left else "no",
                        "annotator_2": "yes" if in_right else "no",
                        "agreement_status": "agreed" if agreed else "disputed",
                    }
                )
    return disagreements
