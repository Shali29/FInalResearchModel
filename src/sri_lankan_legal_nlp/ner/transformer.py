"""Reproducible transformer token-classification training for bilingual legal NER."""

from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForTokenClassification, AutoTokenizer

from sri_lankan_legal_nlp.ner.baselines import tags_to_spans
from sri_lankan_legal_nlp.ner.evaluation import exact_span_metrics
from sri_lankan_legal_nlp.ner.transformer_alignment import align_labels

LOGGER = logging.getLogger(__name__)


def set_seed(seed: int) -> None:
    """Set all available random seeds and deterministic CPU behavior."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a UTF-8 JSONL dataset."""
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


class NerDataset(Dataset):
    """Pre-tokenized NER examples retaining IDs and exact offset mappings."""

    def __init__(
        self,
        rows: list[dict[str, Any]],
        tokenizer: Any,
        label_to_id: dict[str, int],
        maximum_length: int,
    ) -> None:
        self.rows = rows
        self.items: list[dict[str, Any]] = []
        for row in rows:
            encoded = tokenizer(
                str(row["text"]),
                truncation=True,
                max_length=maximum_length,
                padding="max_length",
                return_offsets_mapping=True,
            )
            offsets = [tuple(pair) for pair in encoded.pop("offset_mapping")]
            encoded["labels"] = align_labels(offsets, row.get("label", []), label_to_id)
            encoded["offsets"] = offsets
            self.items.append(encoded)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return self.items[index]


def collate(batch: list[dict[str, Any]]) -> dict[str, Any]:
    """Stack model fields while leaving offset mappings as Python values."""
    tensor_keys = {"input_ids", "attention_mask", "token_type_ids", "labels"}
    output = {
        key: torch.tensor([item[key] for item in batch], dtype=torch.long)
        for key in tensor_keys
        if key in batch[0]
    }
    output["offsets"] = [item["offsets"] for item in batch]
    return output


def predict(
    model: Any,
    loader: DataLoader,
    rows: list[dict[str, Any]],
    id_to_label: dict[int, str],
    device: torch.device,
) -> dict[str, list[tuple[int, int, str]]]:
    """Return exact character-span predictions in original task order."""
    model.eval()
    predictions: dict[str, list[tuple[int, int, str]]] = {}
    row_index = 0
    with torch.no_grad():
        for batch in loader:
            offsets_batch = batch.pop("offsets")
            labels = batch.pop("labels")
            inputs = {key: value.to(device) for key, value in batch.items()}
            predicted = model(**inputs).logits.argmax(dim=-1).cpu().tolist()
            for offsets, gold_ids, predicted_ids in zip(
                offsets_batch, labels.tolist(), predicted, strict=True
            ):
                usable = [
                    (offset, id_to_label[prediction])
                    for offset, gold_id, prediction in zip(
                        offsets, gold_ids, predicted_ids, strict=True
                    )
                    if gold_id != -100
                ]
                token_offsets = [("", start, end) for (start, end), _ in usable]
                tags = [tag for _, tag in usable]
                predictions[str(rows[row_index]["id"])] = tags_to_spans(token_offsets, tags)
                row_index += 1
    return predictions


def train_transformer(config_path: Path, model_name: str) -> dict[str, Any]:
    """Fine-tune one configured checkpoint and select by validation macro-F1."""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    settings = config["transformer_training"]
    seed = int(config["project"]["random_seed"])
    set_seed(seed)
    entity_labels = list(config["annotation"]["labels"])
    bio_labels = ["O"] + [f"{prefix}-{label}" for label in entity_labels for prefix in ("B", "I")]
    label_to_id = {label: index for index, label in enumerate(bio_labels)}
    id_to_label = {index: label for label, index in label_to_id.items()}
    split_dir = Path(config["phase6"]["split_dir"])
    train_rows = read_jsonl(split_dir / "train.jsonl")
    validation_rows = read_jsonl(split_dir / "validation.jsonl")
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    train_dataset = NerDataset(train_rows, tokenizer, label_to_id, int(settings["max_length"]))
    validation_dataset = NerDataset(
        validation_rows, tokenizer, label_to_id, int(settings["max_length"])
    )
    generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(
        train_dataset,
        batch_size=int(settings["batch_size"]),
        shuffle=True,
        generator=generator,
        collate_fn=collate,
    )
    validation_loader = DataLoader(
        validation_dataset,
        batch_size=int(settings["batch_size"]),
        shuffle=False,
        collate_fn=collate,
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=len(bio_labels),
        id2label=id_to_label,
        label2id=label_to_id,
    ).to(device)
    optimizer = AdamW(model.parameters(), lr=float(settings["learning_rate"]))
    weighting_enabled = bool(settings.get("class_weighting", False))
    flattened_labels = [
        label for item in train_dataset.items for label in item["labels"] if label != -100
    ]
    counts = torch.bincount(torch.tensor(flattened_labels), minlength=len(bio_labels)).float()
    raw_weights = counts.sum() / (len(bio_labels) * counts.clamp(min=1))
    weights = raw_weights.pow(float(settings.get("class_weight_power", 0.5)))
    weights = (weights / weights.mean()).clamp(max=float(settings.get("maximum_class_weight", 8.0)))
    if not weighting_enabled:
        weights = torch.ones_like(weights)
    criterion = torch.nn.CrossEntropyLoss(weight=weights.to(device), ignore_index=-100)
    accumulation = int(settings["gradient_accumulation_steps"])
    safe_name = model_name.replace("/", "--")
    if weighting_enabled:
        safe_name += "--weighted"
    safe_name += str(settings.get("run_name_suffix", ""))
    output = Path(config["phase6"]["output_dir"]).parent / "transformers" / safe_name
    output.mkdir(parents=True, exist_ok=True)
    history: list[dict[str, float | int]] = []
    best_score = -1.0
    stale_epochs = 0
    for epoch in range(1, int(settings["epochs"]) + 1):
        model.train()
        optimizer.zero_grad()
        total_loss = 0.0
        for step, batch in enumerate(train_loader, start=1):
            batch.pop("offsets")
            labels = batch.pop("labels").to(device)
            inputs = {key: value.to(device) for key, value in batch.items()}
            logits = model(**inputs).logits
            loss = criterion(logits.view(-1, len(bio_labels)), labels.view(-1)) / accumulation
            loss.backward()
            total_loss += float(loss.item()) * accumulation
            if step % accumulation == 0 or step == len(train_loader):
                optimizer.step()
                optimizer.zero_grad()
        predictions = predict(model, validation_loader, validation_rows, id_to_label, device)
        metrics = exact_span_metrics(validation_rows, predictions, entity_labels)
        score = float(metrics["macro"]["f1"])
        history.append(
            {
                "epoch": epoch,
                "training_loss": total_loss / len(train_loader),
                "validation_macro_f1": score,
            }
        )
        LOGGER.info("%s epoch %s validation macro-F1 %.4f", model_name, epoch, score)
        if score > best_score:
            best_score = score
            stale_epochs = 0
            model.save_pretrained(output / "best_checkpoint")
            tokenizer.save_pretrained(output / "best_checkpoint")
            (output / "validation_metrics.json").write_text(
                json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
            )
            with (output / "validation_predictions.jsonl").open(
                "w", encoding="utf-8", newline="\n"
            ) as stream:
                for row in validation_rows:
                    task_id = str(row["id"])
                    stream.write(
                        json.dumps(
                            {
                                "id": task_id,
                                "gold": row.get("label", []),
                                "predicted": predictions.get(task_id, []),
                                "meta": row["meta"],
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
        else:
            stale_epochs += 1
            if stale_epochs >= int(settings["early_stopping_patience"]):
                break
    manifest = {
        "model": model_name,
        "device": str(device),
        "seed": seed,
        "train_tasks": len(train_rows),
        "validation_tasks": len(validation_rows),
        "test_set_used": False,
        "selection_metric": "validation_macro_f1",
        "class_weighting": weighting_enabled,
        "class_weight_power": float(settings.get("class_weight_power", 0.5)),
        "optimizer_updates_per_epoch": (len(train_loader) + accumulation - 1) // accumulation,
        "class_weights": {label: float(weights[index]) for index, label in enumerate(bio_labels)},
        "best_validation_macro_f1": best_score,
        "history": history,
        "corpus_status": "provisional_not_final_gold",
    }
    (output / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
