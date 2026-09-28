"""Prepare conservative plain-Sinhala review tasks without fabricating translations."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def load_verified_glossary(path: Path) -> dict[str, str]:
    """Load only explicitly expert-verified Sinhala-to-Sinhala glossary entries."""
    entries: dict[str, str] = {}
    for row in _read_jsonl(path):
        if row.get("review_status") != "verified_by_legal_expert":
            continue
        source = str(row.get("source_term", "")).strip()
        explanation = str(row.get("plain_sinhala_explanation", "")).strip()
        if source and explanation:
            entries[source] = explanation
    return entries


def _record_id(row: dict[str, Any]) -> str:
    existing = row.get("record_id") or row.get("id")
    if existing:
        return str(existing)
    digest = hashlib.sha256(str(row.get("text", "")).encode("utf-8")).hexdigest()[:16]
    return f"simplification-{digest}"


def has_sinhala_unicode(text: str) -> bool:
    """Return whether text contains at least one character in the Sinhala block."""
    return any("\u0d80" <= character <= "\u0dff" for character in text)


def has_mojibake(text: str) -> bool:
    """Detect common UTF-8-decoded-as-Latin-1 corruption seen in extracted Sinhala."""
    return any(marker in text for marker in ("à¶", "à·", "â€", "ï¿½"))


def text_is_usable(row: dict[str, Any]) -> bool:
    """Reject empty/corrupt text and Sinhala records lacking actual Sinhala characters."""
    meta = row.get("meta", {})
    language = str(row.get("language") or meta.get("language") or "unknown")
    text = str(row.get("text", ""))
    if not text.strip() or has_mojibake(text):
        return False
    return language != "si" or has_sinhala_unicode(text)


def prepare_review_record(row: dict[str, Any], glossary: dict[str, str]) -> dict[str, Any]:
    """Create a traceable task; never invent translation or simplified legal meaning."""
    meta = row.get("meta", {})
    language = str(row.get("language") or meta.get("language") or "unknown")
    text = str(row.get("text", ""))
    glossary_matches = [
        {"source_term": term, "verified_explanation": explanation}
        for term, explanation in glossary.items()
        if term in text
    ]
    return {
        "record_id": _record_id(row),
        "original_language": language,
        "original_text": text,
        "translated_sinhala": text if language == "si" else None,
        "simplified_sinhala": None,
        "verified_glossary_matches": glossary_matches,
        "preserved_entities": row.get("label", []),
        "preserved_citations": [],
        "source_file": row.get("source_file") or meta.get("source_file"),
        "page_number": row.get("pdf_page_number") or meta.get("pdf_page_number"),
        "document_type": row.get("document_type") or meta.get("document_type"),
        "translation_status": "not_required" if language == "si" else "pending_human_translation",
        "simplification_status": "pending_human_draft",
        "review_status": "pending_expert_review",
        "legal_information_disclaimer": "Explanatory research output only; not legal advice.",
    }


def run_simplification(
    config_path: Path,
    input_override: Path | None = None,
    output_override: Path | None = None,
    max_records: int | None = None,
) -> int:
    """Audit data readiness and generate an unfilled, provenance-preserving review batch."""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    input_path = input_override or Path(
        config.get("paths", {}).get("input_records", "data/extracted/records.jsonl")
    )
    output_dir = output_override or Path(
        config.get("paths", {}).get("output_dir", "results/simplification")
    )
    glossary_path = Path(config["resources"]["glossary"])
    pairs_path = Path(
        config.get("paths", {}).get(
            "verified_pairs", "data/processed/verified_simplification_pairs.jsonl"
        )
    )
    rows = _read_jsonl(input_path)
    limit = max_records if max_records is not None else int(
        config.get("review_batch", {}).get("maximum_records", 100)
    )
    usable_rows = [row for row in rows if text_is_usable(row)]
    selected = usable_rows[: max(limit, 0)]
    glossary = load_verified_glossary(glossary_path)
    verified_pairs = [
        row
        for row in _read_jsonl(pairs_path)
        if row.get("review_status") == "verified_by_legal_expert"
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    tasks_path = output_dir / "expert_review_tasks.jsonl"
    with tasks_path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in selected:
            task = prepare_review_record(row, glossary)
            stream.write(json.dumps(task, ensure_ascii=False) + "\n")

    readiness = {
        "input_path": str(input_path),
        "input_records": len(rows),
        "usable_input_records": len(usable_rows),
        "rejected_for_text_integrity": len(rows) - len(usable_rows),
        "review_tasks_created": len(selected),
        "verified_glossary_entries": len(glossary),
        "verified_simplification_pairs": len(verified_pairs),
        "supervised_training_ready": bool(verified_pairs),
        "supervised_training_run": False,
        "translation_generated": False,
        "simplifications_generated": False,
        "output_status": "blank_pending_human_and_expert_review",
    }
    (output_dir / "data_readiness_report.json").write_text(
        json.dumps(readiness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0
