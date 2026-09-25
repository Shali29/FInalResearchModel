# Final Thesis Objective and Research-Question Traceability

## Scope decision

LawGPT evaluation is removed from the final research scope at the researcher's explicit request.
This supersedes Objective 5 in the interim report. The final thesis must not imply that this change
was supervisor-approved unless written approval is available. Record the approval date or describe
it transparently as a scope change in the methodology and limitations.

The final scope is English and Sinhala processing of the Sri Lankan Constitution and Penal Code.
Tamil, case law, legal advice, and a separate question-answering model are excluded.

## Final aim

To develop and evaluate a provenance-preserving NLP framework that improves access to the Sri
Lankan Constitution and Penal Code by extracting key legal information in English and Sinhala,
providing controlled plain-Sinhala explanations, tracking amendments, and presenting verified
source references through an integrated prototype.

## Final objectives and questions

| ID | Final objective | Research question | Required evidence | Current status |
|---|---|---|---|---|
| O1 | Develop a bilingual, provenance-preserving annotated corpus of Constitution and Penal Code provisions using the approved five-class entity schema. | RQ1: What corpus-construction, annotation, and quality-control process can produce a reliable bilingual legal NER dataset from the supplied English and Sinhala legal documents? | Source manifest, extraction audit, annotation counts, agreement, adjudication, class/language distribution | In progress; 80-task provisional corpus, 420 blank expansion tasks |
| O2 | Implement and compare rule-based, CRF, mBERT, XLM-R, and an English legal-domain NER model. | RQ2: How effectively do the selected models identify the five legal entity types across language and document type? | Grouped CV, untouched test evaluation, exact-span micro/macro/per-class F1, language/document breakdown, errors | Provisional validation only; final corpus and test results unavailable |
| O3 | Implement a controlled legal-text simplification module that produces plain-Sinhala explanations while preserving legally significant content. | RQ3: To what extent can complex provisions be explained in plain Sinhala without losing entities, citations, negation, duties, conditions, exceptions, or penalties? | Paired review set, preservation checks, expert ratings, comprehension study, omission/hallucination counts | Not evaluated |
| O4 | Implement deterministic amendment parsing, linking, versioning, and comparison for the collected amendment materials. | RQ4: How accurately can amendment instructions be classified, linked to affected provisions, and reconstructed chronologically? | Human-verified amendment gold set; reference F1, operation macro-F1, linking accuracy, reconstruction correctness, unresolved rate | Not evaluated |
| O5 | Integrate the components into a source-linked prototype and evaluate its functional correctness and usability. | RQ5: How successfully and efficiently can intended users complete representative legal-information tasks using the integrated prototype? | Functional tests, task success, completion time, satisfaction, comprehension, qualitative feedback | Not implemented/evaluated |

## Objective-to-chapter mapping

| Objective | Methodology section | Results section | Discussion section |
|---|---|---|---|
| O1 | Sources, extraction, annotation, agreement | Corpus and annotation results | Corpus quality and low-resource implications |
| O2 | Splitting, baselines, transformer training, metrics | NER comparison and error analysis | Model behavior, language effects, target comparison |
| O3 | Hybrid simplification safeguards and evaluation design | Readability, preservation, expert and citizen evaluation | Accessibility versus legal fidelity |
| O4 | Reference parsing, operation classification, versioning | Detection, linking, reconstruction and unresolved cases | Reliability and legal-data limitations |
| O5 | API/interface design and user-evaluation protocol | Functional and usability results | Practical usefulness, trust, deployment constraints |

Every objective must have corresponding methodology, results, discussion, and conclusion evidence.
If an evaluation remains incomplete at submission, state this explicitly; do not present an
implementation plan or target as an achieved contribution.
