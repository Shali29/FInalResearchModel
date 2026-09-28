from __future__ import annotations

from sri_lankan_legal_nlp.amendments.pipeline import detect_operations, extract_candidates


def test_detects_sinhala_substitution() -> None:
    text = "116 වන වගන්තියෙහි වචන වෙනුවට අලුත් වචන ආදේශ කිරීමෙන්"
    assert detect_operations(text) == ["substitution"]


def test_detects_multiple_operations_as_ambiguous() -> None:
    row = {
        "record_id": "r1",
        "document_id": "a1",
        "amendment_number": "1/2020",
        "language": "si",
        "source_file": "a.pdf",
        "pdf_page_number": 2,
        "quality_status": "pending_review",
        "text": "8 වන වගන්තිය ඉවත් කිරීමෙන් සහ අලුත් වගන්තිය ඇතුළත් කිරීමෙන්",
    }
    event = extract_candidates(row)[0]
    assert event["operation"] is None
    assert event["ambiguity_reason"] == "multiple_operation_cues"
    assert set(event["operation_candidates"]) == {"insertion", "deletion"}


def test_does_not_claim_link_or_reconstructed_text() -> None:
    row = {
        "record_id": "r2",
        "document_id": "a2",
        "language": "si",
        "text": "109 වන වගන්තියට අලුත් උපවගන්තිය ඇතුළත් කිරීමෙන්",
    }
    event = extract_candidates(row)[0]
    assert event["original_text"] is None
    assert event["updated_text"] is None
    assert event["link_status"] == "reference_detected_not_linked"
    assert event["verification_status"] == "pending_manual_review"
