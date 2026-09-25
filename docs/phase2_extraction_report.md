# Phase 2 Legal-Document Extraction Report

## Objective

Create reproducible UTF-8 text and structured page records from every supplied legal PDF while
preserving source identity, physical PDF page provenance, extraction method, and review status.
No source PDF was modified.

## Inputs and command

- 12 configured PDFs under `F:/Me/Research/Dataset/Constitution_&_Penalcode`
- `configs/data_config.yaml`
- PyMuPDF embedded-text extraction
- Tesseract 5.4 with portable English and Sinhala language data

```powershell
.\.venv\Scripts\Activate.ps1
python -m sri_lankan_legal_nlp extract --config configs\data_config.yaml
```

OCR output is cached by document and physical page. Re-running the command revalidates sources
and rebuilds reports without repeating completed OCR pages.

## Generated outputs

All outputs are under `data/extracted/`:

| Output | Purpose |
|---|---|
| `manifest.jsonl` | PDF identity, SHA-256, edition note, page totals, methods, and status |
| `records.jsonl` | One validated, page-bounded record per physical PDF page |
| `text/en/`, `text/si/` | UTF-8 text with explicit `[[PDF_PAGE_N]]` markers |
| `page_quality.jsonl` | Machine-readable page diagnostics and warnings |
| `extraction_quality.csv` | Spreadsheet-friendly quality report |
| `uncertain_segments.jsonl` | All records not yet human-verified |
| `rejected_segments.jsonl` | Seven pages that failed automated quality gates |
| `provision_candidates.jsonl` | Conservative Article/Section candidates, all pending review |
| `corpus_statistics.json` | Descriptive counts by language and document type |
| `ocr_cache/` | Resumable page-level OCR cache |

## Measured results

These are extraction measurements, not legal or model-performance results.

| Measure | Count |
|---|---:|
| Source PDFs | 12 |
| Physical PDF pages / page records | 1,062 |
| Usable embedded-text pages | 867 |
| Usable Sinhala OCR pages | 188 |
| Rejected pages | 7 |
| Provision-heading candidates | 2,328 |
| Explicit-label candidates | 54 |
| Numbered-line candidates | 2,274 |

| Language | Document type | Total | Usable | Rejected | Estimated sentences | Estimated tokens |
|---|---|---:|---:|---:|---:|---:|
| English | Constitution | 306 | 306 | 0 | 3,787 | 70,668 |
| English | Penal Code | 278 | 278 | 0 | 5,517 | 131,514 |
| Sinhala | amendments | 49 | 49 | 0 | 768 | 17,600 |
| Sinhala | Constitution | 289 | 283 | 6 | 4,264 | 105,359 |
| Sinhala | Penal Code | 140 | 139 | 1 | 4,026 | 112,792 |

Sentence and token counts are descriptive rule-based estimates, not linguistic gold counts or
transformer-token counts.

## Rejected pages

- `constitution-si.pdf`: physical pages 2, 6, 22, 24, 250, and 252
- `දණ්ඩ නීති සංග්_රහය.pdf`: physical page 1

Most are sparse/front-matter candidates below the 40-visible-character threshold after OCR.
Page 2 of the Sinhala Constitution became empty after an exact repeated boundary line was
removed. They remain in both `records.jsonl` and `rejected_segments.jsonl`; nothing was silently
discarded.

## Quality interpretation

- No extracted record is automatically declared legally verified.
- OCR produced Sinhala Unicode, but the pilot showed recognition errors; success is not accuracy.
- Exact repeated boundary lines are removed only when present on at least 60% of document pages.
- Legal punctuation, digits, subsection markers, negation, and references are not intentionally
  stripped.
- Provision candidates are not confirmed/deduplicated provision counts. Contents entries,
  footnotes, overlapping editions, and OCR errors can produce false positives.
- Printed page labels remain null unless safely recoverable; physical PDF page numbers are always
  retained.

## Validation performed

- 12 automated tests passed and Ruff reported all checks passed.
- All JSONL rows validated against strict Pydantic schemas.
- Exactly 1,062 page records map to 1,062 manifest PDF pages.
- Record IDs are unique and deterministic.
- Source SHA-256 values match the manifest; raw PDFs were unchanged.
- Usable Sinhala records decode as UTF-8 without Unicode replacement characters.
- The source registry matches discovered PDF filenames exactly.

## Manual work required before Phase 3

1. Review the seven rejected pages against the PDF images.
2. Sample OCR from every Sinhala source, especially section numbers, dates, penalties, negation,
   and amendment operations.
3. Review provision candidates and remove contents-page/footnote false positives.
4. Choose the canonical English Penal Code edition and deduplicate overlapping text.
5. Verify each amendment's official title, Act number, date, and edition metadata.

## Initial visual review completed

The seven rejected pages and one OCR page from each scanned/legacy-font Sinhala source were
rendered and compared visually. Decisions are recorded in
`data/extracted/manual_review_ledger.csv`.

- The six rejected Sinhala Constitution pages appear blank and are classified for exclusion as
  blank pages, not extraction failures containing missed legal text.
- Sinhala Penal Code page 1 is a cover carrying title/edition metadata and should be retained as
  metadata, not provision text.
- All eight sampled OCR body pages require human correction. OCR is readable enough to support
  review, but word-level errors and, in the 2002 sample, material digit errors make it unsafe for
  direct annotation or amendment application.
- Researcher decision on 2026-09-13: `Penal Code.pdf` is the canonical English consolidated base
  through Act 16/2006. `Penal-Code I.pdf` is used as the source collection for later English
  amendment Acts. Both retain provenance, and overlapping base text must not be counted twice.

## Completion checklist

- [x] Recursive PDF discovery and exact registry check.
- [x] SHA-256 manifest.
- [x] Embedded-text-first extraction.
- [x] English/Sinhala OCR fallback and resumable cache.
- [x] NFC normalization and Sinhala Unicode checks.
- [x] Conservative repeated boundary removal with warnings.
- [x] Page provenance and extraction method retained.
- [x] Text, JSONL, quality CSV, rejected queue, manifest, and statistics generated.
- [x] Conservative provision candidates generated.
- [x] Automated schema, coverage, checksum, Unicode, unit, and lint checks passed.
- [x] Seven rejected pages visually classified at the technical/document level.
- [x] One OCR page per scanned/legacy Sinhala source visually sampled.
- [ ] Sinhala-fluent legal reviewer corrects/approves sampled OCR and expands review.
- [ ] Provision candidates confirmed and deduplicated.
- [x] Canonical English Penal Code role confirmed by the researcher.

The Phase 2 software and automated extraction run are complete. The corpus is **provisional**, not
legally verified, until the manual-review items are completed.
