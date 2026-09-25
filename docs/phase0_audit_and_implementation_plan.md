# Phase 0 Audit and Implementation Plan

## Status and evidence basis

This audit was prepared from the supplied local files on 2026-09-11. PDF text was inspected with
Poppler `pdftotext` using UTF-8 output. Page counts below are PDF page counts inferred from page
boundaries in that extraction, not printed page labels. No source PDF was modified.

The two files `F:/Me/Research/IM_2021_118_Research report.pdf` and
`F:/Me/Research/IM-2021-118.pdf` have the same SHA-256 digest
(`77CE869F...C261A6C`) and are byte-identical copies. This audit calls that 36-page document the
**proposal**. The distinct 43-page
`F:/Me/Research/Interim/IM_2021_118-Interim.pdf` (`FAB348F0...17C03BB`) is called the
**interim report** and is authoritative when the two reports conflict.

## Confirmed research definition

### Aim

Develop and validate an NLP framework that makes the Sri Lankan Constitution and Penal Code
more accessible to ordinary citizens by extracting key information, simplifying legal language,
tracking amendments, and supporting English and Sinhala interaction. Outputs must be legal
information with traceable sources, not legal advice.

This wording follows the interim report, section 1.12. The phrase "natural language queries" does
not authorize development of a new question-answering model: interim sections 1.13 and 3.2.2
replace that earlier plan with an external evaluation of LawGPT.

### Objectives

1. Create a bilingual English/Sinhala annotated corpus of the Constitution and Penal Code.
2. Implement and evaluate Legal NER, treating English F1 >85% and Sinhala F1 >75% only as
   research targets.
3. Build amendment tracking for supplied Constitution and Penal Code materials.
4. Build a legal-text simplification module producing simple Sinhala while preserving meaning.
5. Evaluate LawGPT as an existing bilingual QA case study; do not build a duplicate QA model.
6. Integrate the three built components (NER, simplification, amendment tracking) into a prototype.

Objectives 1–5 reproduce the substance of interim section 1.13; objective 6 makes explicit the
integration described in interim section 3.7.

### Research questions

The interim report retains three research questions:

1. How effectively can NLP models extract legal entities (rights, offenses, and penalties) from
   the Constitution and Penal Code so that they support meaningful explanations for citizens?
2. How can legal language be simplified into simple Sinhala without losing legal precision?
3. How can amendment tracking show how the law has changed over time?

The questions do not independently ask whether LawGPT is accurate or usable even though this is
Objective 5. A fourth evaluation question is therefore recommended in the corrections document.

## Current methodology

The interim report adopts design-science research with iterative problem analysis, artifact
development, and empirical evaluation. The operational interpretation for implementation is:

1. Inventory and preserve authoritative source documents, checksums, provenance, and page-level
   extraction evidence.
2. Extract embedded text first; use Sinhala/English OCR only for pages whose embedded text is
   absent or demonstrably unusable.
3. Segment provisions and align English/Sinhala by legal structure, not page number.
4. Define guidelines and double-annotate a shared subset before model development.
5. Build rule/dictionary and CRF baselines, then mBERT, XLM-R, and English-only Legal-BERT.
6. Reserve one grouped final test set. Conduct grouped, stratified five-fold cross-validation only
   on development data if class counts and provision groups support it.
7. Use a transparent hybrid simplification baseline unless verified complex/simple Sinhala pairs
   become available.
8. Use deterministic amendment-reference parsing and versioned diffs before considering ML.
9. Integrate the three components and evaluate the prototype with users after ethics approval.
10. Evaluate LawGPT separately as an external benchmark with a documented query set and rubric.

This refines the report methodology where it is underspecified; it does not assert completed
experiments.

## Entity schema decision

The selected annotation schema remains exactly the five classes specified in both reports:

- `FUNDAMENTAL_RIGHT`
- `OFFENSE`
- `PENALTY`
- `CONSTITUTIONAL_BODY`
- `TEMPORAL_ENTITY`

`LEGAL_PROVISION` or `LEGAL_REFERENCE` is potentially essential because provisions such as
"Article 13(1)" and "section 53" are required for citation retrieval and amendment linking, but
these spans can also be captured deterministically as structural metadata rather than learned NER
entities. No new annotation class is approved or added in Phase 0. Before annotation starts, a
small document sample should compare the two options and obtain researcher/supervisor approval.

## Proposed evaluation framework

| Component | Primary measures | Required breakdown / safeguard |
|---|---|---|
| Extraction | usable-page rate, character/script checks, provision detection rate, warning rate | language, file, embedded text vs OCR; manual sample review |
| Alignment | exact provision-key match rate, coverage, duplicate/conflict rate, reviewed precision | language pair and document type |
| Annotation | span-level exact-match entity F1 plus per-class agreement | token Cohen's kappa only as secondary; report prevalence and shared-subset size |
| NER | exact-span entity precision, recall, micro/macro/per-class F1 | language, Constitution/Penal Code, fold mean/SD; untouched grouped test set |
| Simplification | verified preservation of entities, citations, negation, duties, exceptions and penalties; expert accuracy; citizen comprehension | sentence/lexical change; only validated Sinhala readability measures; omissions/hallucinations |
| Amendment tracking | reference P/R/F1, operation accuracy and macro-F1, link accuracy, reconstructed-text correctness, completeness, unresolved rate | manually verified gold records and operation type |
| LawGPT | legal accuracy, completeness, citation correctness, understandability | separate external benchmark; rater agreement; do not merge with NER metrics |
| Prototype | task success/time, usability/satisfaction, qualitative themes | user group; ethics approval and sample size |

Targets in the reports are hypotheses/acceptance goals, not results. Confidence intervals, sample
sizes, effect sizes, and statistical tests should be reported only when the data and assumptions
support them.

## Supplied legal-document inventory

| File | PDF pages | Embedded-text audit | Initial role |
|---|---:|---|---|
| `constitution.pdf` | 306 | 374,539 non-whitespace Latin-script characters | English consolidated Constitution, revised 2023, amended through 2022-10-31 |
| `constitution-si.pdf` | 289 | 233,670 characters; 211,367 in Sinhala Unicode block | Sinhala consolidated Constitution |
| `Penal Code.pdf` | 79 | 291,002 characters | English consolidated code listing amendments through Act 16/2006; edition authority/date must be verified |
| `Penal-Code I.pdf` | 199 | 325,376 characters | English consolidated code through 1998 plus five Acts from 2002–2021 |
| `දණ්ඩ නීති සංග්_රහය.pdf` | 140 | only 2,660 characters, mainly CamScanner marks | Sinhala Penal Code scan; OCR required |
| Seven `Amendment_PenalCode_Sinhala_*.pdf` files | 49 total | three have no embedded text; four expose non-Unicode/legacy-glyph text | Sinhala Penal Code amendment candidates; OCR/font recovery required |

`Penal-Code I.pdf` has a table of contents declaring: consolidated Penal Code pages 3–168;
Act 12/2002 pages 169–171; Act 16/2006 pages 172–185; Act 10/2018 pages 186–188;
Act 5/2021 pages 189–197; and Act 25/2021 pages 198–200. The PDF has 199 physical pages, so
printed page labels and PDF indices must be stored separately.

There are 12 supplied legal PDFs and approximately 1,062 physical PDF pages. This is not the same
as 12 independent legal instruments because two files are consolidated collections and may
overlap. No duplicate legal PDF hashes were found.

## Confirmed inconsistencies and gaps

1. **Languages:** the proposal sometimes says three languages/English-Sinhala-Tamil and even
   describes the corpus as English/Tamil. The interim scope consistently excludes Tamil and uses
   English/Sinhala. The latter governs.
2. **QA:** the proposal says to build a bilingual QA interface using DPR. The interim report says
   to build three components and evaluate LawGPT rather than duplicate QA. The latter governs.
3. **Entity list:** both methodologies name five entities, but objective text sometimes lists only
   four and omits `TEMPORAL_ENTITY`. The five-class list governs pending explicit approval.
4. **Cross-validation:** both reports say five-fold CV but do not define a held-out final test set,
   grouping, stratification, leakage control, or what happens with rare classes. The proposed
   methodology adds these necessary safeguards.
5. **Document/page claims:** the proposal claims about 300 Constitution pages, 450 Penal Code
   pages, and 66 amendment documents across three languages. The interim repeats these numbers
   across two languages. The supplied folder instead contains 12 PDFs/approximately 1,062 PDF
   pages, with overlap and scans. Neither report estimate is a verified corpus statistic.
6. **Constitutional amendments:** the two consolidated Constitution PDFs contain the law amended
   through the Twenty Second Amendment and amendment footnotes. They are not a supplied set of
   all 22 standalone amendment Acts. Chapters XII and XXIV are constitutional chapters, not by
   themselves evidence that all historical amendment instructions are available.
7. **Penal Code amendments:** the English collection exposes five standalone amendment Acts from
   printed pages 169–200. Seven Sinhala amendment PDFs are present (1980, 1998, 2002, 2006,
   2018, and two from 2021). Completeness of "all amendments" is unverified.
8. **Amendment relationship claim:** both reports suggest constitutional amendments affect related
   Penal Code provisions, but no supplied evidence establishes such relationships. They must not
   be inferred.
9. **Simplification data:** no verified aligned complex-legal/simple-Sinhala dataset was identified
   in the supplied folder. Supervised simplification is therefore not currently supported.
10. **Ground truth:** no annotations, adjudicated amendment records, expert-reviewed glossary,
    simplifications, user-study responses, ethics approval, or LawGPT evaluation set were supplied.
11. **Source authority:** some documents identify Parliament/Government Printing, while
    `Penal-Code I.pdf` identifies LankaLAW. Authority, edition, and completeness must be recorded
    per file and checked before claiming an official or current text.

## Feasibility risks and controls

| Risk | Consequence | Control |
|---|---|---|
| Sinhala scans and legacy encodings | corrupt corpus and labels | OCR page-by-page; Unicode/script validation; manual sampling |
| Missing standalone constitutional Acts | historical versions cannot be reconstructed reliably | acquire authoritative Acts or restrict tracking to evidenced footnotes/current consolidated text |
| Missing/unequal bilingual amendments | alignment and bilingual evaluation bias | report coverage; never manufacture translations |
| Small or imbalanced entity counts | unstable five-fold and macro-F1 | pilot annotation, grouped stratification, reduce folds if justified |
| Provision leakage | inflated model scores | split by provision/document group before sentence/token expansion |
| Ambiguous entity definitions | low agreement | pilot, adjudication, boundary examples, schema decision gate |
| No simplification pairs | supervised model infeasible | hybrid baseline and expert-reviewed glossary; separate translation from simplification |
| Legal validation availability | unsafe or unverifiable outputs | pending-review status and expert verification workflow |
| User evaluation logistics | objectives cannot be fully evaluated | ethics/consent plan and recruitment schedule before testing |
| Limited local environment | pipeline cannot run reproducibly | Phase 1 installs a pinned Python environment and records system/OCR versions |

## Staged implementation plan

1. **Phase 1 – Foundation:** create the repository structure, pinned environment, configurations,
   logging, schemas, tests, and source-ingestion policy. Keep raw PDFs external or copy them only
   after choosing a documented non-destructive policy.
2. **Phase 2 – Extraction:** generate a checksum manifest; embedded extraction first; OCR failed
   pages; preserve page/provision provenance; publish quality and manual-review queues.
3. **Phase 3 – Alignment:** match bilingual provisions by normalized legal identifiers and report
   unmatched/conflicting records.
4. **Phase 4 – Annotation:** resolve the legal-reference schema question, create guidelines and
   blank tasks, pilot double annotation, adjudicate, and calculate agreement.
5. **Phase 5 – Splits:** create grouped final test and development folds; run explicit leakage and
   class-support checks.
6. **Phase 6 – NER:** run rules and CRF first, then multilingual transformers and English-only
   Legal-BERT; choose models on development macro-F1 only.
7. **Phase 7 – Simplification:** implement and validate the hybrid baseline; train a sequence model
   only if verified pairs later exist.
8. **Phase 8 – Amendments:** parse references/operations deterministically, create reviewed gold
   records, reconstruct only evidenced versions, and expose unresolved cases.
9. **Phase 9 – Integration:** provide FastAPI and a small interface with provenance, confidence,
   verification state, and a prominent information-not-advice notice.
10. **Phase 10 – Analysis:** generate tables, figures, uncertainty estimates, errors, limitations,
    and thesis chapter drafts only from saved outputs.
11. **Phase 11 – QA:** test schemas and Unicode, detect leakage, re-hash raw sources, trace every
    metric, list unverified outputs, and produce a reproducibility report.

## Phase 0 completion checklist

- [x] Research proposal and interim report located, hashed, and inspected.
- [x] Interim report treated as the newer methodology.
- [x] Supplied legal directory recursively inventoried without modifying sources.
- [x] Aim, objectives, questions, methodology, entity schema, and metrics recorded.
- [x] Major contradictions, missing inputs, and feasibility risks recorded.
- [x] Staged implementation plan produced.
- [ ] Researcher/supervisor confirms whether legal-reference spans become NER labels or metadata.
- [ ] Authoritative source status and completeness of amendment material confirmed.
- [ ] Phase 1 begins only after the Phase 0 decisions are accepted.
