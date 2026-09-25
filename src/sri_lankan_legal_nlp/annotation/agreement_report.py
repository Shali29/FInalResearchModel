"""Aggregate independent annotator agreement over shared task IDs."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from sri_lankan_legal_nlp.annotation.common import iter_tokens, normalized_span


def _read_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return {row["id"]: row for row in rows}


def _token_labels(text: str, raw_spans: list[Any]) -> list[str]:
    spans = [normalized_span(span) for span in raw_spans]
    labels: list[str] = []
    for _, start, end in iter_tokens(text):
        covering = [label for left, right, label in spans if start >= left and end <= right]
        labels.append(covering[0] if covering else "O")
    return labels


def _cohen_kappa(first: list[str], second: list[str]) -> float:
    """Calculate Cohen's kappa without loading a heavyweight ML runtime."""
    if len(first) != len(second) or not first:
        raise ValueError("Kappa requires two non-empty label sequences of equal length")
    size = len(first)
    observed = sum(left == right for left, right in zip(first, second, strict=True)) / size
    first_counts, second_counts = Counter(first), Counter(second)
    labels = set(first_counts) | set(second_counts)
    expected = sum((first_counts[label] / size) * (second_counts[label] / size) for label in labels)
    if expected == 1.0:
        return 1.0 if observed == 1.0 else 0.0
    return (observed - expected) / (1.0 - expected)


def calculate_agreement(first_path: Path, second_path: Path) -> dict[str, Any]:
    """Calculate exact entity agreement and token kappa over common independently labeled tasks."""
    first, second = _read_jsonl(first_path), _read_jsonl(second_path)
    shared_ids = sorted(set(first) & set(second))
    if not shared_ids:
        raise ValueError("The annotator exports contain no shared research task IDs")
    gold_spans: set[tuple[str, int, int, str]] = set()
    predicted_spans: set[tuple[str, int, int, str]] = set()
    first_tokens: list[str] = []
    second_tokens: list[str] = []
    for task_id in shared_ids:
        if first[task_id]["text"] != second[task_id]["text"]:
            raise ValueError(f"Text mismatch for shared task {task_id}")
        text = first[task_id]["text"]
        for start, end, label in map(normalized_span, first[task_id].get("label", [])):
            gold_spans.add((task_id, start, end, label))
        for start, end, label in map(normalized_span, second[task_id].get("label", [])):
            predicted_spans.add((task_id, start, end, label))
        first_tokens.extend(_token_labels(text, first[task_id].get("label", [])))
        second_tokens.extend(_token_labels(text, second[task_id].get("label", [])))
    true_positive = len(gold_spans & predicted_spans)
    precision = true_positive / len(predicted_spans) if predicted_spans else 0.0
    recall = true_positive / len(gold_spans) if gold_spans else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    kappa = _cohen_kappa(first_tokens, second_tokens) if first_tokens else 0.0
    return {
        "shared_task_count": len(shared_ids),
        "annotator_1_entity_count": len(gold_spans),
        "annotator_2_entity_count": len(predicted_spans),
        "exact_span_true_positives": true_positive,
        "exact_span_precision": precision,
        "exact_span_recall": recall,
        "exact_span_f1": f1,
        "token_cohen_kappa": kappa,
        "interpretation_warning": (
            "Token kappa can be inflated by non-entity O tokens; interpret it with exact-span F1."
        ),
    }


def write_agreement_report(first_path: Path, second_path: Path, output_path: Path) -> None:
    """Calculate and save an agreement report as traceable JSON."""
    report = calculate_agreement(first_path, second_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
