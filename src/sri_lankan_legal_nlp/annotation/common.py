"""Shared annotation schemas and offset helpers."""

from __future__ import annotations

import re
from typing import Any

TOKEN_PATTERN = re.compile(r"\w+(?:[’'\-]\w+)*|[^\w\s]", flags=re.UNICODE)


def iter_tokens(text: str) -> list[tuple[str, int, int]]:
    """Return Unicode-aware tokens with half-open character offsets."""
    return [(match.group(), match.start(), match.end()) for match in TOKEN_PATTERN.finditer(text)]


def normalized_span(span: Any) -> tuple[int, int, str]:
    """Accept Doccano list spans or object spans and return one canonical tuple."""
    if isinstance(span, list) and len(span) == 3:
        start, end, label = span
    elif isinstance(span, dict):
        start, end, label = span.get("start_offset"), span.get("end_offset"), span.get("label")
    else:
        raise ValueError(f"Unsupported span representation: {span!r}")
    if not isinstance(start, int) or not isinstance(end, int) or not isinstance(label, str):
        raise ValueError(f"Invalid span values: {span!r}")
    return start, end, label
