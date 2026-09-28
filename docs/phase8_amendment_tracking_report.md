# Phase 8 — Amendment Tracking

## Objective

Extract traceable amendment-operation candidates from the supplied amendment documents, identify
affected provision references, and prepare a human-verification workflow. Automatic consolidation
is prohibited until references, operations, and source wording are verified.

## Inputs and collection boundary

The extraction corpus currently contains 49 pages classified as amendments, covering seven
Sinhala Penal Code amendment documents. No English amendment page is currently represented under
the extraction record type `amendment`. The supplied collection is incomplete and must not be
described as a complete legislative history.

## Deterministic baseline result

The parser identified 67 provision-reference candidates:

| Parsed operation | Candidate count |
|---|---:|
| Substitution | 44 |
| Insertion | 1 |
| Unresolved or multiple cues | 22 |
| **Total** | **67** |

These are unverified candidates, not accuracy results. A candidate can contain OCR errors, refer to
a provision quoted inside replacement text, or include more than one operation. The parser
therefore does not automatically change the Penal Code.

## Outputs

- `results/amendments/amendment_candidates.jsonl`: provenance-preserving machine candidates
- `results/amendments/amendment_review.csv`: UTF-8 spreadsheet for human verification
- `results/amendments/amendment_tracking_report.json`: auditable run summary

Run the phase with:

```powershell
python -m sri_lankan_legal_nlp track-amendments --config configs\amendment_config.yaml
```

## Required human review

Open `amendment_review.csv` and complete the reviewer columns. Confirm whether the detected
reference is actually the amendment target, select the correct operation, enter the linked source
record only after checking the principal enactment, and record OCR or legal ambiguity in the
notes. Do not enter reconstructed text unless the complete original and replacement wording have
been verified against the official sources.

Accuracy, macro-F1, linking accuracy, reconstructed-text correctness, completeness, and unresolved
rate against gold data are unavailable until this review creates a manually verified gold set.
