"""Deterministic group-preserving split search for the provisional NER corpus."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any


def _features(rows: list[dict[str, Any]]) -> set[str]:
    values = {f"language={row['meta']['language']}" for row in rows}
    values |= {f"document={row['meta']['document_type']}" for row in rows}
    for row in rows:
        language = row["meta"]["language"]
        values |= {f"language_label={language}:{span[2]}" for span in row.get("label", [])}
    return values


def _groups(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["meta"].get("parent_record_id", row["id"])].append(row)
    return dict(grouped)


def _score(
    parts: list[list[str]],
    groups: dict[str, list[dict[str, Any]]],
    target_fractions: list[float] | None = None,
) -> float:
    all_features = _features([row for values in groups.values() for row in values])
    sizes = [sum(len(groups[group]) for group in part) for part in parts]
    total = sum(sizes)
    targets = (
        [total / len(parts)] * len(parts)
        if target_fractions is None
        else [total * fraction for fraction in target_fractions]
    )
    score = sum((size - target) ** 2 for size, target in zip(sizes, targets, strict=True))
    for part in parts:
        present = _features([row for group in part for row in groups[group]])
        score += 10000 * len(all_features - present)
    return score


def _search_partitions(
    group_ids: list[str],
    groups: dict[str, list[dict[str, Any]]],
    part_count: int,
    seed: int,
    target_fractions: list[float] | None = None,
) -> list[list[str]]:
    rng = random.Random(seed)
    best: list[list[str]] | None = None
    best_score = float("inf")
    for _ in range(10000):
        shuffled = group_ids.copy()
        rng.shuffle(shuffled)
        parts = [[] for _ in range(part_count)]
        part_sizes = [0] * part_count
        fractions = target_fractions or [1 / part_count] * part_count
        targets = [
            len([row for values in groups.values() for row in values]) * f for f in fractions
        ]
        for group in shuffled:
            candidates = list(range(part_count))
            rng.shuffle(candidates)
            selected = min(
                candidates,
                key=lambda index: part_sizes[index] / max(targets[index], 1),
            )
            parts[selected].append(group)
            part_sizes[selected] += len(groups[group])
        score = _score(parts, groups, target_fractions)
        if score < best_score:
            best, best_score = parts, score
            if score == 0:
                break
    if best is None:
        raise RuntimeError("Unable to construct grouped partitions")
    return best


def _rows_for(
    group_ids: list[str], groups: dict[str, list[dict[str, Any]]]
) -> list[dict[str, Any]]:
    return [row for group in group_ids for row in groups[group]]


def _write(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in sorted(rows, key=lambda item: item["id"]):
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def create_grouped_splits(input_path: Path, output: Path, seed: int = 2026) -> dict[str, Any]:
    """Create final holdout, validation, and five grouped development folds."""
    rows = [
        json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line
    ]
    groups = _groups(rows)
    group_ids = sorted(groups)
    train_groups, validation_groups, test_groups = _search_partitions(
        group_ids, groups, 3, seed, [0.70, 0.15, 0.15]
    )
    split_groups = {
        "train": train_groups,
        "validation": validation_groups,
        "test": test_groups,
    }
    output.mkdir(parents=True, exist_ok=True)
    for name, ids in split_groups.items():
        _write(output / f"{name}.jsonl", _rows_for(ids, groups))

    development_groups = train_groups + validation_groups
    folds = _search_partitions(development_groups, groups, 5, seed + 1)
    for index, validation_fold in enumerate(folds, start=1):
        training_fold = [group for fold in folds if fold is not validation_fold for group in fold]
        _write(output / f"fold_{index}_train.jsonl", _rows_for(training_fold, groups))
        _write(output / f"fold_{index}_validation.jsonl", _rows_for(validation_fold, groups))

    intersections = {
        "train_validation": sorted(set(train_groups) & set(validation_groups)),
        "train_test": sorted(set(train_groups) & set(test_groups)),
        "validation_test": sorted(set(validation_groups) & set(test_groups)),
    }
    required_features = _features(rows)
    feature_coverage = {
        name: sorted(_features(_rows_for(ids, groups))) for name, ids in split_groups.items()
    }
    missing_features = {
        name: sorted(required_features - set(features))
        for name, features in feature_coverage.items()
    }
    manifest = {
        "input": str(input_path),
        "random_seed": seed,
        "grouping_key": "parent_record_id",
        "corpus_statuses": sorted({row.get("consensus_status", "unspecified") for row in rows}),
        "task_counts": {name: len(_rows_for(ids, groups)) for name, ids in split_groups.items()},
        "group_counts": {name: len(ids) for name, ids in split_groups.items()},
        "group_intersections": intersections,
        "leakage_detected": any(intersections.values()),
        "target_fractions": {"train": 0.70, "validation": 0.15, "test": 0.15},
        "feature_coverage": feature_coverage,
        "missing_features": missing_features,
        "cross_validation_folds": 5,
        "split_status": "provisional_not_final_gold",
    }
    (output / "split_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
