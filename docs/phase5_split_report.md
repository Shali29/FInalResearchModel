# Phase 5 — Leakage-Safe Data Splitting

## Outcome

The combined provisional NER corpus contains 80 tasks and 297 entity spans. A deterministic,
group-preserving 70/15/15 split was created with random seed 2026:

| Set | Tasks | Parent groups |
|---|---:|---:|
| Train | 56 | 54 |
| Validation | 12 | 12 |
| Untouched test | 12 | 12 |

No `parent_record_id` occurs in more than one set. Five grouped cross-validation folds were also
created from the 68-task development portion (train plus validation). The held-out test set is not
used in those folds.

Every English/Sinhala entity-class combination occurs in train, validation, and test. The corpus
has only two independent Sinhala amendment parent groups, however, so amendment documents cannot
occur in all three sets: validation has no amendment task. Amendment-document NER results therefore
cannot be estimated separately and reliably from this pilot corpus.

## Annotation-quality qualification

These splits are **provisional, not final gold data**. Part of the corpus comes from an
OpenAI-assisted adjudication draft accepted by the researcher for experimentation but still marked
`pending_human_approval`; the targeted gap batch has one annotator. Those statuses remain in the
records and manifest and must be disclosed in thesis reporting. The initial shared-subset agreement
was Cohen's kappa 0.6466 and exact-span F1 0.5304, below the planned kappa threshold above 0.80.

## Artifacts

- `data/processed/provisional_combined_corpus.jsonl`
- `data/splits/provisional/train.jsonl`
- `data/splits/provisional/validation.jsonl`
- `data/splits/provisional/test.jsonl`
- `data/splits/provisional/fold_1_train.jsonl` through `fold_5_validation.jsonl`
- `data/splits/provisional/split_manifest.json`

These files allow Phase 6 pipeline testing and provisional experiments. Final thesis model results
must be rerun after human approval/adjudication and, ideally, independent review of the targeted
gap annotations.
