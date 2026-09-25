# Thesis Metrics, Formulas, and Verified Calculations

## Reporting rule

Only values linked to a machine-readable file or documented human-evaluation dataset are
`OBSERVED`. Planned thresholds are `TARGETS`, not results. Unavailable values remain `PENDING`.

## Named-entity recognition

For each entity class, exact match requires identical start boundary, end boundary, and label.

\[
Precision = \frac{TP}{TP+FP}
\]

\[
Recall = \frac{TP}{TP+FN}
\]

\[
F_1 = \frac{2PR}{P+R} = \frac{2TP}{2TP+FP+FN}
\]

Micro-F1 pools TP, FP, and FN across classes. Macro-F1 is the unweighted arithmetic mean of the
five class-specific F1 scores:

\[
MacroF_1 = \frac{1}{5}\sum_{c=1}^{5}F_{1,c}
\]

For five development folds:

\[
\bar{x}=\frac{1}{5}\sum_{i=1}^{5}x_i
\]

\[
s=\sqrt{\frac{\sum_{i=1}^{5}(x_i-\bar{x})^2}{5-1}}
\]

Do not calculate fold mean/SD until all five comparable fold runs exist.

### Observed provisional validation results

Source: `results/ner/provisional_validation_summary.json`.

| Model | Exact-span micro-F1 | Exact-span macro-F1 | Status |
|---|---:|---:|---|
| Training-derived dictionary | 0.0758 | 0.0833 | OBSERVED, provisional validation |
| CRF | 0.1224 | 0.0808 | OBSERVED, provisional validation |
| mBERT unweighted | 0.0000 | 0.0000 | OBSERVED, provisional validation |
| mBERT strongly weighted | 0.0000 | 0.0000 | OBSERVED, provisional validation; 441 FP |
| XLM-R moderately weighted | 0.0000 | 0.0000 | OBSERVED, provisional validation; 4 FP, 37 FN |

These are not held-out final-test or five-fold results. The targets English F1 > 0.85 and Sinhala
F1 > 0.75 were **not achieved in the provisional experiments**.

## Inter-annotator agreement

Observed shared-subset counts: annotator 1 = 188 spans, annotator 2 = 125 spans, exact shared
spans = 83.

Taking annotator 1 as the comparison reference for this directional span calculation:

\[
P=\frac{83}{125}=0.6640
\]

\[
R=\frac{83}{188}=0.4415
\]

\[
F_1=\frac{2(0.6640)(0.4415)}{0.6640+0.4415}=0.5304
\]

Token Cohen's kappa:

\[
\kappa=\frac{p_o-p_e}{1-p_e}
\]

Observed `kappa = 0.6466`, from `results/ner/inter_annotator_agreement.json`. Report exact-span
agreement with kappa because non-entity tokens can inflate token agreement. The planned kappa
threshold > 0.80 was not reached.

## Corpus and split statistics

| Measure | Verified value | Evidence |
|---|---:|---|
| Source PDFs | 12 | extraction manifest/report |
| Physical PDF pages processed | 1,062 | extraction report |
| Embedded-text usable pages | 867 | extraction report |
| OCR-usable pages | 188 | extraction report |
| Rejected pages | 7 | extraction report |
| Candidate provisions | 2,328 | extraction report |
| Segmented blank annotation tasks | 8,378 | `doccano_tasks.jsonl` line count |
| Provisional aligned pairs | 160 | alignment report |
| Current annotated tasks | 80 | combined provisional corpus |
| Current entity spans | 297 | combined provisional corpus |
| Provisional train/validation/test tasks | 56 / 12 / 12 | split manifest |
| Parent-group leakage | 0 intersections | split manifest |
| Blank expansion tasks | 420 | expansion manifest |
| Double-annotation expansion tasks | 84 | expansion manifest |

The 2,328 provisions and 8,378 tasks measure different units: long candidate provisions were split
into smaller annotation tasks. Always label the units explicitly rather than comparing the counts
as though they describe the same object.

## Amendment tracking

Use a human-verified event set. Required formulas:

\[
Reference\ F_1=\frac{2TP}{2TP+FP+FN}
\]

\[
Operation\ Accuracy=\frac{Correct\ operation\ labels}{All\ gold\ events}
\]

\[
Linking\ Accuracy=\frac{Correct\ affected\ provision\ links}{All\ gold\ events}
\]

\[
Unresolved\ Rate=\frac{Events\ flagged\ unresolved}{All\ processed\ events}
\]

All amendment metric values are currently `PENDING`.

## Simplification

Entity and citation preservation:

\[
Preservation\ Rate=\frac{Required\ items\ retained}{Required\ items\ in\ source}
\]

Comprehension accuracy:

\[
Comprehension=\frac{Correct\ answers}{Total\ questions}
\]

Relative comprehension improvement, when the baseline is non-zero:

\[
Improvement\ \%=\frac{Post-Pre}{Pre}\times100
\]

Report absolute percentage-point change alongside relative improvement. Use no English readability
formula for Sinhala unless its validity for Sinhala is independently justified. All simplification
values are currently `PENDING`.

## Prototype evaluation

\[
Task\ Success=\frac{Successfully\ completed\ tasks}{All\ attempted\ tasks}
\]

Report median completion time and interquartile range for skewed timings. For Likert items, report
item distributions and median/IQR; a mean may be added only with a clear justification. Report
sample size for every subgroup. All prototype/user-evaluation values are currently `PENDING`.

## Confidence intervals and significance

Use bootstrap confidence intervals for entity-level F1 only when the final test set has enough
independent provision groups. Resample parent provisions, not individual tokens. Do not conduct
hypothesis tests solely because software makes them available. State the test, assumptions, sample
size, effect size, confidence interval, and p-value where inferential analysis is justified.
