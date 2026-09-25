"""Phase 6 baseline training and validation entry point."""

from __future__ import annotations

import json
import logging
import platform
import random
from importlib.metadata import version
from pathlib import Path
from typing import Any

import yaml

from sri_lankan_legal_nlp.ner.baselines import (
    bio_tags,
    build_dictionary,
    dictionary_predict,
    tags_to_spans,
    token_features,
    tokenize,
)
from sri_lankan_legal_nlp.ner.evaluation import exact_span_metrics

LOGGER = logging.getLogger(__name__)


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_predictions(
    path: Path,
    rows: list[dict[str, Any]],
    predictions: dict[str, list[tuple[int, int, str]]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            task_id = str(row["id"])
            stream.write(
                json.dumps(
                    {
                        "id": task_id,
                        "text": row["text"],
                        "meta": row["meta"],
                        "gold": row.get("label", []),
                        "predicted": predictions.get(task_id, []),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def _evaluate_slices(
    rows: list[dict[str, Any]],
    predictions: dict[str, list[tuple[int, int, str]]],
    labels: list[str],
) -> dict[str, Any]:
    report: dict[str, Any] = {"overall": exact_span_metrics(rows, predictions, labels)}
    for field in ("language", "document_type"):
        values = sorted({str(row["meta"][field]) for row in rows})
        report[f"by_{field}"] = {
            value: exact_span_metrics(
                [row for row in rows if str(row["meta"][field]) == value], predictions, labels
            )
            for value in values
        }
    return report


def run_ner(config_path: Path) -> int:
    """Train required transparent baselines and evaluate on validation data only."""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    seed = int(config["project"]["random_seed"])
    random.seed(seed)
    labels = list(config["annotation"]["labels"])
    split_dir = Path(config.get("phase6", {}).get("split_dir", "data/splits/provisional"))
    output = Path(config.get("phase6", {}).get("output_dir", "results/ner/baselines"))
    train_rows = _read(split_dir / "train.jsonl")
    validation_rows = _read(split_dir / "validation.jsonl")

    dictionary = build_dictionary(train_rows)
    dictionary_predictions = {
        str(row["id"]): dictionary_predict(row, dictionary) for row in validation_rows
    }
    _write_json(
        output / "dictionary_validation_metrics.json",
        _evaluate_slices(validation_rows, dictionary_predictions, labels),
    )
    _write_json(output / "dictionary.json", dictionary)
    _write_predictions(
        output / "dictionary_validation_predictions.jsonl", validation_rows, dictionary_predictions
    )

    try:
        import sklearn_crfsuite
    except ImportError as error:
        raise RuntimeError("Install sklearn-crfsuite in .venv before running Phase 6") from error

    train_tokens = [tokenize(str(row["text"])) for row in train_rows]
    x_train = [[token_features(tokens, i) for i in range(len(tokens))] for tokens in train_tokens]
    y_train = [bio_tags(row, tokens) for row, tokens in zip(train_rows, train_tokens, strict=True)]
    crf = sklearn_crfsuite.CRF(
        algorithm="lbfgs", c1=0.1, c2=0.1, max_iterations=100, all_possible_transitions=True
    )
    crf.fit(x_train, y_train)
    import joblib

    output.mkdir(parents=True, exist_ok=True)
    joblib.dump(crf, output / "crf_model.joblib")
    validation_tokens = [tokenize(str(row["text"])) for row in validation_rows]
    x_validation = [
        [token_features(tokens, i) for i in range(len(tokens))] for tokens in validation_tokens
    ]
    predicted_tags = crf.predict(x_validation)
    crf_predictions = {
        str(row["id"]): tags_to_spans(tokens, tags)
        for row, tokens, tags in zip(
            validation_rows, validation_tokens, predicted_tags, strict=True
        )
    }
    _write_json(
        output / "crf_validation_metrics.json",
        _evaluate_slices(validation_rows, crf_predictions, labels),
    )
    _write_predictions(
        output / "crf_validation_predictions.jsonl", validation_rows, crf_predictions
    )
    _write_json(
        output / "run_manifest.json",
        {
            "random_seed": seed,
            "training_tasks": len(train_rows),
            "validation_tasks": len(validation_rows),
            "test_set_used": False,
            "split_status": "provisional_not_final_gold",
            "python": platform.python_version(),
            "package_versions": {
                package: version(package)
                for package in ("scikit-learn", "sklearn-crfsuite", "joblib", "PyYAML")
            },
            "selection_rule": "validation macro-F1; held-out test untouched",
        },
    )
    LOGGER.info("Phase 6 baselines written to %s", output)
    return 0
