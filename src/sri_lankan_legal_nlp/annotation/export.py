"""Export validated character-span annotations to JSONL and BIO CoNLL."""

from __future__ import annotations

import json
from pathlib import Path

from sri_lankan_legal_nlp.annotation.common import iter_tokens, normalized_span
from sri_lankan_legal_nlp.annotation.validation import validate_annotation_file


def export_conll(input_path: Path, labels_path: Path, output_path: Path) -> None:
    """Validate and export Doccano JSONL using deterministic Unicode token offsets."""
    errors = validate_annotation_file(input_path, labels_path)
    if errors:
        raise ValueError("Annotation validation failed:\n" + "\n".join(errors[:50]))
    rows = [
        json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line
    ]
    lines: list[str] = []
    for row in rows:
        spans = sorted(normalized_span(span) for span in row.get("label", []))
        for token, start, end in iter_tokens(row["text"]):
            tag = "O"
            for span_start, span_end, label in spans:
                if start >= span_start and end <= span_end:
                    tag = ("B-" if start == span_start else "I-") + label
                    break
                if start < span_end and end > span_start:
                    raise ValueError(f"Token boundary cuts entity span in task {row['id']}")
            lines.append(f"{token}\t{tag}")
        lines.append("")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
