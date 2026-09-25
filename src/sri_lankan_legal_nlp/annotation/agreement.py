"""Inter-annotator agreement for exact spans and token labels."""

from __future__ import annotations

from collections import Counter
from typing import Any

from sri_lankan_legal_nlp.annotation.agreement_report import _cohen_kappa
from sri_lankan_legal_nlp.annotation.common import iter_tokens, normalized_span


def span_prf(gold: list[Any], predicted: list[Any]) -> dict[str, float]:
    """Calculate exact entity-span precision, recall, and F1."""
    gold_set = {normalized_span(span) for span in gold}
    predicted_set = {normalized_span(span) for span in predicted}
    true_positive = len(gold_set & predicted_set)
    precision = true_positive / len(predicted_set) if predicted_set else 0.0
    recall = true_positive / len(gold_set) if gold_set else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def token_kappa(text: str, first: list[Any], second: list[Any]) -> float:
    """Calculate token-level Cohen's kappa as a secondary agreement measure."""
    tokens = iter_tokens(text)

    def labels(spans: list[Any]) -> list[str]:
        normalized = [normalized_span(span) for span in spans]
        values: list[str] = []
        for _, start, end in tokens:
            covering = [
                label for left, right, label in normalized if start >= left and end <= right
            ]
            values.append(covering[0] if covering else "O")
        return values

    first_labels, second_labels = labels(first), labels(second)
    if Counter(first_labels) == Counter({"O": len(first_labels)}) and first_labels == second_labels:
        return 1.0
    return _cohen_kappa(first_labels, second_labels)
