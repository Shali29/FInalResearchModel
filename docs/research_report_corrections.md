# Recommended Research Report Corrections

These are proposed corrections only. The source PDFs have not been edited. The interim report is
treated as newer than the proposal.

## High-priority corrections

1. Replace all in-scope references to three-language or English/Tamil processing with
   **English and Sinhala only**. Preserve Tamil only when objectively describing an external
   dataset or multilingual publication.
2. Replace the proposal's Objective 5 and Phase 6 claim that a new bilingual QA/DPR system will be
   built. State that **LawGPT is an external evaluation benchmark/case study**, while the local
   prototype integrates NER, simplification, and amendment tracking.
3. Make the entity list identical everywhere:
   `FUNDAMENTAL_RIGHT`, `OFFENSE`, `PENALTY`, `CONSTITUTIONAL_BODY`, and
   `TEMPORAL_ENTITY`. Objectives currently abbreviate the list and omit the temporal class.
4. Correct the corpus deliverable described in the proposal as English and Tamil to **English and
   Sinhala**.
5. Replace the unverified estimates "300 pages", "450 pages", and "66 amendment documents" with
   measured corpus statistics after deduplication and document-level classification. Current
   supplied evidence is 12 legal PDFs and about 1,062 physical PDF pages, but consolidated files
   overlap and this must not be presented as 1,062 unique legal pages.
6. Replace "all amendments" with an evidence-bounded claim until completeness is verified. The
   consolidated Constitutions include changes through the Twenty Second Amendment but standalone
   constitutional amendment Acts were not supplied. English Penal Code amendment texts supplied
   separately within `Penal-Code I.pdf` cover five Acts from 2002–2021; seven Sinhala amendment
   PDFs cover a different set.
7. Remove or substantiate the statement that constitutional amendments affect "related Penal Code
   provisions." Do not imply a relationship without explicit documentary evidence.
8. Define five-fold cross-validation as grouped and stratified on development data only, with one
   untouched grouped final test set. Add a fallback when rare entity support makes five folds
   statistically indefensible.
9. Define NER F1 as exact-span entity F1 and specify micro, macro, per-class, per-language, and
   per-document-type results. Token metrics should be secondary.
10. Keep Cohen's kappa as a secondary token-level agreement measure and add exact-span/entity F1.
    Explain that heavy `O`-token prevalence and boundary disagreements can make token kappa
    misleading for NER.
11. Clarify the evaluation table formatting: the >30% readability and >80% comprehension targets
    belong to simplification, while the >90% target must name the exact amendment metric. Never
    call targets preliminary or achieved results before experiments occur.
12. Remove the interim abstract's unsupported wording "climate aware" and "citizen specific legal
    guidance." It is outside the stated variables and risks implying personalized legal advice.
13. Change "plain English explanation" in the interim abstract to match Objective 4: faithful
    translation where needed followed by a clearly separated **plain Sinhala explanation**.
14. Remove "Preliminary evaluations indicate..." unless traceable preliminary results, data,
    protocol, sample sizes, and approvals exist.
15. Update amendment tracking from unspecified "neural architectures" to a deterministic
    legal-reference/version-diff baseline. Add ML only if sufficient verified labels exist.

## Research-design additions

- Add a fourth research question: **How accurately, completely, understandably, and with what
  citation correctness does LawGPT answer a controlled bilingual set of in-scope questions?**
- Define the annotation unit, BIO/BIOES choice, tokenization, overlapping/nested policy, annotator
  qualifications, shared-subset proportion, and adjudication procedure.
- Add explicit extraction quality, bilingual alignment, OCR review, provenance, and Unicode
  validation procedures.
- Separate translation quality from simplification quality and prohibit unvalidated English
  readability formulae for Sinhala.
- Define amendment gold data, operation labels, effective-date handling, completeness, and
  unresolved-case reporting.
- State ethics approval/consent requirements before citizen, lawyer, law-student, or external
  platform evaluation begins.
- Replace any system wording that promises recommendations or legal guidance with legal
  information, plain-language explanation, provenance, and a disclaimer.

## Editorial/structural issues observed

- The proposal restarts chapter numbering at "4 Methodology" after section 6 and repeats section
  numbers 4.1–4.3.
- The interim table of contents omits 3.5.2 although the body includes Amendment Tracking.
- "Evaluation Mathod" should be "Evaluation Method" and the evaluation table columns/targets
  should be rebuilt because extraction has displaced target values.
- Fix typographical fragments such as "Sinhal", "Termology", duplicated bullets, and truncated
  sentences before final submission.
- Verify every citation and identifier before publication. The interim references explicitly label
  one 2026 Senaratna identifier as a placeholder; a placeholder must not remain in a final report.
