"""Exact-span evaluation utilities for legal named-entity recognition."""

from __future__ import annotations

from collections import Counter
from typing import Any

Span = tuple[int, int, str]


def _prf(tp: int, fp: int, fn: int) -> dict[str, float | int]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def exact_span_metrics(
    gold_rows: list[dict[str, Any]],
    predictions: dict[str, list[Span]],
    labels: list[str],
) -> dict[str, Any]:
    """Calculate micro, macro, and per-class exact character-span scores."""
    counts = {label: Counter() for label in labels}
    for row in gold_rows:
        gold = {(int(start), int(end), str(label)) for start, end, label in row.get("label", [])}
        predicted = set(predictions.get(str(row["id"]), []))
        for label in labels:
            gold_label = {span for span in gold if span[2] == label}
            predicted_label = {span for span in predicted if span[2] == label}
            counts[label]["tp"] += len(gold_label & predicted_label)
            counts[label]["fp"] += len(predicted_label - gold_label)
            counts[label]["fn"] += len(gold_label - predicted_label)

    per_class = {
        label: _prf(values["tp"], values["fp"], values["fn"]) for label, values in counts.items()
    }
    micro_counts = Counter()
    for values in counts.values():
        micro_counts.update(values)
    macro = {
        metric: sum(float(per_class[label][metric]) for label in labels) / len(labels)
        for metric in ("precision", "recall", "f1")
    }
    return {
        "match": "exact_character_span_and_label",
        "micro": _prf(micro_counts["tp"], micro_counts["fp"], micro_counts["fn"]),
        "macro": macro,
        "per_class": per_class,
        "evaluated_tasks": len(gold_rows),
    }
