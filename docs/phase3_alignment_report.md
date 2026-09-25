# Phase 3 — Bilingual Alignment

## Objective

Link corresponding English and Sinhala provisions without treating matching PDF page numbers as
evidence of translation equivalence.

## Inputs

- `data/extracted/records.jsonl`
- `data/extracted/provision_candidates.jsonl`
- canonical document-pair declarations in `configs/data_config.yaml`

## Method

The baseline matches document type, provision type, and provision number. A pair is emitted only
when the structural key occurs exactly once in each configured language document. Page numbers
are retained solely as provenance. Text similarity cannot override an ambiguous legal reference.

The configured pairs are the consolidated English and Sinhala Constitution and the English Penal
Code consolidated through 2006 with the supplied Sinhala Penal Code scan. Sinhala-only amendment
Acts are not force-linked to material inside the English collection.

## Automated run

- 160 provisional exact unique pairs
- 468 unmatched structural keys
- 206 duplicate or ambiguous structural keys
- 0 automatically asserted conflicts
- 0 low-confidence text-similarity pairs

Of the provisional pairs, 5 are Constitution pairs and 155 are Penal Code pairs. All remain
`pending_review`. The small number of unambiguous Constitution pairs reflects repeated numbered
lines and contents/index entries in the current candidate data; it does not mean the bilingual
Constitutions contain only five corresponding Articles.

## Outputs

- `data/aligned/alignments.jsonl`
- `data/aligned/alignment_issues.jsonl`
- `data/aligned/alignment_review.csv`
- `data/aligned/alignment_report.md`

## Remaining manual work

1. Correct confirmed OCR digit errors in a derived layer while retaining original OCR.
2. Verify which numbered headings are Articles/Sections rather than contents or numbered clauses.
3. Review each provisional pair and complete `alignment_review.csv`.
4. Verify amendment identities before amendment-level bilingual alignment.

Phase 3 software and the automated baseline are complete. The alignment is not a gold alignment
until the review sheet is completed by an English/Sinhala-fluent reviewer.
