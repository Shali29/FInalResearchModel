"""Tests for conservative Phase 3 structural alignment."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sri_lankan_legal_nlp.data.alignment import align_document_pair
from sri_lankan_legal_nlp.data.models import AlignmentIssue, AlignmentRecord

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "aligned"


def _page(record_id: str, document_id: str, language: str, page: int) -> dict:
    return {
        "record_id": record_id,
        "document_id": document_id,
        "language": language,
        "pdf_page_number": page,
    }


def _candidate(candidate_id: str, document_id: str, language: str, number: str, page: int) -> dict:
    return {
        "candidate_id": candidate_id,
        "document_id": document_id,
        "document_type": "constitution",
        "language": language,
        "provision_type": "article",
        "provision_number": number,
        "source_file": f"{document_id}.pdf",
        "pdf_page_number": page,
    }


def test_only_unique_exact_keys_are_aligned() -> None:
    records = [_page("en-p1", "en-doc", "en", 1), _page("si-p1", "si-doc", "si", 1)]
    candidates = [
        _candidate("en-12", "en-doc", "en", "12", 1),
        _candidate("si-12", "si-doc", "si", "12", 1),
    ]
    alignments, issues = align_document_pair(
        candidates, records, "en-doc", "si-doc", "constitution"
    )
    assert len(alignments) == 1
    assert not issues
    assert alignments[0].provision_number == "12"
    assert alignments[0].manual_review_status == "pending_review"


def test_duplicates_are_reported_not_forced() -> None:
    records = [_page("en-p1", "en-doc", "en", 1), _page("si-p1", "si-doc", "si", 1)]
    candidates = [
        _candidate("en-a", "en-doc", "en", "12", 1),
        _candidate("en-b", "en-doc", "en", "12", 1),
        _candidate("si-a", "si-doc", "si", "12", 1),
    ]
    alignments, issues = align_document_pair(
        candidates, records, "en-doc", "si-doc", "constitution"
    )
    assert not alignments
    assert len(issues) == 1
    assert issues[0].issue_type == "duplicate"


@pytest.mark.skipif(not (OUTPUT / "alignments.jsonl").exists(), reason="alignment not run")
def test_phase3_artifacts_validate() -> None:
    alignment_rows = [
        json.loads(line)
        for line in (OUTPUT / "alignments.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    issue_rows = [
        json.loads(line)
        for line in (OUTPUT / "alignment_issues.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert alignment_rows
    assert len({row["alignment_id"] for row in alignment_rows}) == len(alignment_rows)
    assert all(AlignmentRecord.model_validate(row) for row in alignment_rows)
    assert all(AlignmentIssue.model_validate(row) for row in issue_rows)
    assert all(row["manual_review_status"] == "pending_review" for row in alignment_rows)
