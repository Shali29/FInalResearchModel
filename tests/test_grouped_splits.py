"""Tests for Phase 5 grouped train, validation, test, and CV splits."""

from __future__ import annotations

import json
from pathlib import Path

from sri_lankan_legal_nlp.data.grouped_splits import create_grouped_splits


def test_grouped_splits_have_no_parent_leakage(tmp_path: Path) -> None:
    source = tmp_path / "corpus.jsonl"
    rows = []
    for index in range(30):
        language = "en" if index % 2 == 0 else "si"
        rows.append(
            {
                "id": f"task-{index}",
                "text": "legal text",
                "label": [[0, 5, "OFFENSE"]],
                "meta": {
                    "language": language,
                    "document_type": "penal_code",
                    "parent_record_id": f"provision-{index}",
                },
            }
        )
    source.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    report = create_grouped_splits(source, tmp_path / "splits", seed=11)

    assert sum(report["task_counts"].values()) == 30
    assert 19 <= report["task_counts"]["train"] <= 22
    assert 4 <= report["task_counts"]["validation"] <= 6
    assert 4 <= report["task_counts"]["test"] <= 6
    assert report["leakage_detected"] is False
    assert all(not missing for missing in report["missing_features"].values())
