"""Tests for Phase 4 blank-task preparation and annotation safeguards."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sri_lankan_legal_nlp.annotation.agreement import span_prf, token_kappa
from sri_lankan_legal_nlp.annotation.agreement_report import calculate_agreement
from sri_lankan_legal_nlp.annotation.label_studio import convert_label_studio_rows
from sri_lankan_legal_nlp.annotation.prepare import _split_text
from sri_lankan_legal_nlp.annotation.validation import validate_annotation_rows

ROOT = Path(__file__).resolve().parents[1]
ANNOTATION = ROOT / "data" / "annotation"
LABELS = {
    "FUNDAMENTAL_RIGHT",
    "OFFENSE",
    "PENALTY",
    "CONSTITUTIONAL_BODY",
    "TEMPORAL_ENTITY",
}


def test_text_segments_preserve_exact_source_offsets() -> None:
    text = "First paragraph.\n\nදෙවන ඡේදය."
    for segment, start, end in _split_text(text, 1800):
        assert segment == text[start:end]


def test_invalid_and_overlapping_spans_are_rejected() -> None:
    rows = [
        {
            "id": "one",
            "text": "Parliament 2026",
            "label": [[0, 10, "CONSTITUTIONAL_BODY"], [5, 15, "TEMPORAL_ENTITY"]],
        }
    ]
    errors = validate_annotation_rows(rows, LABELS)
    assert any("overlapping" in error for error in errors)


def test_agreement_reports_exact_spans_and_kappa() -> None:
    spans = [[0, 10, "CONSTITUTIONAL_BODY"]]
    assert span_prf(spans, spans)["f1"] == 1.0
    assert token_kappa("Parliament acts", spans, spans) == 1.0


@pytest.mark.skipif(
    not (ANNOTATION / "doccano_pilot_tasks.jsonl").exists(), reason="Phase 4 not run"
)
def test_generated_tasks_are_blank_and_traceable() -> None:
    rows = [
        json.loads(line)
        for line in (ANNOTATION / "doccano_pilot_tasks.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line
    ]
    assert len(rows) == 500
    assert all(row["label"] == [] for row in rows)
    assert all(row["meta"]["parent_record_id"] for row in rows)
    assert all(row["meta"]["source_file"] and row["meta"]["pdf_page_number"] >= 1 for row in rows)
    shared = json.loads((ANNOTATION / "label_studio_shared_tasks.json").read_text(encoding="utf-8"))
    assert len(shared) == 50
    assert all(task["data"]["research_task_id"] for task in shared)


def test_label_studio_conversion_preserves_task_identity() -> None:
    tasks = [
        {
            "data": {"research_task_id": "task-1", "text": "Parliament acts", "language": "en"},
            "annotations": [
                {
                    "result": [
                        {
                            "type": "labels",
                            "value": {
                                "start": 0,
                                "end": 10,
                                "text": "Parliament",
                                "labels": ["CONSTITUTIONAL_BODY"],
                            },
                        }
                    ]
                }
            ],
        }
    ]
    rows = convert_label_studio_rows(tasks)
    assert rows[0]["id"] == "task-1"
    assert rows[0]["label"] == [[0, 10, "CONSTITUTIONAL_BODY"]]


def test_aggregate_agreement_uses_only_shared_ids(tmp_path: Path) -> None:
    row = {
        "id": "shared-1",
        "text": "Parliament acts",
        "label": [[0, 10, "CONSTITUTIONAL_BODY"]],
        "meta": {},
    }
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    serialized = json.dumps(row) + "\n"
    first.write_text(serialized, encoding="utf-8")
    second.write_text(serialized, encoding="utf-8")
    report = calculate_agreement(first, second)
    assert report["shared_task_count"] == 1
    assert report["exact_span_f1"] == 1.0
    assert report["token_cohen_kappa"] == 1.0


@pytest.mark.skipif(
    not (ANNOTATION / "label_studio_enriched_pilot_tasks.json").exists(),
    reason="enriched pilot not generated",
)
def test_enriched_pilot_is_blank_balanced_and_traceable() -> None:
    tasks = json.loads(
        (ANNOTATION / "label_studio_enriched_pilot_tasks.json").read_text(encoding="utf-8")
    )
    assert len(tasks) == 500
    assert all(task["data"]["research_task_id"] for task in tasks)
    assert all("annotations" not in task and "predictions" not in task for task in tasks)
