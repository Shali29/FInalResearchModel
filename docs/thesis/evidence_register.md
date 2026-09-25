# Thesis Evidence Register and Completion Control

## Evidence classification

- `VERIFIED`: supported by a saved source or experiment artifact.
- `PROVISIONAL`: observed, but based on incomplete/unadjudicated data.
- `PENDING`: planned but not performed.
- `UNSUPPORTED`: stated in a draft without an available source file.

## Current claims

| Claim | Status | Evidence/action |
|---|---|---|
| Research covers Constitution and Penal Code in English and Sinhala | VERIFIED | Research reports and current scope |
| Five approved entity classes | VERIFIED | Interim methodology and `ner_config.yaml` |
| LawGPT evaluation is part of final thesis | REMOVED | Explicit researcher decision; revise Objective 5 |
| 12 PDFs and 1,062 processed pages | VERIFIED | Phase 2 outputs |
| 2,328 candidate provisions | VERIFIED | Phase 2 outputs |
| 8,378 segmented blank annotation tasks | VERIFIED | `doccano_tasks.jsonl` line count |
| 160 provisional bilingual pairs | PROVISIONAL | Phase 3 outputs; manual verification incomplete |
| 80 annotated tasks and 297 spans | PROVISIONAL | `provisional_combined_corpus.jsonl` |
| Kappa 0.6466 and exact-span F1 0.5304 | PROVISIONAL | agreement report; adjudication not final gold |
| Final NER accuracy/F1 | PENDING | Existing values are validation pilots only |
| mBERT/XLM-R produced F1 = 0.0 | VERIFIED-PROVISIONAL | Saved validation manifests and metrics |
| 420 expansion tasks are annotated | FALSE/PENDING | Tasks are blank and await humans |
| Survey with 31 adults and subgroup counts 21/7/3 | UNSUPPORTED IN REPOSITORY | Supply raw anonymised export, consent/ethics evidence, and analysis script |
| Survey difficulty/usefulness percentages | UNSUPPORTED IN REPOSITORY | Do not use until raw survey file is supplied and recalculated |
| Text simplification improves readability >30% | TARGET ONLY | Requires real paired evaluation |
| Citizen comprehension >80% | TARGET ONLY | Requires consented user study |
| Amendment tracking accuracy >90% | TARGET ONLY | Requires verified gold events and defined metric |
| Prototype usability and task success | PENDING | Prototype/user study not complete |

## Required thesis corrections

1. Replace Interim Objective 5 (LawGPT evaluation) with integrated prototype and usability
   evaluation, and document the scope change.
2. Remove every LawGPT workflow, comparison, result, and claim from methodology through conclusion.
3. Correct the older report's English/Tamil corpus statement to English/Sinhala.
4. Do not claim constitutional amendments affect Penal Code provisions without explicit source
   evidence.
5. Distinguish 1,062 physical pages from unique legal content and overlapping documents.
6. Do not call 160 alignments bilingual gold; they remain provisional.
7. Do not call the 420 expansion records an annotated corpus until human exports are validated.
8. Do not report model targets as achieved results.
9. Explain that 2,328 candidate provisions were segmented into 8,378 blank annotation tasks; do
   not present either count without its unit and generation stage.
10. Verify every bibliographic entry, DOI, title, venue, volume, pages, and year against the original
    publication before submission.

## Data required from the researcher

- Anonymised raw survey export and questionnaire, if the 31-participant study actually occurred.
- Ethics/consent approval or the approved consent text for human studies.
- Human-completed expansion annotation exports.
- Human-verified simplification examples and expert/citizen evaluation data.
- Human-verified amendment event gold records.
- Final prototype test and usability data.
- Written confirmation/approval of the LawGPT scope removal if available.

Until these exist, the thesis must use explicit `PENDING — NOT YET MEASURED` markers rather than
plausible-looking numeric replacements.
