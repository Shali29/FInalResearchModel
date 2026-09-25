"""Lightweight character-span to transformer-subword alignment."""

from __future__ import annotations

from typing import Any


def align_labels(
    offsets: list[tuple[int, int]],
    spans: list[list[Any]],
    label_to_id: dict[str, int],
) -> list[int]:
    """Align character spans to subwords; special and padding tokens receive -100."""
    labels: list[int] = []
    previous: tuple[int, int, str] | None = None
    normalized = [(int(start), int(end), str(label)) for start, end, label in spans]
    for start, end in offsets:
        if start == end:
            labels.append(-100)
            previous = None
            continue
        matched = next(
            (
                (left, right, label)
                for left, right, label in normalized
                if start < right and left < end
            ),
            None,
        )
        if matched is None:
            labels.append(label_to_id["O"])
            previous = None
            continue
        prefix = "I" if previous == matched else "B"
        labels.append(label_to_id[f"{prefix}-{matched[2]}"])
        previous = matched
    return labels
