# Phase 6 — Legal NER (Baseline Stage)

## Objective and inputs

This stage establishes reproducible, explainable baselines before transformer training. It uses
`data/splits/provisional/train.jsonl` for fitting and `validation.jsonl` for evaluation. The held-out
test set was not loaded for evaluation or model selection.

## Provisional validation results

| Model | Exact-span micro-F1 | Exact-span macro-F1 | English micro-F1 | Sinhala micro-F1 |
|---|---:|---:|---:|---:|
| Training-derived dictionary | 0.0758 | 0.0833 | 0.3200 | 0.0187 |
| CRF | 0.1224 | 0.0808 | 0.2609 | 0.0000 |

These are real validation outputs, but they are not final thesis test results. The low scores are
consistent with a very small provisional corpus, limited repeated entity phrases, annotation
disagreement, and single-annotator gap examples. They must not be presented as achieved target
performance. Neither the English target above 85% nor Sinhala target above 75% can currently be
claimed.

The dictionary baseline learns exact entity strings from training annotations only and performs
longest-first non-overlapping matching. The CRF uses explainable word form, case, number,
prefix/suffix, and adjacent-token features. The Unicode tokenizer explicitly preserves Sinhala
combining marks and zero-width joiners.

## Outputs

- `results/ner/baselines/dictionary_validation_metrics.json`
- `results/ner/baselines/dictionary_validation_predictions.jsonl`
- `results/ner/baselines/crf_validation_metrics.json`
- `results/ner/baselines/crf_validation_predictions.jsonl`
- `results/ner/baselines/crf_model.joblib`
- `results/ner/baselines/run_manifest.json`

The next execution step is validation-only training for mBERT and XLM-R. Model selection must use
validation macro-F1; the untouched test set remains closed until one final model configuration is
selected.

## Transformer implementation status

The mBERT/XLM-R token-classification pipeline is implemented with character-to-subword BIO
alignment, `-100` masking for special/padding tokens, fixed seeds, CPU/GPU detection, gradient
accumulation, validation macro-F1 checkpoint selection, and early stopping. CPU-safe defaults are
stored in `configs/ner_config.yaml`.

The local environment reports PyTorch as CPU-only. An automated mBERT run was attempted, but the
external checkpoint retrieval remained idle and produced no model files or metrics, so the process
was stopped. No transformer result is claimed. Run the documented command again when Hugging Face
model downloads are available; CPU fine-tuning can take substantially longer than GPU training.

The subsequent user-run download succeeded. The first unweighted mBERT experiment stopped after
two epochs through early stopping and obtained validation macro-F1 0.0: it predicted only the
dominant non-entity (`O`) class (37 false negatives and no entity predictions). This is retained as
a real negative baseline under `bert-base-multilingual-cased--unweighted`; it is not a system error
and is not a final test result.

Inverse-square-root BIO-label weighting is now enabled from training-set counts, normalized and
capped at 8.0. Weighted runs are saved separately with a `--weighted` suffix so the unweighted
result remains reproducible. This change uses training labels only and does not inspect the test
set.

A stronger small-corpus mBERT experiment used inverse-frequency weighting and 28 optimizer updates
per epoch. It also obtained exact-span validation macro-F1 0.0, but for the opposite reason: its
saved validation predictions contained 441 false-positive spans (437 `PENALTY` and 4
`CONSTITUTIONAL_BODY`) and no exact true positives, against 37 gold spans. Thus the stronger weights
overcorrected the all-`O` behavior. After three mBERT configurations on the same 12-task validation
set, further mBERT tuning is stopped to limit validation overfitting. This is reported as a model
and data limitation, not hidden or converted into a claimed result.

The required main bilingual `xlm-roberta-base` experiment then used moderate square-root class
weighting, 28 optimizer updates per epoch, and early stopping. It completed three epochs with
falling training loss (1.9478, 1.7256, 1.4404), but exact-span validation macro-F1 remained 0.0.
The selected checkpoint predicted four `OFFENSE` spans; none exactly matched the 37 gold spans
(`tp=0`, `fp=4`, `fn=37`). The test set remained untouched. Further transformer tuning is deferred
until the annotated corpus is expanded and independently reviewed.

## Expanded-corpus baseline rerun

After completion of the five-part, 420-task Annotator 1 expansion, the baselines were rerun using
the 350-task training set and the 75-task validation set under
`data/splits/expanded_provisional/`. The 75-task held-out test set was not evaluated.

| Model | Exact-span micro-F1 | Exact-span macro-F1 | English micro-F1 | Sinhala micro-F1 |
|---|---:|---:|---:|---:|
| Training-derived dictionary | 0.1077 | 0.0672 | 0.1212 | 0.0863 |
| CRF | 0.1985 | 0.1208 | 0.2118 | 0.1594 |

The expanded CRF improves over the earlier 80-task provisional run, but performance remains well
below the proposed targets. `FUNDAMENTAL_RIGHT` and `TEMPORAL_ENTITY` have zero exact-match F1 in
this validation run, and the expansion has only one annotator so far. These are provisional
technical results, not final thesis test results. Detailed metrics and predictions are stored in
`results/ner/expanded_baselines/`.
