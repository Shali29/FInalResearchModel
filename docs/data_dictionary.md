# Data Dictionary

This document defines the minimum provenance fields. It will be expanded with validated Phase 2
schemas before any corpus output is considered stable.

| Field | Type | Meaning |
|---|---|---|
| `record_id` | string | Stable unique identifier generated from document and structural context |
| `document_id` | string | Stable identifier for the source legal instrument/edition |
| `document_type` | enum | `constitution`, `penal_code`, or `amendment` |
| `document_title` | string | Title transcribed from the source, pending verification where necessary |
| `language` | enum | `en` or `si` |
| `provision_type` | string/null | For example `article`, `section`, `schedule`, or `unknown` |
| `provision_number` | string/null | Source-preserving provision identifier; never coerced to an integer |
| `subsection` | string/null | Source-preserving nested identifier |
| `text` | string | Original extracted legal text in UTF-8 |
| `source_file` | string | Source PDF filename |
| `source_sha256` | string | SHA-256 digest of the source PDF |
| `pdf_page_number` | integer | One-based physical PDF page index |
| `printed_page_label` | string/null | Page label printed in the document, if recoverable |
| `amendment_number` | string/null | Verified amendment/Act identifier |
| `extraction_method` | enum | `embedded_text`, `ocr_eng`, `ocr_sin`, or `manual_transcription` |
| `quality_status` | enum | `verified`, `pending_review`, `low_quality`, or `rejected` |
| `verification_notes` | string/null | Human-review notes; not a legal interpretation |

Page number is intentionally split into physical PDF position and printed label because the
supplied `Penal-Code I.pdf` demonstrates that these can differ.
