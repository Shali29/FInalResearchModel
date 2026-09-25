"""Validation tests for real Phase 2 artifacts when they exist."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sri_lankan_legal_nlp.data.models import (
    ExtractionRecord,
    ProvisionCandidate,
    SourceManifestRecord,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "extracted"


def jsonl_rows(path: Path) -> list[dict]:
    """Load every non-empty JSONL row as an object."""
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


@pytest.mark.skipif(not (OUTPUT / "manifest.jsonl").exists(), reason="extraction not run")
def test_manifest_and_records_validate_and_cover_all_pages() -> None:
    manifest_rows = jsonl_rows(OUTPUT / "manifest.jsonl")
    manifests = [SourceManifestRecord.model_validate(row) for row in manifest_rows]
    records = [ExtractionRecord.model_validate(row) for row in jsonl_rows(OUTPUT / "records.jsonl")]
    assert len(manifests) == 12
    assert sum(item.pdf_page_count for item in manifests) == len(records)
    assert len({item.record_id for item in records}) == len(records)
    assert all(item.language in {"en", "si"} for item in records)


@pytest.mark.skipif(not (OUTPUT / "manifest.jsonl").exists(), reason="extraction not run")
def test_original_pdf_checksums_are_unchanged() -> None:
    manifest_rows = jsonl_rows(OUTPUT / "manifest.jsonl")
    manifests = [SourceManifestRecord.model_validate(row) for row in manifest_rows]
    for item in manifests:
        digest = hashlib.sha256(Path(item.source_path).read_bytes()).hexdigest()
        assert digest == item.source_sha256


@pytest.mark.skipif(not (OUTPUT / "records.jsonl").exists(), reason="extraction not run")
def test_sinhala_records_are_utf8_and_contain_no_replacement_characters() -> None:
    records = [ExtractionRecord.model_validate(row) for row in jsonl_rows(OUTPUT / "records.jsonl")]
    usable_sinhala = [
        item for item in records if item.language == "si" and item.quality_status != "rejected"
    ]
    assert usable_sinhala
    assert all("\ufffd" not in item.text for item in usable_sinhala)


@pytest.mark.skipif(
    not (OUTPUT / "provision_candidates.jsonl").exists(), reason="extraction not run"
)
def test_provision_candidates_are_unverified_and_traceable() -> None:
    rows = jsonl_rows(OUTPUT / "provision_candidates.jsonl")
    candidates = [ProvisionCandidate.model_validate(row) for row in rows]
    assert candidates
    assert all(item.verification_status == "pending_review" for item in candidates)
    assert all(item.source_sha256 and item.pdf_page_number >= 1 for item in candidates)
