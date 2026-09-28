"""Deterministic, review-first extraction of statutory amendment instructions."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

REFERENCE_RE = re.compile(
    r"(?P<number>\d+[A-Za-zඅ-ෆ]?)\s*(?:වන\s+)?(?P<kind>වගන්තිය|උපවගන්තිය|section|article)",
    re.IGNORECASE,
)

OPERATION_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "insertion": tuple(
        re.compile(value, re.IGNORECASE)
        for value in (r"ඇතුළත්\s+කිරීම", r"එකතු\s+කිරීම", r"\binsert(?:ed|ion|ing)?\b")
    ),
    "deletion": tuple(
        re.compile(value, re.IGNORECASE)
        for value in (r"ඉවත්\s+කිරීම", r"\b(?:delete|deletion|omit|omission)\w*\b")
    ),
    "substitution": tuple(
        re.compile(value, re.IGNORECASE)
        for value in (r"ආදේශ\s+කිරීම", r"වෙනුවට", r"\bsubstitut\w*\b", r"\breplac\w*\b")
    ),
    "repeal": tuple(
        re.compile(value, re.IGNORECASE) for value in (r"අවලංගු", r"\brepeal\w*\b")
    ),
    "renumbering": tuple(
        re.compile(value, re.IGNORECASE)
        for value in (r"නැවත\s+අංක", r"\brenumber\w*\b")
    ),
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def detect_operations(text: str) -> list[str]:
    """Return every operation supported by an explicit textual cue."""
    return [
        operation
        for operation, patterns in OPERATION_PATTERNS.items()
        if any(pattern.search(text) for pattern in patterns)
    ]


def extract_candidates(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract provision-linked page candidates while preserving uncertainty."""
    text = str(row.get("text", ""))
    references = list(REFERENCE_RE.finditer(text))
    events: list[dict[str, Any]] = []
    for index, match in enumerate(references):
        start = max(0, match.start() - 160)
        end = min(len(text), match.end() + 500)
        instruction = text[start:end].strip()
        operations = detect_operations(instruction)
        operation = operations[0] if len(operations) == 1 else None
        event_key = f"{row['record_id']}:{match.start()}:{match.group('number')}"
        event_id = "amendment-event-" + hashlib.sha256(event_key.encode("utf-8")).hexdigest()[:16]
        events.append(
            {
                "amendment_event_id": event_id,
                "source_record_id": row["record_id"],
                "amendment_id": row.get("document_id"),
                "amendment_number": row.get("amendment_number"),
                "language": row.get("language"),
                "affected_document": "penal_code",
                "affected_provision_type": (
                    "section"
                    if match.group("kind").lower() in {"වගන්තිය", "section"}
                    else "subsection"
                ),
                "affected_provision": match.group("number"),
                "operation": operation,
                "operation_candidates": operations,
                "amending_instruction": instruction,
                "original_text": None,
                "updated_text": None,
                "source_file": row.get("source_file"),
                "page_number": row.get("pdf_page_number"),
                "extraction_quality_status": row.get("quality_status"),
                "link_status": "reference_detected_not_linked",
                "reconstruction_status": "not_attempted_pending_verification",
                "verification_status": "pending_manual_review",
                "ambiguity_reason": (
                    None
                    if len(operations) == 1
                    else "no_operation_cue" if not operations else "multiple_operation_cues"
                ),
                "reference_character_start": match.start(),
                "reference_character_end": match.end(),
                "reference_index_on_page": index,
            }
        )
    return events


def run_amendment_tracking(config_path: Path) -> int:
    """Create amendment candidates and a manual-review sheet; do not consolidate automatically."""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    paths = config.get("paths", {})
    input_path = Path(paths.get("extracted_records", "data/extracted/records.jsonl"))
    output_dir = Path(paths.get("output_dir", "results/amendments"))
    rows = [row for row in _read_jsonl(input_path) if row.get("document_type") == "amendment"]
    candidates = [event for row in rows for event in extract_candidates(row)]
    candidates.sort(
        key=lambda event: (
            str(event["amendment_id"]),
            int(event["page_number"] or 0),
            int(event["reference_character_start"]),
        )
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "amendment_candidates.jsonl").open(
        "w", encoding="utf-8", newline="\n"
    ) as stream:
        for event in candidates:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")

    review_fields = [
        "amendment_event_id",
        "amendment_number",
        "affected_provision_type",
        "affected_provision",
        "operation",
        "operation_candidates",
        "source_file",
        "page_number",
        "amending_instruction",
        "reviewer_reference_correct",
        "reviewer_operation",
        "reviewer_linked_record_id",
        "reviewer_notes",
        "verification_status",
    ]
    with (output_dir / "amendment_review.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=review_fields, extrasaction="ignore")
        writer.writeheader()
        for event in candidates:
            row = event | {
                "operation_candidates": "|".join(event["operation_candidates"]),
                "reviewer_reference_correct": "",
                "reviewer_operation": "",
                "reviewer_linked_record_id": "",
                "reviewer_notes": "",
            }
            writer.writerow(row)

    operation_counts = Counter(event["operation"] or "unresolved" for event in candidates)
    report = {
        "source_amendment_pages": len(rows),
        "source_amendment_documents": len({row.get("document_id") for row in rows}),
        "languages": dict(Counter(str(row.get("language")) for row in rows)),
        "candidate_events": len(candidates),
        "operation_counts": dict(operation_counts),
        "unresolved_operation_count": operation_counts["unresolved"],
        "linked_to_original_provision_count": 0,
        "reconstructed_text_count": 0,
        "manually_verified_gold_count": 0,
        "evaluation_available": False,
        "status": "candidates_pending_manual_review",
    }
    (output_dir / "amendment_tracking_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0
