# Assumptions and Decision Log

## Phase 0 assumptions

1. The path written by the researcher as `Constitution/_&/_Penalcode` refers to the existing
   directory `F:/Me/Research/Dataset/Constitution_&_Penalcode`.
2. The malformed source path notation in the request refers to the verified files
   `F:/Me/Research/IM_2021_118_Research report.pdf` and
   `F:/Me/Research/Interim/IM_2021_118-Interim.pdf`.
3. `IM_2021_118_Research report.pdf` and `IM-2021-118.pdf` are treated as duplicate copies because
   their SHA-256 digests are identical.
4. PDF page counts in the Phase 0 audit mean physical PDF pages inferred from `pdftotext` page
   boundaries. Printed page labels can differ and will be stored separately where recoverable.
5. The filenames of Sinhala amendment PDFs are discovery hints, not verified legal metadata.
   Dates, Act numbers, titles, language, and authority must be extracted and reviewed.
6. The phrase "chapter XII, XXIV for amendment" is not interpreted as a set of constitutional
   amendment Acts. In a consolidated Constitution, chapters and amendment source instruments are
   different structural concepts.
7. The current five-class entity schema is frozen for Phase 0. Legal provision/reference spans are
   a pending design decision and will not be silently added.
8. The consolidated Constitution may support current-text analysis and some footnote-level change
   provenance, but complete historical reconstruction is considered unsupported until standalone
   amendment sources or another authoritative version history is available.
9. No extracted text, annotation, model result, legal relationship, or document completeness claim
   is considered verified merely because a filename or report asserts it.

## Phase 1 assumptions

1. `F:/Me/Research/Final/MyResearchModel` is the project root corresponding to the requested
   `sri_lankan_legal_nlp/` tree. A second nested project directory is intentionally not created.
2. Raw PDFs remain at their existing external location during Phase 1. Whether to copy them into
   `data/raw/` or reference them through a manifest will be decided in Phase 2; neither choice may
   alter the originals.
3. Python 3.11 is the reproducibility target. No functioning Python installation was available at
   the Phase 1 audit, so executable Python tests remain pending until it is installed.
4. Dependency ranges in `requirements.txt` are installation constraints, not a record of the
   environment. Exact resolved versions must be captured with `pip freeze` after installation.

## Decisions requiring confirmation before later phases

- Whether to annotate `LEGAL_REFERENCE`/`LEGAL_PROVISION`, or store provision references only as
  deterministic structural metadata.
- Which copies/editions of the two English Penal Code PDFs are canonical, and how overlapping text
  will be deduplicated.
- Whether standalone official constitutional amendment Acts will be supplied or acquired.
- Whether missing English/Sinhala counterparts should remain explicitly unmatched rather than be
  translated for corpus alignment (recommended: remain unmatched).
- Availability of legal experts, annotators, user-study ethics approval, and a reviewed bilingual
  glossary.

## Phase 2 assumptions and decisions

1. Physical PDF page numbers are the machine provenance key. Printed labels remain null unless
   recoverable without confusing provisions or footnotes.
2. A page uses OCR when embedded text is sparse, corrupt, or contains too little Sinhala Unicode.
   Legacy-font glyph output is not accepted as Sinhala text.
3. OCR text is never automatically `verified`, even when script and length checks pass.
4. Exact numbered lines are provision-heading candidates, not confirmed provisions. Contents
   pages, footnotes, and OCR errors require review.
5. Researcher decision on 2026-09-13: `Penal Code.pdf` is the canonical English consolidated base
   through 2006. `Penal-Code I.pdf` is retained as the source collection for later English
   amendment Acts. Both retain provenance; overlapping base text is not counted twice.

## Phase 4 annotation decisions

1. On 2026-09-24, the researcher instructed the pipeline to use the completed adjudication CSV.
   The decisions originated in an AI-assisted draft and were accepted for continued researcher-led
   experimentation. Provenance must remain recorded; the corpus may be described as
   researcher-accepted AI-assisted adjudication, not independent legal-expert adjudication.
2. Institutional rules determine how AI assistance must be disclosed in the thesis. The software
   will not remove provenance or make a false expert-review claim.
3. The adjudicated shared subset is still insufficient for five-fold bilingual evaluation because
   English and Sinhala class/group coverage remains incomplete.
