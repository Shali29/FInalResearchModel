# Phase 7 — Legal Text Simplification

## Objective

Prepare a controlled plain-Sinhala simplification workflow without fabricating translations,
expert judgments, or supervised training data. Translation and simplification remain separate.

## Data-readiness result

No expert-verified complex-legal/plain-Sinhala pairs and no lawyer-verified glossary entries were
found. Supervised sequence-to-sequence training is therefore not supported and was not run.

The audit read 1,062 extracted records. Seven were rejected from the review batch because their
text failed the Unicode integrity gate, including mojibake patterns found in some records marked
as Sinhala. Source extraction files were not altered. From the 1,055 usable records, the pipeline
created a deterministic 100-record review template.

## Safeguards and outputs

- English inputs keep `translated_sinhala` empty and require human translation.
- Sinhala inputs retain the original text but keep `simplified_sinhala` empty.
- Only glossary entries marked `verified_by_legal_expert` may be applied.
- Source file, page, document type, entities, statuses, and disclaimer are retained.
- Every generated task remains `pending_expert_review`.
- No readability, comprehension, legal-accuracy, hallucination, or omission result is claimed.

Outputs:

- `results/simplification/data_readiness_report.json`
- `results/simplification/expert_review_tasks.jsonl`

Run with:

```powershell
python -m sri_lankan_legal_nlp simplify --config configs\simplification_config.yaml
```

The next human step is to create and legally review Sinhala translations, plain-Sinhala drafts,
and glossary entries. Those verified records are prerequisites for quantitative evaluation and
any supervised model experiment.
