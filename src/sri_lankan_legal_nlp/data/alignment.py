"""Conservative structure-first bilingual provision alignment."""

from __future__ import annotations

import csv
import hashlib
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from sri_lankan_legal_nlp.data.models import AlignmentIssue, AlignmentRecord

LOGGER = logging.getLogger(__name__)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read non-empty JSONL objects from *path*."""
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def _write_jsonl(path: Path, records: list[Any]) -> None:
    """Write validated Pydantic models as UTF-8 JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(record.model_dump_json() + "\n")


def _stable_id(prefix: str, *parts: str) -> str:
    payload = "|".join(parts).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(payload).hexdigest()[:16]}"


def _candidate_key(row: dict[str, Any]) -> tuple[str, str]:
    return row["provision_type"], row["provision_number"].strip()


def _record_index(records: list[dict[str, Any]]) -> dict[tuple[str, int], dict[str, Any]]:
    return {(row["document_id"], row["pdf_page_number"]): row for row in records}


def _issue(
    issue_type: str,
    language: str,
    document_type: str,
    key: tuple[str, str],
    rows: list[dict[str, Any]],
    page_records: dict[tuple[str, int], dict[str, Any]],
    details: str,
) -> AlignmentIssue:
    linked = [page_records[(row["document_id"], row["pdf_page_number"])] for row in rows]
    candidate_ids = [row["candidate_id"] for row in rows]
    return AlignmentIssue(
        issue_id=_stable_id("alignment-issue", issue_type, *sorted(candidate_ids)),
        issue_type=issue_type,
        language=language,
        document_type=document_type,
        provision_type=key[0],
        provision_number=key[1],
        candidate_ids=candidate_ids,
        record_ids=[row["record_id"] for row in linked],
        source_files=[row["source_file"] for row in rows],
        pdf_page_numbers=[row["pdf_page_number"] for row in rows],
        details=details,
    )


def align_document_pair(
    candidates: list[dict[str, Any]],
    records: list[dict[str, Any]],
    english_document_id: str,
    sinhala_document_id: str,
    document_type: str,
) -> tuple[list[AlignmentRecord], list[AlignmentIssue]]:
    """Align only exact provision keys occurring once in each language document."""
    page_records = _record_index(records)
    by_language: dict[str, dict[tuple[str, str], list[dict[str, Any]]]] = {
        "en": defaultdict(list),
        "si": defaultdict(list),
    }
    for row in candidates:
        if row["document_id"] == english_document_id:
            by_language["en"][_candidate_key(row)].append(row)
        elif row["document_id"] == sinhala_document_id:
            by_language["si"][_candidate_key(row)].append(row)

    alignments: list[AlignmentRecord] = []
    issues: list[AlignmentIssue] = []
    all_keys = sorted(set(by_language["en"]) | set(by_language["si"]))
    for key in all_keys:
        english = by_language["en"].get(key, [])
        sinhala = by_language["si"].get(key, [])
        if len(english) == 1 and len(sinhala) == 1:
            en_candidate, si_candidate = english[0], sinhala[0]
            en_record = page_records[(english_document_id, en_candidate["pdf_page_number"])]
            si_record = page_records[(sinhala_document_id, si_candidate["pdf_page_number"])]
            alignments.append(
                AlignmentRecord(
                    alignment_id=_stable_id(
                        "alignment", en_candidate["candidate_id"], si_candidate["candidate_id"]
                    ),
                    english_record_id=en_record["record_id"],
                    sinhala_record_id=si_record["record_id"],
                    english_candidate_id=en_candidate["candidate_id"],
                    sinhala_candidate_id=si_candidate["candidate_id"],
                    document_type=document_type,
                    provision_type=key[0],
                    provision_number=key[1],
                    alignment_method="exact_unique_structural_match",
                    confidence_score=0.95,
                    manual_review_status="pending_review",
                    english_source_file=en_candidate["source_file"],
                    english_pdf_page_number=en_candidate["pdf_page_number"],
                    sinhala_source_file=si_candidate["source_file"],
                    sinhala_pdf_page_number=si_candidate["pdf_page_number"],
                )
            )
            continue

        if not english or not sinhala:
            present = english or sinhala
            language = "en" if english else "si"
            issues.append(
                _issue(
                    "unmatched",
                    language,
                    document_type,
                    key,
                    present,
                    page_records,
                    (
                        "No candidate with the same provision type and number exists "
                        "in the other language."
                    ),
                )
            )
            continue

        combined = english + sinhala
        issues.append(
            _issue(
                "duplicate",
                "bilingual",
                document_type,
                key,
                combined,
                page_records,
                (
                    f"Ambiguous structural key: {len(english)} English and "
                    f"{len(sinhala)} Sinhala candidates."
                ),
            )
        )
    return alignments, issues


def _write_summary(
    path: Path, alignments: list[AlignmentRecord], issues: list[AlignmentIssue]
) -> None:
    counts: dict[str, int] = defaultdict(int)
    for issue in issues:
        counts[issue.issue_type] += 1
    lines = [
        "# Phase 3 Bilingual Alignment Report",
        "",
        (
            "Alignment used exact provision type and number only. Page numbers were retained "
            "as provenance"
        ),
        "but were never used to infer translation equivalence.",
        "",
        f"- Provisional exact unique pairs: {len(alignments)}",
        f"- Unmatched structural keys: {counts['unmatched']}",
        f"- Duplicate/ambiguous structural keys: {counts['duplicate']}",
        f"- Conflicting keys: {counts['conflicting']}",
        f"- Low-confidence keys: {counts['low_confidence']}",
        "",
        "All pairs remain pending manual bilingual review. Amendment documents without an explicit",
        "English counterpart and verified amendment identity were not force-aligned.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_review_csv(path: Path, alignments: list[AlignmentRecord]) -> None:
    fields = [
        "alignment_id",
        "document_type",
        "provision_type",
        "provision_number",
        "english_source_file",
        "english_pdf_page_number",
        "sinhala_source_file",
        "sinhala_pdf_page_number",
        "review_decision",
        "reviewer",
        "review_date",
        "notes",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for item in alignments:
            row = {field: "" for field in fields}
            row.update(
                {
                    "alignment_id": item.alignment_id,
                    "document_type": item.document_type,
                    "provision_type": item.provision_type,
                    "provision_number": item.provision_number,
                    "english_source_file": item.english_source_file,
                    "english_pdf_page_number": item.english_pdf_page_number,
                    "sinhala_source_file": item.sinhala_source_file,
                    "sinhala_pdf_page_number": item.sinhala_pdf_page_number,
                }
            )
            writer.writerow(row)


def run_alignment(config_path: Path) -> int:
    """Run Phase 3 from Phase 2 artifacts using configured canonical document pairs."""
    with config_path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    root = config_path.resolve().parents[1]
    extracted = root / config["paths"]["extracted"]
    output = root / config["paths"]["aligned"]
    candidates = _read_jsonl(extracted / "provision_candidates.jsonl")
    records = _read_jsonl(extracted / "records.jsonl")

    all_alignments: list[AlignmentRecord] = []
    all_issues: list[AlignmentIssue] = []
    for pair in config["alignment"]["document_pairs"]:
        alignments, issues = align_document_pair(
            candidates,
            records,
            pair["english_document_id"],
            pair["sinhala_document_id"],
            pair["document_type"],
        )
        all_alignments.extend(alignments)
        all_issues.extend(issues)

    output.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output / "alignments.jsonl", all_alignments)
    _write_jsonl(output / "alignment_issues.jsonl", all_issues)
    _write_review_csv(output / "alignment_review.csv", all_alignments)
    _write_summary(output / "alignment_report.md", all_alignments, all_issues)
    LOGGER.info(
        "Wrote %s provisional pairs and %s review issues.", len(all_alignments), len(all_issues)
    )
    return 0
