"""Validated records written by the legal-document extraction pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Forbid accidental schema drift in research artifacts."""

    model_config = ConfigDict(extra="forbid")


class DocumentSpec(StrictModel):
    """Researcher-controlled metadata for one known source PDF."""

    document_id: str
    document_type: Literal["constitution", "penal_code", "amendment"]
    document_title: str
    language: Literal["en", "si"]
    amendment_number: str | None = None
    edition_note: str
    corpus_role: str | None = None


class SourceManifestRecord(StrictModel):
    """Immutable identity and processing status of a source PDF."""

    document_id: str
    document_type: str
    document_title: str
    language: str
    amendment_number: str | None
    edition_note: str
    source_file: str
    source_path: str
    source_sha256: str
    file_size_bytes: int
    pdf_page_count: int
    processed_page_count: int
    embedded_text_pages: int
    ocr_pages: int
    pages_requiring_ocr: int
    rejected_pages: int
    extraction_status: Literal["complete", "partial", "failed"]


class ExtractionRecord(StrictModel):
    """One page-bounded text unit with complete provenance."""

    record_id: str
    document_id: str
    document_type: str
    document_title: str
    language: str
    provision_type: Literal["article", "section", "page_segment"]
    provision_number: str | None
    subsection: str | None = None
    text: str
    source_file: str
    source_sha256: str
    pdf_page_number: int = Field(ge=1)
    printed_page_label: str | None = None
    amendment_number: str | None
    extraction_method: Literal["embedded_text", "ocr_eng", "ocr_sin", "none"]
    quality_status: Literal["verified", "pending_review", "low_quality", "rejected"]
    verification_notes: str | None


class PageQualityRecord(StrictModel):
    """Measurable extraction diagnostics for one physical PDF page."""

    document_id: str
    source_file: str
    language: str
    pdf_page_number: int
    extraction_method: str
    embedded_non_whitespace_characters: int
    final_non_whitespace_characters: int
    expected_script_ratio: float
    replacement_character_ratio: float
    repeated_boundary_lines_removed: int
    quality_status: str
    warnings: list[str]


class ProvisionCandidate(StrictModel):
    """Conservative heading candidate requiring structural or manual confirmation."""

    candidate_id: str
    document_id: str
    document_type: str
    language: str
    provision_type: Literal["article", "section"]
    provision_number: str
    source_file: str
    source_sha256: str
    pdf_page_number: int
    candidate_method: Literal["explicit_label", "numbered_line"]
    matched_text: str
    verification_status: Literal["pending_review"] = "pending_review"


class AlignmentRecord(StrictModel):
    """One conservative English-Sinhala provision alignment candidate."""

    alignment_id: str
    english_record_id: str
    sinhala_record_id: str
    english_candidate_id: str
    sinhala_candidate_id: str
    document_type: Literal["constitution", "penal_code", "amendment"]
    provision_type: Literal["article", "section"]
    provision_number: str
    subsection: str | None = None
    amendment_number: str | None = None
    alignment_method: Literal["exact_unique_structural_match"]
    confidence_score: float = Field(ge=0.0, le=1.0)
    manual_review_status: Literal["pending_review", "verified", "rejected"]
    english_source_file: str
    english_pdf_page_number: int = Field(ge=1)
    sinhala_source_file: str
    sinhala_pdf_page_number: int = Field(ge=1)


class AlignmentIssue(StrictModel):
    """Traceable reason why a provision candidate was not automatically aligned."""

    issue_id: str
    issue_type: Literal["unmatched", "duplicate", "conflicting", "low_confidence"]
    language: Literal["en", "si", "bilingual"]
    document_type: str
    provision_type: str
    provision_number: str
    amendment_number: str | None = None
    candidate_ids: list[str]
    record_ids: list[str]
    source_files: list[str]
    pdf_page_numbers: list[int]
    details: str
    manual_review_status: Literal["pending_review"] = "pending_review"
