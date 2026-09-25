"""Phase 5 consensus construction and leakage-safe split feasibility audit."""

from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from sri_lankan_legal_nlp.annotation.common import normalized_span

LOGGER = logging.getLogger(__name__)


def _read_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return {row["id"]: row for row in rows}


def exact_agreement_corpus(
    first: dict[str, dict[str, Any]], second: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Create a provisional corpus containing only exact spans shared by both annotators."""
    corpus: list[dict[str, Any]] = []
    for task_id in sorted(set(first) & set(second)):
        left, right = first[task_id], second[task_id]
        if left["text"] != right["text"]:
            raise ValueError(f"Text mismatch for shared task {task_id}")
        left_spans = {normalized_span(span) for span in left.get("label", [])}
        right_spans = {normalized_span(span) for span in right.get("label", [])}
        corpus.append(
            {
                "id": task_id,
                "text": left["text"],
                "label": [list(span) for span in sorted(left_spans & right_spans)],
                "meta": left.get("meta", {}),
                "consensus_status": "exact_agreement_only_pending_adjudication",
            }
        )
    return corpus


def feasibility_report(
    corpus: list[dict[str, Any]], labels: list[str], folds: int
) -> dict[str, Any]:
    """Measure entity and independent parent-group support for every language/class cell."""
    entity_counts: Counter[tuple[str, str]] = Counter()
    groups: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in corpus:
        language = row["meta"].get("language", "unknown")
        group = row["meta"].get("parent_record_id", row["id"])
        for _, _, label in map(normalized_span, row.get("label", [])):
            entity_counts[(language, label)] += 1
            groups[(language, label)].add(group)
    cells: list[dict[str, Any]] = []
    for language in ("en", "si"):
        for label in labels:
            key = (language, label)
            group_count = len(groups[key])
            cells.append(
                {
                    "language": language,
                    "label": label,
                    "entity_count": entity_counts[key],
                    "independent_group_count": group_count,
                    "supports_requested_folds": group_count >= folds,
                }
            )
    unsupported = [cell for cell in cells if not cell["supports_requested_folds"]]
    feasible = not unsupported
    statuses = sorted({row.get("consensus_status", "unspecified") for row in corpus})
    return {
        "corpus_status": statuses[0] if len(statuses) == 1 else statuses,
        "task_count": len(corpus),
        "entity_count": sum(entity_counts.values()),
        "requested_grouped_cross_validation_folds": folds,
        "grouping_key": "parent_record_id",
        "language_label_support": cells,
        "five_fold_feasible": feasible,
        "unsupported_cells": unsupported,
        "final_split_created": False,
        "reason": (
            "Required language/class group support is sufficient for provisional grouped splits."
            if feasible
            else "Final train/validation/test and cross-validation splits are withheld until "
            "adjudication and adequate independent group support exist for every required cell."
        ),
    }


def run_splitting(config_path: Path) -> int:
    """Build provisional consensus and audit feasibility without forcing invalid splits."""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    root = config_path.resolve().parents[1]
    annotation = root / config["paths"]["annotation"]
    output = root / config["paths"]["splits"]
    output.mkdir(parents=True, exist_ok=True)
    first = _read_jsonl(annotation / "shared_annotator1_clean.jsonl")
    second = _read_jsonl(annotation / "shared_annotator2_clean.jsonl")
    corpus = exact_agreement_corpus(first, second)
    corpus_path = output / "provisional_exact_agreement_corpus.jsonl"
    with corpus_path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in corpus:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    report = feasibility_report(
        corpus,
        config["annotation"]["labels"],
        int(config["splitting"]["development_cross_validation_folds"]),
    )
    (output / "split_feasibility_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    LOGGER.warning(report["reason"])
    return 0
