from __future__ import annotations

import json
from pathlib import Path

from sri_lankan_legal_nlp.simplification.pipeline import (
    load_verified_glossary,
    prepare_review_record,
    text_is_usable,
)


def test_only_verified_glossary_entries_are_loaded(tmp_path: Path) -> None:
    path = tmp_path / "glossary.jsonl"
    rows = [
        {"source_term": "A", "plain_sinhala_explanation": "B", "review_status": "draft"},
        {
            "source_term": "C",
            "plain_sinhala_explanation": "D",
            "review_status": "verified_by_legal_expert",
        },
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    assert load_verified_glossary(path) == {"C": "D"}


def test_english_review_task_does_not_invent_translation() -> None:
    task = prepare_review_record(
        {"record_id": "r1", "language": "en", "text": "Original legal text"}, {}
    )
    assert task["translated_sinhala"] is None
    assert task["simplified_sinhala"] is None
    assert task["translation_status"] == "pending_human_translation"


def test_sinhala_source_is_preserved_but_not_claimed_as_simplified() -> None:
    task = prepare_review_record(
        {"record_id": "r2", "language": "si", "text": "සිංහල නීති පාඨය"}, {}
    )
    assert task["translated_sinhala"] == "සිංහල නීති පාඨය"
    assert task["simplified_sinhala"] is None
    assert task["review_status"] == "pending_expert_review"


def test_mojibake_sinhala_is_rejected() -> None:
    assert not text_is_usable({"language": "si", "text": "à¶±à·“à¶­à·’"})
    assert text_is_usable({"language": "si", "text": "සිංහල නීති පාඨය"})
