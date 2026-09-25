"""Unit tests for conservative Phase 2 extraction helpers."""

from __future__ import annotations

from sri_lankan_legal_nlp.data.extraction import (
    normalize_legal_text,
    provision_candidates,
    provision_hint,
    remove_repeated_boundaries,
    script_ratio,
)
from sri_lankan_legal_nlp.data.models import ExtractionRecord


def test_unicode_normalization_preserves_sinhala_and_legal_markers() -> None:
    original = "  12. අයිතිය (1) — නොකළ යුතුය.  \r\n\r\n\r\nNext"
    normalized = normalize_legal_text(original, "NFC")
    assert "අයිතිය" in normalized
    assert "12." in normalized
    assert "(1)" in normalized
    assert "—" in normalized
    assert "නොකළ" in normalized
    assert "\n\n\n" not in normalized


def test_expected_script_ratio_detects_legacy_latin_glyph_text() -> None:
    assert script_ratio("මෙය සිංහල පාඨයකි", "si") == 1.0
    assert script_ratio("YS% ,xld legacy font", "si") == 0.0
    assert script_ratio("Section 53 of the Penal Code", "en") == 1.0


def test_only_explicit_provision_headings_are_classified() -> None:
    assert provision_hint("Article 12\nEquality", "constitution") == ("article", "12")
    assert provision_hint("Section 53(1)\nPenalty", "penal_code") == ("section", "53(1)")
    assert provision_hint("(1) A person shall...", "penal_code") == ("page_segment", None)


def test_boundary_removal_is_limited_to_page_edges() -> None:
    text = (
        "Repeated header\nFirst paragraph\nSecond line\nRepeated header\n"
        "Fourth line\nFifth line\nLast line"
    )
    cleaned, removed = remove_repeated_boundaries(text, {"Repeated header"})
    assert removed == 1
    assert "Repeated header" in cleaned
    assert cleaned.startswith("First paragraph")


def test_numbered_provision_candidates_are_pending_not_verified() -> None:
    record = ExtractionRecord(
        record_id="test-p0001-a",
        document_id="test",
        document_type="penal_code",
        document_title="Test",
        language="en",
        provision_type="page_segment",
        provision_number=None,
        text="Short title\n1. This Ordinance may be cited...\n(1) A subsection",
        source_file="test.pdf",
        source_sha256="0" * 64,
        pdf_page_number=1,
        amendment_number=None,
        extraction_method="embedded_text",
        quality_status="pending_review",
        verification_notes=None,
    )
    candidates = provision_candidates(record)
    assert [(item.provision_type, item.provision_number) for item in candidates] == [
        ("section", "1")
    ]
    assert candidates[0].verification_status == "pending_review"
