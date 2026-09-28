"""Read-only service layer for the research prototype."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from sri_lankan_legal_nlp.ner.baselines import tags_to_spans, token_features, tokenize
from sri_lankan_legal_nlp.simplification.pipeline import prepare_review_record

DISCLAIMER = (
    "This prototype provides research-based legal information, not legal advice. "
    "Check the cited official source and verification status."
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read JSONL if present, allowing the API to start before every phase is complete."""
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


@lru_cache(maxsize=1)
def load_crf() -> Any | None:
    """Load the expanded provisional CRF once; return None when unavailable."""
    path = Path("results/ner/expanded_baselines/crf_model.joblib")
    if not path.exists():
        return None
    import joblib

    return joblib.load(path)


def predict_entities(text: str, language: str) -> dict[str, Any]:
    """Run the saved CRF and expose character spans with provisional status."""
    model = load_crf()
    if model is None:
        return {
            "entities": [],
            "model": None,
            "status": "model_unavailable",
            "disclaimer": DISCLAIMER,
        }
    tokens = tokenize(text)
    features = [[token_features(tokens, index) for index in range(len(tokens))]]
    tags = model.predict(features)[0] if tokens else []
    spans = tags_to_spans(tokens, tags)
    return {
        "language": language,
        "entities": [
            {"start": start, "end": end, "label": label, "text": text[start:end]}
            for start, end, label in spans
        ],
        "model": "expanded_provisional_crf",
        "model_validation_micro_f1": 0.1985294117647059,
        "status": "provisional_not_final_gold",
        "disclaimer": DISCLAIMER,
    }


def find_source_records(query: str, language: str | None, limit: int) -> list[dict[str, Any]]:
    """Find literal text or provision matches in provenance-preserving extracted records."""
    needle = query.casefold().strip()
    matches: list[dict[str, Any]] = []
    for row in read_jsonl(Path("data/extracted/records.jsonl")):
        if language and row.get("language") != language:
            continue
        searchable = f"{row.get('provision_number') or ''} {row.get('text') or ''}".casefold()
        if needle and needle not in searchable:
            continue
        matches.append(row)
        if len(matches) >= limit:
            break
    return matches


def find_amendments(provision: str | None, limit: int) -> list[dict[str, Any]]:
    """Return unverified amendment candidates, optionally filtered by provision number."""
    rows = read_jsonl(Path("results/amendments/amendment_candidates.jsonl"))
    if provision:
        rows = [row for row in rows if str(row.get("affected_provision")) == provision]
    return rows[:limit]


def simplification_template(text: str, language: str) -> dict[str, Any]:
    """Return a blank human-review task, never an invented translation or simplification."""
    return prepare_review_record(
        {"record_id": "api-user-text", "language": language, "text": text}, {}
    )
