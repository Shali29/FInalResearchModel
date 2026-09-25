"""Create blank, provenance-rich annotation tasks without inventing labels."""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import random
import re
from pathlib import Path
from typing import Any

import yaml

from sri_lankan_legal_nlp.annotation.enrichment import (
    select_enriched_tasks,
    write_enriched_outputs,
)

LOGGER = logging.getLogger(__name__)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def _task_id(record_id: str, index: int) -> str:
    digest = hashlib.sha256(f"{record_id}|{index}".encode()).hexdigest()[:12]
    return f"annotation-{digest}"


def _split_text(text: str, maximum: int) -> list[tuple[str, int, int]]:
    """Group unmodified paragraphs and retain offsets into the source page text."""
    paragraphs = list(re.finditer(r"\S(?:.*?\S)?(?=\n\s*\n|\Z)", text, flags=re.DOTALL))
    if not paragraphs and text.strip():
        start = len(text) - len(text.lstrip())
        end = len(text.rstrip())
        paragraphs = [re.match(r"[\s\S]+", text[start:end])] if start == 0 else []
        if not paragraphs:
            return [(text[start:end], start, end)]

    segments: list[tuple[str, int, int]] = []
    for paragraph in paragraphs:
        start, end = paragraph.start(), paragraph.end()
        if end - start <= maximum:
            segments.append((text[start:end], start, end))
            continue
        cursor = start
        while cursor < end:
            target = min(cursor + maximum, end)
            if target < end:
                boundary = text.rfind("\n", cursor, target)
                if boundary <= cursor:
                    boundary = text.rfind(" ", cursor, target)
                target = boundary if boundary > cursor else target
            chunk_start = cursor
            chunk_end = target
            while chunk_start < chunk_end and text[chunk_start].isspace():
                chunk_start += 1
            while chunk_end > chunk_start and text[chunk_end - 1].isspace():
                chunk_end -= 1
            if chunk_start < chunk_end:
                segments.append((text[chunk_start:chunk_end], chunk_start, chunk_end))
            cursor = max(target, cursor + 1)
    return segments


def _label_studio_xml(labels: list[str]) -> str:
    colors = ["#D4380D", "#096DD9", "#389E0D", "#722ED1", "#D48806"]
    label_rows = "\n".join(
        f'    <Label value="{label}" background="{colors[index % len(colors)]}"/>'
        for index, label in enumerate(labels)
    )
    return (
        "<View>\n"
        '  <Header value="Sri Lankan Legal NER - information extraction, not legal advice"/>\n'
        '  <Header size="4" value="Quick label guide"/>\n'
        '  <Header size="5" value="FUNDAMENTAL_RIGHT: an explicitly protected right or freedom"/>\n'
        '  <Header size="5" value="OFFENSE: an act or omission expressly made punishable"/>\n'
        '  <Header size="5" value="PENALTY: a fine, imprisonment, forfeiture, '
        'or other punishment"/>\n'
        '  <Header size="5" value="CONSTITUTIONAL_BODY: the official name of a '
        'constitutional institution or office"/>\n'
        '  <Header size="5" value="TEMPORAL_ENTITY: a date, duration, deadline, or frequency"/>\n'
        '  <Header size="5" value="Use no label when none applies. Do not label '
        'Article, Section, Act, or amendment references."/>\n'
        '  <Text name="text" value="$text"/>\n'
        '  <Labels name="label" toName="text">\n'
        f"{label_rows}\n"
        "  </Labels>\n"
        "</View>\n"
    )


def _stratified_pilot(
    tasks: list[dict[str, Any]], requested_count: int, seed: int
) -> list[dict[str, Any]]:
    """Select a deterministic round-robin sample across language and document type."""
    if requested_count >= len(tasks):
        return tasks.copy()
    rng = random.Random(seed)
    strata: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for task in tasks:
        key = (task["meta"]["language"], task["meta"]["document_type"])
        strata.setdefault(key, []).append(task)
    for values in strata.values():
        rng.shuffle(values)
    selected: list[dict[str, Any]] = []
    keys = sorted(strata)
    while len(selected) < requested_count:
        made_progress = False
        for key in keys:
            if strata[key] and len(selected) < requested_count:
                selected.append(strata[key].pop())
                made_progress = True
        if not made_progress:
            break
    return selected


def _write_doccano(path: Path, tasks: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for task in tasks:
            stream.write(json.dumps(task, ensure_ascii=False) + "\n")


def _label_studio_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": task["id"],
            "data": {
                "research_task_id": task["id"],
                "text": task["text"],
                **task["meta"],
            },
        }
        for task in tasks
    ]


def prepare_annotation(config_path: Path) -> int:
    """Create blank Doccano and Label Studio tasks plus a progress tracker."""
    with config_path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    root = config_path.resolve().parents[1]
    source_path = root / config["paths"]["extracted_records"]
    output = root / config["paths"]["annotation"]
    output.mkdir(parents=True, exist_ok=True)
    allowed_quality = set(config["preparation"]["include_quality_statuses"])
    maximum = int(config["preparation"]["maximum_task_characters"])
    records = _read_jsonl(source_path)

    tasks: list[dict[str, Any]] = []
    for record in records:
        if record["quality_status"] not in allowed_quality or not record["text"].strip():
            continue
        for index, (text, start, end) in enumerate(_split_text(record["text"], maximum), start=1):
            metadata = {
                "parent_record_id": record["record_id"],
                "document_id": record["document_id"],
                "document_type": record["document_type"],
                "language": record["language"],
                "provision_type": record["provision_type"],
                "provision_number": record["provision_number"],
                "subsection": record["subsection"],
                "amendment_number": record["amendment_number"],
                "source_file": record["source_file"],
                "pdf_page_number": record["pdf_page_number"],
                "extraction_method": record["extraction_method"],
                "quality_status": record["quality_status"],
                "source_start": start,
                "source_end": end,
            }
            tasks.append(
                {
                    "id": _task_id(record["record_id"], index),
                    "text": text,
                    "label": [],
                    "meta": metadata,
                }
            )

    seed = int(config["project"]["random_seed"])
    pilot = _stratified_pilot(tasks, int(config["preparation"]["pilot_task_count"]), seed)
    _write_doccano(output / "doccano_tasks.jsonl", tasks)
    _write_doccano(output / "doccano_pilot_tasks.jsonl", pilot)
    (output / "label_studio_tasks.json").write_text(
        json.dumps(_label_studio_tasks(tasks), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output / "label_studio_pilot_tasks.json").write_text(
        json.dumps(_label_studio_tasks(pilot), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    labels = config["annotation"]["labels"]
    (output / "label_studio_config.xml").write_text(_label_studio_xml(labels), encoding="utf-8")
    (output / "labels.json").write_text(
        json.dumps(labels, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    enriched, enrichment_groups = select_enriched_tasks(
        tasks,
        config["preparation"]["enrichment_cues"],
        int(config["preparation"]["enriched_pilot_per_language_entity_group"]),
        seed,
    )
    write_enriched_outputs(output, enriched, enrichment_groups, seed)

    rng = random.Random(seed)
    shared_count = round(len(pilot) * config["preparation"]["shared_subset_fraction"])
    shared_ids = set(rng.sample([task["id"] for task in pilot], shared_count))
    shared_tasks = [task for task in pilot if task["id"] in shared_ids]
    _write_doccano(output / "doccano_shared_tasks.jsonl", shared_tasks)
    (output / "label_studio_shared_tasks.json").write_text(
        json.dumps(_label_studio_tasks(shared_tasks), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    fields = [
        "task_id",
        "language",
        "document_type",
        "source_file",
        "pdf_page_number",
        "shared_subset",
        "annotator_1",
        "annotator_1_status",
        "annotator_2",
        "annotator_2_status",
        "adjudication_status",
        "notes",
    ]
    with (output / "annotation_progress.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for task in pilot:
            writer.writerow(
                {
                    "task_id": task["id"],
                    "language": task["meta"]["language"],
                    "document_type": task["meta"]["document_type"],
                    "source_file": task["meta"]["source_file"],
                    "pdf_page_number": task["meta"]["pdf_page_number"],
                    "shared_subset": "yes" if task["id"] in shared_ids else "no",
                    "annotator_1_status": "not_started",
                    "annotator_2_status": "not_started"
                    if task["id"] in shared_ids
                    else "not_required",
                    "adjudication_status": "not_started"
                    if task["id"] in shared_ids
                    else "not_required",
                }
            )
    LOGGER.info(
        (
            "Created %s blank tasks, selected %s general pilot tasks, %s enriched tasks, "
            "and assigned %s general shared tasks."
        ),
        len(tasks),
        len(pilot),
        len(enriched),
        shared_count,
    )
    return 0
