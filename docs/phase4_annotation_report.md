# Phase 4 — Annotation Preparation

## Objective

Prepare provenance-preserving blank tasks for manual Legal NER annotation. No entity annotation is
generated automatically or represented as ground truth.

## Inputs

- Phase 2 page records in `data/extracted/records.jsonl`
- the five-class schema in `configs/ner_config.yaml`

## Outputs

- full Doccano pool: `data/annotation/doccano_tasks.jsonl`
- 500-task Doccano pilot: `data/annotation/doccano_pilot_tasks.jsonl`
- full and pilot Label Studio imports
- Label Studio XML configuration and JSON label list
- a 500-row annotation progress tracker
- a deterministic 50-task shared subset for two independent annotators
- validation, BIO CoNLL export, and agreement calculation modules

Tasks retain the parent extraction record, document type, language, source filename, physical page,
extraction method, quality state, and source character offsets. Rejected and low-quality extraction
records are excluded by configuration.

## Current limitations

The extracted corpus is page-bounded. Tasks therefore use exact paragraph/chunk spans from the
page text rather than asserting unverified Article/Section boundaries. All labels remain empty.
The pilot requires human annotation and adjudication before Phase 5 data splitting or Phase 6
training can produce research results.

After the initial general pilot yielded very few annotated entities, an additional entity-enriched
pilot was generated. It contains 50 English and 50 Sinhala tasks for each of five heuristic cue
groups, for 500 tasks total. Cues influence task selection only: they do not create annotations,
do not guarantee that an entity exists, and must not be treated as ground truth. The enriched
progress tracker records the selection cue for sampling-bias analysis.

For independent annotation, import `label_studio_pilot_tasks.json` into the first project and
`label_studio_shared_tasks.json` into a separate second project. Do not reveal the first
annotator's labels to the second annotator before both exports are complete.

Each Label Studio task includes a stable `research_task_id` inside its `data` object. The conversion
script preserves this ID, validates that exactly one active annotation exists per submitted task,
and converts character spans to canonical JSONL. The agreement script joins only shared IDs and
reports exact-span precision, recall, F1, and token-level Cohen's kappa.

## Initial shared-subset agreement

The two annotators completed the same 50 tasks. Raw exports were preserved. Derived clean copies
trimmed boundary whitespace and applied only logged researcher-confirmed overlap corrections from
`configs/annotation_corrections.yaml`.

- Annotator 1 entities after normalization: 188
- Annotator 2 entities after normalization: 125
- Exact-span true positives: 83
- Exact-span precision: 0.664
- Exact-span recall: 0.4415
- Exact-span F1: 0.5304
- Token-level Cohen's kappa: 0.6466

The proposed kappa threshold above 0.80 was not achieved in this initial round. Token kappa must
also be interpreted cautiously because non-entity tokens can inflate it. The 147 disputed span
decisions in `data/annotation/adjudication_sheet.csv` require human adjudication and should inform
revisions to the guidelines before the shared subset is relabeled or finalized as gold data.

## Corpus expansion after the provisional model experiments

Following zero-F1 provisional transformer experiments, a blank 420-task expansion batch was
created under `data/annotation/expansion/`. It contains 220 English and 200 Sinhala tasks, all from
unique parent records and with no task-ID overlap with the existing 80-task corpus. Eighty-four
tasks (20%) are reserved for independent double annotation. Selection cues are recorded for audit,
but no entity labels were generated. See `docs/expansion_annotation_instructions.md`.
