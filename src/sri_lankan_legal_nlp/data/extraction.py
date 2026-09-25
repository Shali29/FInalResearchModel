"""Conservative PDF extraction with provenance and OCR quality gates."""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import os
import re
import shutil
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pymupdf
import pytesseract
from PIL import Image

from sri_lankan_legal_nlp.data.config import DataConfig, load_data_config
from sri_lankan_legal_nlp.data.models import (
    DocumentSpec,
    ExtractionRecord,
    PageQualityRecord,
    ProvisionCandidate,
    SourceManifestRecord,
)

LOGGER = logging.getLogger(__name__)
SINHALA_RE = re.compile(r"[\u0D80-\u0DFF]")
LATIN_RE = re.compile(r"[A-Za-z]")
REPLACEMENT = "\ufffd"
EXPLICIT_PROVISION_RE = re.compile(
    r"(?im)^\s*(Article|Section)\s+([0-9]+(?:[A-Z]|\s*[A-Z])?(?:\([0-9A-Za-z]+\))*)(?=\s|$)"
)
NUMBERED_PROVISION_RE = re.compile(r"(?m)^\s*([0-9]{1,3}[A-Z]{0,3})\.\s+(?=\S)")
PROTECTED_BOUNDARY_RE = re.compile(
    r"(?i)\b(article|section|chapter|schedule|amendment|act\s+no\.)\b|^\s*\d+[A-Z]?(?:\.|\s)"
)


@dataclass
class PageDraft:
    """Mutable page state retained only while one document is processed."""

    page_number: int
    embedded_text: str
    final_text: str
    extraction_method: str
    warnings: list[str]
    expected_script_ratio: float
    replacement_ratio: float
    removed_boundary_lines: int = 0


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Calculate a source checksum without loading the whole PDF into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_legal_text(text: str, normalization: str) -> str:
    """Normalize Unicode and whitespace without changing legal punctuation or numbering."""
    normalized = unicodedata.normalize(
        normalization, text.replace("\r\n", "\n").replace("\r", "\n")
    )
    lines = [line.rstrip() for line in normalized.split("\n")]
    output: list[str] = []
    blank_count = 0
    for line in lines:
        if line:
            blank_count = 0
            output.append(line)
        else:
            blank_count += 1
            if blank_count <= 1:
                output.append("")
    return "\n".join(output).strip()


def non_whitespace_count(text: str) -> int:
    """Count visible characters as a simple extraction-coverage signal."""
    return sum(not char.isspace() for char in text)


def script_ratio(text: str, language: str) -> float:
    """Calculate expected letters as a fraction of Latin plus Sinhala letters."""
    sinhala = len(SINHALA_RE.findall(text))
    latin = len(LATIN_RE.findall(text))
    denominator = sinhala + latin
    if denominator == 0:
        return 0.0
    return (sinhala if language == "si" else latin) / denominator


def replacement_ratio(text: str) -> float:
    """Calculate Unicode replacement characters per visible character."""
    visible = max(non_whitespace_count(text), 1)
    return text.count(REPLACEMENT) / visible


def embedded_text_is_usable(
    text: str, spec: DocumentSpec, config: DataConfig
) -> tuple[bool, list[str]]:
    """Reject empty, corrupt, or wrong-script embedded text before OCR fallback."""
    warnings: list[str] = []
    visible = non_whitespace_count(text)
    ratio = script_ratio(text, spec.language)
    replacements = replacement_ratio(text)
    if visible < config.extraction.minimum_non_whitespace_characters_per_page:
        warnings.append("insufficient_embedded_text")
    if spec.language == "si" and visible >= 40 and ratio < 0.40:
        warnings.append("sinhala_unicode_ratio_too_low_possible_legacy_font")
    if replacements > config.extraction.maximum_replacement_character_ratio:
        warnings.append("replacement_character_ratio_too_high")
    return not warnings, warnings


def configure_tesseract(config: DataConfig) -> set[str]:
    """Return installed OCR languages, or an empty set when Tesseract is unavailable."""
    executable = Path(config.extraction.tesseract_executable)
    if not executable.is_file() and shutil.which("tesseract") is None:
        return set()
    if executable.is_file():
        pytesseract.pytesseract.tesseract_cmd = str(executable)
    tessdata = Path(config.extraction.tessdata_directory).resolve()
    if not tessdata.is_dir():
        LOGGER.error("Configured tessdata directory does not exist: %s", tessdata)
        return set()
    os.environ["TESSDATA_PREFIX"] = str(tessdata)
    try:
        return set(pytesseract.get_languages(config=""))
    except pytesseract.TesseractError:
        LOGGER.exception("Unable to query Tesseract languages")
        return set()


def ocr_page(page: pymupdf.Page, language: str, dpi: int) -> str:
    """Render and OCR one page; callers must verify language availability first."""
    pixmap = page.get_pixmap(dpi=dpi, alpha=False)
    mode = "RGB" if pixmap.n == 3 else "RGBA"
    image = Image.frombytes(mode, (pixmap.width, pixmap.height), pixmap.samples)
    return pytesseract.image_to_string(image, lang=language)


def boundary_candidates(text: str) -> tuple[set[str], set[str]]:
    """Return conservative top/bottom line candidates for repeated-header detection."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return set(), set()
    return set(lines[:3]), set(lines[-3:])


def repeated_boundary_lines(pages: list[PageDraft], config: DataConfig) -> set[str]:
    """Find exact repeated boundary lines while protecting legal-structure lines."""
    counts: Counter[str] = Counter()
    for page in pages:
        top, bottom = boundary_candidates(page.final_text)
        counts.update(top | bottom)
    threshold = max(
        config.extraction.repeated_boundary_line_minimum_pages,
        int(len(pages) * config.extraction.repeated_boundary_line_minimum_fraction + 0.999),
    )
    return {
        line
        for line, count in counts.items()
        if count >= threshold and len(line) >= 4 and not PROTECTED_BOUNDARY_RE.search(line)
    }


def remove_repeated_boundaries(text: str, repeated: set[str]) -> tuple[str, int]:
    """Remove only exact repeats occurring among the first/last three non-empty lines."""
    lines = text.splitlines()
    nonempty_indices = [index for index, line in enumerate(lines) if line.strip()]
    eligible = set(nonempty_indices[:3] + nonempty_indices[-3:])
    removed = 0
    kept: list[str] = []
    for index, line in enumerate(lines):
        if index in eligible and line.strip() in repeated:
            removed += 1
            continue
        kept.append(line)
    return "\n".join(kept).strip(), removed


def provision_hint(text: str, document_type: str) -> tuple[str, str | None]:
    """Extract only explicit Article/Section headings; uncertain numbers remain page segments."""
    match = EXPLICIT_PROVISION_RE.search(text)
    if match:
        return match.group(1).lower(), re.sub(r"\s+", "", match.group(2))
    expected = "article" if document_type == "constitution" else "section"
    return "page_segment", None if expected else None


def provision_candidates(record: ExtractionRecord) -> list[ProvisionCandidate]:
    """Find explicit labels and conservative numbered-line headings on one page."""
    if record.quality_status == "rejected" or record.document_type == "amendment":
        expected_type = "section"
    else:
        expected_type = "article" if record.document_type == "constitution" else "section"
    candidates: list[ProvisionCandidate] = []
    seen: set[tuple[str, str]] = set()
    patterns = (
        (EXPLICIT_PROVISION_RE, "explicit_label"),
        (NUMBERED_PROVISION_RE, "numbered_line"),
    )
    for pattern, method in patterns:
        for match in pattern.finditer(record.text):
            if method == "explicit_label":
                provision_type = match.group(1).lower()
                number = re.sub(r"\s+", "", match.group(2))
            else:
                provision_type = expected_type
                number = match.group(1)
            key = (provision_type, number)
            if key in seen:
                continue
            seen.add(key)
            matched = match.group(0).strip()
            digest = hashlib.sha256(
                f"{record.record_id}|{provision_type}|{number}|{method}".encode()
            ).hexdigest()[:12]
            candidates.append(
                ProvisionCandidate(
                    candidate_id=f"candidate-{digest}",
                    document_id=record.document_id,
                    document_type=record.document_type,
                    language=record.language,
                    provision_type=provision_type,
                    provision_number=number,
                    source_file=record.source_file,
                    source_sha256=record.source_sha256,
                    pdf_page_number=record.pdf_page_number,
                    candidate_method=method,
                    matched_text=matched,
                )
            )
    return candidates


def stable_record_id(document_id: str, page_number: int, text: str) -> str:
    """Create a deterministic ID tied to page position and extracted content."""
    text_digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{document_id}-p{page_number:04d}-{text_digest}"


def write_jsonl(path: Path, records: list[Any]) -> None:
    """Write model or mapping records as UTF-8 JSON Lines."""
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            payload = record.model_dump(mode="json") if hasattr(record, "model_dump") else record
            stream.write(json.dumps(payload, ensure_ascii=False) + "\n")


def process_document(
    pdf_path: Path,
    spec: DocumentSpec,
    config: DataConfig,
    output_root: Path,
    available_ocr_languages: set[str],
) -> tuple[SourceManifestRecord, list[ExtractionRecord], list[PageQualityRecord]]:
    """Extract one PDF into page-bounded records and diagnostics."""
    source_hash = sha256_file(pdf_path)
    drafts: list[PageDraft] = []
    ocr_cache_directory = output_root / "ocr_cache" / spec.document_id
    with pymupdf.open(pdf_path) as document:
        page_count = document.page_count
        for index, page in enumerate(document):
            embedded = normalize_legal_text(
                page.get_text("text"), config.extraction.unicode_normalization
            )
            usable, warnings = embedded_text_is_usable(embedded, spec, config)
            final_text = embedded
            method = "embedded_text" if usable else "none"
            ocr_language = config.extraction.ocr_languages[spec.language]
            if not usable and config.extraction.ocr_fallback:
                if ocr_language in available_ocr_languages:
                    try:
                        cache_path = ocr_cache_directory / f"page_{index + 1:04d}.txt"
                        if cache_path.is_file():
                            candidate = cache_path.read_text(encoding="utf-8")
                            warnings.append("ocr_cache_used")
                        else:
                            LOGGER.info(
                                "OCR %s page %s/%s (%s)",
                                pdf_path.name,
                                index + 1,
                                page_count,
                                ocr_language,
                            )
                            candidate = normalize_legal_text(
                                ocr_page(page, ocr_language, config.extraction.ocr_dpi),
                                config.extraction.unicode_normalization,
                            )
                            ocr_cache_directory.mkdir(parents=True, exist_ok=True)
                            cache_path.write_text(candidate, encoding="utf-8")
                        candidate_usable, candidate_warnings = embedded_text_is_usable(
                            candidate, spec, config
                        )
                        if candidate_usable:
                            final_text = candidate
                            method = f"ocr_{ocr_language}"
                            warnings = ["embedded_text_replaced_by_ocr"]
                        else:
                            warnings.extend(f"ocr_{warning}" for warning in candidate_warnings)
                    except (pytesseract.TesseractError, OSError):
                        LOGGER.exception("OCR failed for %s page %s", pdf_path.name, index + 1)
                        warnings.append("ocr_execution_failed")
                else:
                    warnings.append(f"ocr_language_unavailable:{ocr_language}")
            drafts.append(
                PageDraft(
                    page_number=index + 1,
                    embedded_text=embedded,
                    final_text=final_text if method != "none" else "",
                    extraction_method=method,
                    warnings=sorted(set(warnings)),
                    expected_script_ratio=script_ratio(final_text, spec.language),
                    replacement_ratio=replacement_ratio(final_text),
                )
            )

    repeated = repeated_boundary_lines(drafts, config)
    records: list[ExtractionRecord] = []
    quality_records: list[PageQualityRecord] = []
    text_directory = output_root / "text" / spec.language
    text_directory.mkdir(parents=True, exist_ok=True)
    document_text_pages: list[str] = []
    for draft in drafts:
        cleaned, removed = remove_repeated_boundaries(draft.final_text, repeated)
        draft.final_text = cleaned
        draft.removed_boundary_lines = removed
        if removed:
            draft.warnings.append("repeated_boundary_line_removed")
        if draft.extraction_method == "none" or not cleaned:
            status = "rejected"
        elif set(draft.warnings) - {"repeated_boundary_line_removed"}:
            status = (
                "pending_review" if draft.extraction_method.startswith("ocr_") else "low_quality"
            )
        else:
            status = "pending_review"
        provision_type, provision_number = provision_hint(cleaned, spec.document_type)
        record = ExtractionRecord(
            record_id=stable_record_id(spec.document_id, draft.page_number, cleaned),
            document_id=spec.document_id,
            document_type=spec.document_type,
            document_title=spec.document_title,
            language=spec.language,
            provision_type=provision_type,
            provision_number=provision_number,
            text=cleaned,
            source_file=pdf_path.name,
            source_sha256=source_hash,
            pdf_page_number=draft.page_number,
            amendment_number=spec.amendment_number,
            extraction_method=draft.extraction_method,
            quality_status=status,
            verification_notes="; ".join(sorted(set(draft.warnings))) or None,
        )
        records.append(record)
        quality_records.append(
            PageQualityRecord(
                document_id=spec.document_id,
                source_file=pdf_path.name,
                language=spec.language,
                pdf_page_number=draft.page_number,
                extraction_method=draft.extraction_method,
                embedded_non_whitespace_characters=non_whitespace_count(draft.embedded_text),
                final_non_whitespace_characters=non_whitespace_count(cleaned),
                expected_script_ratio=round(script_ratio(cleaned, spec.language), 6),
                replacement_character_ratio=round(replacement_ratio(cleaned), 8),
                repeated_boundary_lines_removed=removed,
                quality_status=status,
                warnings=sorted(set(draft.warnings)),
            )
        )
        document_text_pages.append(f"[[PDF_PAGE_{draft.page_number}]]\n{cleaned}")

    text_path = text_directory / f"{spec.document_id}.txt"
    text_path.write_text("\n\n".join(document_text_pages) + "\n", encoding="utf-8")
    embedded_pages = sum(
        item.extraction_method == "embedded_text" and item.quality_status != "rejected"
        for item in records
    )
    ocr_pages = sum(
        item.extraction_method.startswith("ocr_") and item.quality_status != "rejected"
        for item in records
    )
    needs_ocr = sum(item.extraction_method == "none" for item in records)
    rejected_pages = sum(item.quality_status == "rejected" for item in records)
    status = (
        "complete" if rejected_pages == 0 else "partial" if embedded_pages + ocr_pages else "failed"
    )
    manifest = SourceManifestRecord(
        document_id=spec.document_id,
        document_type=spec.document_type,
        document_title=spec.document_title,
        language=spec.language,
        amendment_number=spec.amendment_number,
        edition_note=spec.edition_note,
        source_file=pdf_path.name,
        source_path=str(pdf_path.resolve()),
        source_sha256=source_hash,
        file_size_bytes=pdf_path.stat().st_size,
        pdf_page_count=page_count,
        processed_page_count=len(drafts),
        embedded_text_pages=embedded_pages,
        ocr_pages=ocr_pages,
        pages_requiring_ocr=needs_ocr,
        rejected_pages=rejected_pages,
        extraction_status=status,
    )
    return manifest, records, quality_records


def sentence_count(text: str) -> int:
    """Return a conservative punctuation-delimited sentence estimate."""
    return len([part for part in re.split(r"(?<=[.!?])\s+|\n{2,}", text) if part.strip()])


def token_count(text: str) -> int:
    """Count Unicode alphanumeric token spans; this is descriptive, not model tokenization."""
    return len(re.findall(r"[^\W_]+(?:['’][^\W_]+)?", text, flags=re.UNICODE))


def write_outputs(
    output_root: Path,
    manifests: list[SourceManifestRecord],
    records: list[ExtractionRecord],
    quality: list[PageQualityRecord],
) -> None:
    """Validate and write all Phase 2 artifacts."""
    output_root.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_root / "manifest.jsonl", manifests)
    write_jsonl(output_root / "records.jsonl", records)
    uncertain = [record for record in records if record.quality_status != "verified"]
    rejected = [record for record in records if record.quality_status == "rejected"]
    write_jsonl(output_root / "uncertain_segments.jsonl", uncertain)
    write_jsonl(output_root / "rejected_segments.jsonl", rejected)
    write_jsonl(output_root / "page_quality.jsonl", quality)
    candidates = [candidate for record in records for candidate in provision_candidates(record)]
    write_jsonl(output_root / "provision_candidates.jsonl", candidates)

    with (output_root / "extraction_quality.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as stream:
        fieldnames = list(PageQualityRecord.model_fields)
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for item in quality:
            row = item.model_dump(mode="json")
            row["warnings"] = "|".join(row["warnings"])
            writer.writerow(row)

    statistics: list[dict[str, Any]] = []
    keys = sorted({(record.language, record.document_type) for record in records})
    for language, document_type in keys:
        selected = [
            record
            for record in records
            if record.language == language and record.document_type == document_type
        ]
        usable = [record for record in selected if record.quality_status != "rejected"]
        selected_candidates = [
            candidate
            for candidate in candidates
            if candidate.language == language and candidate.document_type == document_type
        ]
        statistics.append(
            {
                "language": language,
                "document_type": document_type,
                "pages": len(selected),
                "usable_page_records": len(usable),
                "provision_heading_candidates": len(selected_candidates),
                "unique_provision_number_candidates": len(
                    {(item.provision_type, item.provision_number) for item in selected_candidates}
                ),
                "sentences_estimated": sum(sentence_count(record.text) for record in usable),
                "tokens_estimated": sum(token_count(record.text) for record in usable),
                "extraction_warnings": sum(bool(record.verification_notes) for record in selected),
                "rejected_pages": len(selected) - len(usable),
            }
        )
    (output_root / "corpus_statistics.json").write_text(
        json.dumps(statistics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def run_extraction(config_path: Path) -> int:
    """Discover configured PDFs, extract them, and return a process status code."""
    config = load_data_config(config_path)
    root = config.legal_pdf_root
    if not root.is_dir():
        raise FileNotFoundError(f"Legal PDF directory does not exist: {root}")
    discovered = {path.name: path for path in root.rglob("*.pdf")}
    configured = config.documents
    missing = sorted(set(configured) - set(discovered))
    unconfigured = sorted(set(discovered) - set(configured))
    if missing or unconfigured:
        raise ValueError(
            f"Source registry mismatch; missing={missing}, unconfigured={unconfigured}"
        )

    output_root = Path(config.paths["extracted"])
    available_ocr = configure_tesseract(config)
    LOGGER.info("Available Tesseract languages: %s", sorted(available_ocr))
    manifests: list[SourceManifestRecord] = []
    records: list[ExtractionRecord] = []
    quality: list[PageQualityRecord] = []
    for filename in sorted(configured):
        LOGGER.info("Processing %s", filename)
        manifest, document_records, document_quality = process_document(
            discovered[filename], configured[filename], config, output_root, available_ocr
        )
        manifests.append(manifest)
        records.extend(document_records)
        quality.extend(document_quality)
    write_outputs(output_root, manifests, records, quality)
    rejected_pages = sum(item.rejected_pages for item in manifests)
    LOGGER.info("Processed %s PDFs and %s pages", len(manifests), len(records))
    if rejected_pages:
        LOGGER.warning("%s pages remain rejected after extraction quality gates", rejected_pages)
    return 0
