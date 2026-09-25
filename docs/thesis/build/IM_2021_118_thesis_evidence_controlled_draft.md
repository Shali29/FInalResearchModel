
> **DOCUMENT STATUS — EVIDENCE-CONTROLLED DRAFT (25 September 2026).**  
> This document is formatted as a thesis, but it is not yet submission-ready. Values marked
> **PENDING — NOT YET MEASURED** require completed human annotation or evaluation. The existing NER
> values are provisional validation results and are not final held-out-test performance. External
> QA benchmark evaluation has been removed from the final scope.


## DECLARATION

I hereby state that this research report and findings presented in it are my own and it has not been submitted before nor is it currently being submitted for any other academic programme. Where material has been used from other sources due recognition has been given by mentioning the source.

**Signature of the student**

Signature: _________________ Date: _________________

**Signature of Supervisor**

Supervisor's Signature: _________________ Date: _________________

---

## ABSTRACT

Sri Lankan constitutional and criminal-law documents are publicly available, but specialised
terminology, long sentence structures, bilingual presentation, scanned sources, and amendment
history can impede effective access. This research develops a provenance-preserving NLP framework
for analysing the Constitution of Sri Lanka and the Penal Code in English and Sinhala. The planned
framework comprises a bilingual annotated corpus, legal named-entity recognition (NER), controlled
plain-Sinhala explanation, deterministic amendment tracking, and a source-linked prototype. The
approved entity schema contains `FUNDAMENTAL_RIGHT`, `OFFENSE`, `PENALTY`,
`CONSTITUTIONAL_BODY`, and `TEMPORAL_ENTITY`.

Twelve supplied legal PDFs comprising 1,062 physical pages were processed. Embedded text was usable
on 867 pages, OCR output was usable on 188 pages, and seven pages were rejected. Extraction yielded
2,328 candidate provisions, subsequently segmented into 8,378 blank annotation tasks. A pilot
corpus currently contains 80 annotated tasks and 297 entity spans. On a 50-task independently
annotated subset, token-level Cohen's kappa was 0.6466 and exact-span agreement F1 was 0.5304,
below the planned kappa threshold above 0.80.

Provisional validation experiments produced exact-span micro/macro F1 of 0.0758/0.0833 for a
training-derived dictionary and 0.1224/0.0808 for a CRF. The tested mBERT and XLM-R configurations
obtained exact-span validation F1 of 0.0. Diagnostic outputs showed both majority-class collapse
and unstable false-positive behaviour. These results do not support the proposed English and
Sinhala performance targets. Consequently, 420 additional blank tasks were selected for human
annotation, including 84 tasks for independent double annotation. Final held-out NER evaluation,
simplification evaluation, amendment evaluation, prototype testing, and user evaluation remain
pending. The present evidence demonstrates a reproducible corpus-engineering and evaluation
framework while showing that substantially more high-quality annotated data is required before a
reliable legal NER model or citizen-facing system can be claimed.

**Keywords:** legal NLP, named-entity recognition, Sinhala, bilingual corpus, statutory text,
amendment tracking, text simplification, Sri Lanka

## ACKNOWLEDGEMENTS

I sincerely thank everyone who supported me throughout this research. My deepest gratitude goes to my supervisor, Mr. Dinesh Asanka, for his continuous guidance, encouragement, and technical supervision, which were vital to the successful completion of this study. I also extend my appreciation to Dr. Keerthi Wijayasiriwardhane for his coordination and invaluable support. I am thankful to the academic and non-academic staff of the Department of Industrial Management for their assistance. I further wish to express my genuine gratitude to all those who have contributed, regardless of the scale of their involvement, in transforming this research into a reality. Finally, I am deeply grateful to my friends and parents for their encouragement, understanding, and constant motivation, which inspired me to complete this journey successfully.

---

## TABLE OF CONTENTS

[TOC]

---

## LIST OF TABLES

| Table | Title | Page |
|-------|-------|------|
| Table 1 | Research objectives and outputs | 3 |
| Table 2 | Summary of the research gap | 10 |
| Table 3 | Approved entity annotation schema | 14 |
| Table 4 | Research phases and current evidence | 18 |
| Table 5 | Survey respondent profile | 19 |
| Table 6 | Citizen knowledge confidence and cost concerns | 20 |
| Table 7 | Expected usefulness of system features | 22 |
| Table 8 | Corpus engineering outputs | 25 |
| Table 9 | NER model comparison | 25 |
| Table 10 | Text simplification evaluation | 26 |
| Table 11 | Amendment tracking evaluation | 26 |
| Table 12 | Integrated prototype evaluation | 27 |
| Table 13 | Threats to validity and controls | 31 |

---

## LIST OF FIGURES

| Figure | Title | Page |
|--------|-------|------|
| Figure 1 | Proposed system architecture | 11 |
| Figure 2 | Survey respondents by role | 19 |
| Figure 3 | Reported legal information difficulties | 21 |
| Figure 4 | Expected usefulness of system features | 22 |
| Figure 5 | Evidence required before reliance | 24 |

---

## LIST OF ABBREVIATIONS

| Abbreviation | Meaning |
|--------------|---------|
| API | Application Programming Interface |
| BIO | Beginning Inside Outside tagging scheme |
| CRF | Conditional Random Field |
| DDR | Design and Development Research |
| IAA | Inter-annotator agreement |
| NER | Named Entity Recognition |
| NLP | Natural Language Processing |
| OCR | Optical Character Recognition |
| XLM-R | XLM-RoBERTa |

---

## CHAPTER 1: INTRODUCTION

### 1.1 Background

The Constitution of Sri Lanka defines the structure of government, the powers of public institutions, and the fundamental rights of citizens. The Penal Code defines criminal offences and punishments. Although these texts are central to civic and professional life, direct access to a PDF does not guarantee meaningful access to the law. Readers must locate the correct provision, interpret specialised language, determine whether the text has been amended, and often move between English and Sinhala versions.

Natural language processing offers methods for recognising legally significant phrases, structuring provisions, simplifying difficult language, and representing changes between statutory versions. Legal NLP models, however, depend on domain-specific data. English models cannot be assumed to perform reliably on Sinhala legal text, and a model trained on case law may not transfer directly to constitutional provisions or criminal statutes. This research therefore begins with corpus construction and human annotation before model training.

### 1.2 Research Problem

Sri Lankan citizens, students, and legal practitioners face three connected problems. First, important concepts such as fundamental rights, offences, penalties, constitutional bodies, and legal time expressions are embedded in lengthy provisions. Second, legal wording is difficult for non-specialists to understand, particularly when a reader prefers Sinhala. Third, consolidated statutes and separate amendment instruments make it difficult to establish how a provision changed and which wording is current.

Existing search and question-answering tools do not by themselves solve these problems. Search results may retrieve a provision without identifying its key entities, explaining the wording, or showing its amendment history. The research problem is therefore the absence of an evaluated bilingual framework that joins key-information extraction, plain-language explanation, and amendment tracking for the Sri Lankan Constitution and Penal Code.

### 1.3 Research Aim

The aim is to develop and evaluate an NLP-based framework that improves access to the Sri Lankan Constitution and Penal Code by extracting key legal information in English and Sinhala, producing legally controlled plain-Sinhala explanations, and tracing amendments to affected provisions.

### 1.4 Research Objectives

**Table 1: Research objectives and outputs**

| Objective | Research Output |
|-----------|-----------------|
| Develop a bilingual annotated corpus | Structured English and Sinhala provisions with human-verified entity spans and provenance |
| Implement and evaluate legal NER | Comparative results for rule-based, CRF, multilingual transformer, and English legal-domain models |
| Develop amendment tracking | Versioned links between amendment instructions and affected provisions with side-by-side changes |
| Implement text simplification | Plain Sinhala explanations that preserve legal meaning, citations, exceptions, and penalties |
| Evaluate usefulness and usability | Survey findings, expert review, comprehension testing, and prototype usability evidence |

### 1.5 Research Questions

1. How effectively can NLP models identify fundamental rights, offences, penalties, constitutional bodies, and temporal entities in English and Sinhala constitutional and criminal-law text?

2. How can complex legal wording be explained in plain Sinhala while retaining the meaning of rights, duties, prohibitions, exceptions, conditions, penalties, and citations?

3. How accurately can amendment instructions be linked to affected provisions and represented as a chronological version history?

4. How do citizens, law students, and lawyers assess their current access difficulties and the expected usefulness of the proposed system features?

### 1.6 Scope

The study covers the Constitution of Sri Lanka, consolidated through the Twenty Second Amendment in the collected source, and the Penal Code with the amendment documents available to the researcher. The primary languages are English and Sinhala. Tamil language support is excluded due to scope constraints. The system provides legal information, not legal advice.

### 1.7 Contribution

The principal contribution is a reproducible workflow for a low-resource bilingual legal domain. The work combines source provenance, OCR review, provision segmentation, annotation, leakage-controlled model evaluation, plain-language safeguards, and amendment versioning. The survey adds user evidence that informs feature priorities and trust requirements. The outputs can support later Sri Lankan legal NLP research without presenting automatically generated explanations as authoritative law.

### 1.8 Thesis Structure

Chapter 2 reviews legal NLP, multilingual NER, simplification, amendment extraction, and Sri Lankan research. Chapter 3 presents the research design, data, annotation process, models, and evaluation measures. Chapter 4 documents implementation and available results, including the survey analysis and fields for unfinished experiments. Chapter 5 interprets the findings and limitations. Chapter 6 concludes the research and identifies the work required for final validation and future extension.

---

## CHAPTER 2: LITERATURE REVIEW

### 2.1 Legal Information Access in Sri Lanka

Legal accessibility has linguistic, technical, and interpretive dimensions. A document may be publicly downloadable yet remain inaccessible when it is scanned, inconsistently encoded, difficult to search, or written in specialised language. For bilingual statutory analysis, accessibility also depends on whether parallel provisions can be located reliably and whether discrepancies introduced through OCR or version differences are visible to the user.

Sri Lankan legal NLP research has demonstrated the feasibility of information retrieval, entity extraction, and legal question answering. Prior work has focused mainly on court decisions, constitutional search, or broad document collections. The present research differs by concentrating on the Constitution and Penal Code as linked sources of rights, state institutions, offences, penalties, and amendment histories.

### 2.2 Legal Named Entity Recognition

Named entity recognition converts unstructured text into spans assigned to predefined categories. Traditional CRF models use lexical, orthographic, and contextual features. Neural sequence models learn representations from data, while transformer models use contextual pre-training and subword tokenisation. Surveys of legal NER report that domain-specific and transformer-based models generally outperform general baselines when sufficient annotated data is available (Leitner et al., 2021; Premasiri et al., 2025).

LEGAL-BERT demonstrates the value of legal-domain pre-training for English tasks (Chalkidis et al., 2020). It is not a bilingual Sinhala model. Multilingual BERT and XLM-RoBERTa are therefore more appropriate candidates for cross-language experiments, while English Legal-BERT provides an English-only comparator. Performance must be reported separately by language and document type because an overall micro-F1 score can conceal weak performance on Sinhala or rare entity classes.

### 2.3 Low Resource and Bilingual NLP

Sinhala legal text presents low-resource challenges, including limited annotated corpora, OCR errors, script-specific tokenisation, and variation between formal legal usage and ordinary language. The development of a bilingual annotated corpus is therefore a foundational contribution of this research, not merely a preparatory step.

### 2.4 Legal Text Simplification

Text simplification seeks to reduce lexical and syntactic difficulty while preserving meaning. In law, a fluent explanation can still be unsafe if it omits a condition, changes a prohibition, weakens an obligation, or removes an exception. Alva-Manchego et al. (2020) distinguish simplification from summarisation and translation. Dale (2021) emphasises the difficulty of simplifying legal text without losing precision. The present framework therefore separates faithful translation from simplification and retains the source provision beside every explanation.

### 2.5 Amendment Extraction and Consolidation

Amendment instruments express operations such as insertion, deletion, substitution, repeal, and renumbering. Smywinski-Pohl et al. (2021) show that amendment information can be extracted from statutory text. Automatic consolidation remains risky because a reference may be ambiguous, an amendment may depend on another instrument, and OCR errors can change section numbers or years. The proposed system uses deterministic reference parsing and versioned comparison as the first baseline. Ambiguous cases require manual review.

### 2.6 Research Gap

**Table 2: Summary of the research gap**

| Area | Established Work | Gap Addressed by This Research |
|------|------------------|-------------------------------|
| Legal NER | Entity extraction from legal and court documents | Bilingual entity extraction for Sri Lankan constitutional and Penal Code provisions |
| Sinhala NLP | Growing multilingual resources and general Sinhala processing | Human-annotated statutory entities with explicit provenance and OCR review |
| Simplification | General and legal-domain simplification methods | Plain Sinhala explanation with legal preservation checks and source text display |
| Amendments | Extraction and consolidation methods in other jurisdictions | Version tracking for collected Sri Lankan constitutional and Penal Code materials |
| Evaluation | Model-level accuracy and retrieval | Combined technical, expert, citizen, and usability evaluation |

### 2.7 Conceptual Framework

The conceptual framework links document type, language, annotation quality, and model choice to extraction performance. Extracted entities support the simplification and amendment components by identifying the legal concepts that must be preserved. User type and task shape perceived usefulness, comprehension, and trust. The framework therefore treats model accuracy as necessary but insufficient: the system must also preserve source references and communicate uncertainty.

---

## CHAPTER 3: RESEARCH METHODOLOGY

### 3.1 Research Design

The study uses a design-science and development-research approach. The artefacts are the bilingual corpus, NER models, simplification module, amendment tracker, and integrated prototype. Development proceeds iteratively through problem definition, source audit, data preparation, annotation, modelling, evaluation, and refinement. Quantitative measures assess model performance and survey responses. Qualitative review assesses legal accuracy, annotation disagreements, simplification errors, and user feedback.

**Figure 1: Proposed system architecture**

```
[Authoritative PDFs English and Sinhala] → [Extraction and provision structuring] → [Bilingual corpus and manual annotation] → [Legal NER training and evaluation]
                                                                                              ↓
                                                                         [Text simplification with legal safeguards]
                                                                                              ↓
                                                                         [Amendment tracking and version comparison]
                                                                                              ↓
                                                                         [Integrated citizen-facing legal document analysis framework]
```

### 3.2 Data Sources and Provenance

The source audit identified 12 legal PDFs containing English and Sinhala Constitution and Penal Code materials, including overlapping consolidated documents and collected amendment Acts. The collection contained approximately 1,062 physical PDF pages. The Constitution sources included consolidated wording through the Twenty Second Amendment, but the collection did not contain all 22 amendments as separate Acts. The English Penal Code amendment material included five Acts in the collected volume, while seven separate Sinhala Penal Code amendment PDFs were identified.

### 3.3 Extraction and Quality Control

Embedded text is extracted where available. OCR is applied when the source is scanned or the embedded text is unusable. Sinhala OCR receives special review because digit substitutions and legacy-font problems can change legal meaning. Confirmed examples during development included section identifiers misread as different numbers and the year 2002 being rendered incorrectly. Review therefore prioritises Act numbers, years, provision numbers, subsection markers, dates, monetary amounts, imprisonment periods, negation, conditions, and quotation boundaries.

### 3.4 Bilingual Alignment

English and Sinhala provisions are aligned primarily by document type, provision type, provision number, and subsection structure. Page numbers are not used as evidence of correspondence. The automated baseline produced 160 provisional pairs, comprising five Constitution pairs and 155 Penal Code pairs. It also recorded 468 unmatched structural references and 206 duplicated or ambiguous references. Because manual review was deferred, these pairs remain provisional and are not used as verified bilingual accuracy evidence.

### 3.5 Annotation Schema

**Table 3: Approved five-class entity annotation schema**

| Entity | Operational Definition | Illustrative Expression |
|--------|------------------------|------------------------|
| FUNDAMENTAL_RIGHT | A right expressly declared or recognised as a fundamental right in the selected constitutional context | freedom of speech and expression |
| OFFENSE | A named criminal offence or conduct explicitly designated as an offence | murder |
| PENALTY | The complete punishment expression, including imprisonment, fine, or another legal consequence | fine not exceeding one hundred thousand rupees |
| CONSTITUTIONAL_BODY | A formally named body or institution created or recognised by the Constitution | Public Service Commission |
| TEMPORAL_ENTITY | A date, deadline, duration, or legally significant time expression not absorbed into a penalty span | within fourteen days |

Article and Section references remain structural metadata rather than a sixth entity class. Overlapping entities are not allowed in the approved schema. Tasks with no target entity are retained as negative examples. Two annotators independently label a shared subset. Disagreements are adjudicated before the gold corpus is produced.

### 3.6 Corpus Preparation and Agreement

The software generated 8,378 blank tasks in the complete candidate pool and a balanced 500-task pilot. An initial annotation export contained 145 completed tasks, but only one entity was marked, showing that the random sample was too sparse for training. The process was corrected by producing an entity-enriched pilot without automatically generating labels. A later expansion batch contained 420 independent parent provisions, including 220 English and 200 Sinhala tasks, with 84 reserved for independent double annotation. This correction is methodologically important because it improves entity coverage without converting keyword cues into gold labels.

Inter-annotator agreement is calculated on the shared subset using exact-span entity F1 and token-level Cohen kappa. Kappa is retained because it appears in the approved methodology, but exact-span agreement is more directly relevant to NER. All disputed items must receive a documented adjudication decision before gold-corpus creation.

### 3.7 Data Splitting

The gold corpus is divided using grouped splitting at the parent-provision level. Sentences from the same Article or Section cannot appear across training, validation, and test sets. An untouched test set is reserved for final reporting. Five-fold cross-validation is performed on the development portion only if each fold contains defensible representation of the rare classes. Otherwise, the number of folds is reduced and the reason is reported.

### 3.8 NER Models

The NER experiments compare a dictionary or rule baseline, a CRF baseline, multilingual BERT, XLM-RoBERTa base, and an English Legal-BERT checkpoint on English data. Token labels are aligned to subwords, padding tokens are masked, random seeds are fixed, and the best checkpoint is selected using validation macro-F1. The held-out test set is evaluated once after model selection.

Primary metrics are exact-match entity-level precision, recall, and F1. Results are also reported by class, language, and document type. Micro-F1 measures performance across all spans, while macro-F1 gives equal weight to each entity class.

### 3.9 Text Simplification

The simplification component uses a controlled hybrid baseline unless a verified parallel corpus of complex legal text and plain Sinhala explanations becomes available. The workflow preserves the original provision, produces or verifies a faithful Sinhala translation, applies glossary and structural simplification rules, and checks entities, citations, negation, conditions, duties, prohibitions, exceptions, and penalties. A legal reviewer rates accuracy, and citizen participants answer comprehension questions based on the original and simplified versions.

### 3.10 Amendment Tracking

The amendment module extracts affected provision references and operation types. Each event stores the amendment identifier, effective date where available, source file, affected provision, original text, instruction, updated text, and verification status. Operations are applied chronologically to produce a version history. The evaluation uses a manually verified set of amendment instructions and reports reference-detection F1, operation-classification macro-F1, linking accuracy, reconstructed-text correctness, completeness, and unresolved-case rate.

### 3.11 Survey and User Needs Assessment

The cross-sectional survey collected 31 valid adult responses. Routing presented a common section followed by role-specific questions for citizens, law students, and lawyers. Feature-usefulness, likelihood, and scenario-value items used ordered response scales. Multiple-response questions were analysed as counts and percentages of respondents, so their percentages can total more than 100 percent. The analysis is descriptive because convenience sampling and small subgroup sizes, particularly the lawyer group, do not support population-level inference.

### 3.12 Ethics

All legal documents are public sources. Original text is attributed and preserved. Survey participation was voluntary, and every included respondent confirmed consent and an age of at least 18 years. The system must display a legal-information disclaimer, link generated outputs to source provisions, identify unverified content, and avoid claims that it replaces a lawyer or gives legal advice.

---

## CHAPTER 4: SYSTEM DEVELOPMENT AND RESULTS

### 4.1 Implementation Status

**Table 4: Research phases and current evidence**

| Phase | Output or Evidence | Status at This Preparation |
|-------|-------------------|---------------------------|
| 0 Source audit | Scope, inconsistencies, assumptions, source inventory | Completed |
| 1 Project setup | Python 3.11 environment, modular package, tests, configurations | Completed |
| 2 Extraction | Structured records, OCR, quality ledger, provenance | Automated extraction completed; verified corrections must remain traceable |
| 3 Alignment | 160 provisional pairs and issue reports | Implementation completed; gold review deferred |
| 4 Annotation | Guidelines, Label Studio tasks, agreement and adjudication code | Implemented; manual gold-corpus completion is required |
| 5 Splitting | Grouped leakage-controlled train/validation/test procedure | To be finalised from adjudicated gold corpus |
| 6 NER modelling | Baselines and transformer comparison | In progress |
| 7–9 | Simplification, amendment tracking, and integration | Planned and specified; final outputs pending |

The implementation follows a modular Python package structure with separate components for data extraction, annotation, NER, simplification, amendment handling, evaluation, and the application layer. Configuration files record data paths and experiment settings. Automated tests are used to protect record schemas, Unicode handling, task identifiers, and annotation conversion.

### 4.2 User Needs and Usability Evidence

**PENDING — NOT YET VERIFIED.** The working manuscript contained numerical claims for a
31-participant survey, but the anonymised raw questionnaire export and analysis script were not
available in the research repository when this draft was generated. Those claims are therefore
excluded. If the study was conducted with appropriate consent, the raw anonymised data must be
supplied, quality checked, and recalculated before respondent profiles, percentages, charts, or
conclusions are inserted.

Required reporting will include recruitment and consent procedures, exact subgroup sizes, missing
data rules, descriptive distributions, task definitions, and the limitations of convenience
sampling. No inferential population claim will be made from a small non-probability sample.

### 4.7 Corpus Engineering Results

**Table 8: Corpus engineering outputs**

| Measure | Observed Result | Interpretation |
|---------|----------------|----------------|
| Legal source PDFs | 12 | Includes overlapping consolidated documents and amendment materials |
| Approximate physical pages | 1,062 | Page count is not equal to unique legal content |
| Complete blank candidate tasks | 8,378 | Candidate pool, not an annotated corpus |
| Provisional bilingual pairs | 160 | Manual verification deferred; not bilingual gold data |
| Unmatched structural references | 468 | Require parser improvement or manual resolution |
| Duplicated or ambiguous references | 206 | Excluded from automatic gold alignment |
| Expansion annotation tasks | 420 | 220 English and 200 Sinhala independent provisions |
| Shared expansion tasks | 84 | Reserved for independent double annotation |

### 4.8 NER Experimental Results

The following values are observed **provisional validation results**, not five-fold or final
held-out-test results. The training set contained 56 tasks, validation contained 12 tasks, and the
untouched test set contained 12 tasks. No parent-record overlap was detected among these sets.

| Model | Exact-span micro-F1 | Exact-span macro-F1 | Interpretation |
|---|---:|---:|---|
| Training-derived dictionary | 0.0758 | 0.0833 | Highest provisional macro-F1 |
| CRF | 0.1224 | 0.0808 | Highest provisional micro-F1 |
| mBERT, unweighted | 0.0000 | 0.0000 | No entity spans predicted |
| mBERT, strong inverse-frequency weighting | 0.0000 | 0.0000 | 441 false-positive spans; 37 false negatives |
| XLM-R, moderate square-root weighting | 0.0000 | 0.0000 | 4 false-positive `OFFENSE` spans; 37 false negatives |

For exact entity spans,

\[
P=rac{TP}{TP+FP},\qquad
R=rac{TP}{TP+FN},\qquad
F_1=rac{2TP}{2TP+FP+FN}.
\]

The dictionary result gives the highest macro-F1, while the CRF gives the highest micro-F1. Both
scores are too low to support deployment. Transformer training loss decreased, but no predicted
span exactly matched a validation entity. Strong weighting overcorrected majority-class collapse
and generated excessive `PENALTY` false positives. These findings indicate insufficient and
unstable supervision in the provisional corpus rather than achievement of the planned targets.

The English F1 > 85% and Sinhala F1 > 75% targets were **not achieved**. Further tuning on the same
12 validation tasks was stopped to limit validation overfitting. Final model comparison, per-class
confidence intervals, five-fold mean/standard deviation, English-only Legal-BERT, and final test
evaluation remain **PENDING — NOT YET MEASURED** until the expanded annotations are independently
reviewed and adjudicated.

### 4.9 Text Simplification Results

**Table 10: Text simplification evaluation**

| Evaluation Dimension | Measure | Final Result |
|---------------------|---------|--------------|
| Readability | Validated Sinhala readability or controlled proxy | [VALUE AND METHOD] |
| Comprehension | Correct answers before and after simplification | [VALUE] |
| Legal accuracy | Mean expert rating and agreement | [VALUE] |
| Entity preservation | Entities retained exactly | [VALUE] |
| Citation preservation | Article and Section references retained | [VALUE] |
| Meaning failures | Negation, condition, exception, duty, penalty, hallucination | [COUNTS BY TYPE] |

### 4.10 Amendment Tracking Results

**Table 11: Amendment tracking evaluation**

| Metric | Definition | Final Result |
|--------|-----------|--------------|
| Reference detection F1 | Exact identification of affected provisions | [VALUE] |
| Operation macro F1 | Insertion, deletion, substitution, repeal, and renumbering | [VALUE] |
| Linking accuracy | Correct amendment-to-provision link | [VALUE] |
| Reconstruction correctness | Verified current wording after chronological application | [VALUE] |
| Completeness | Gold amendment events recovered | [VALUE] |
| Unresolved-case rate | Ambiguous events sent for review | [VALUE] |

### 4.11 Integrated Prototype and User Evaluation

The final prototype evaluation should use representative tasks such as locating arrest-related rights, identifying the penalty for a selected offence, comparing original and simplified wording, and viewing the history of an amended provision. Record task success, completion time, satisfaction, comprehension, and observed errors. Compare participant types descriptively unless the final sample supports inferential analysis.

**Table 12: Integrated prototype evaluation fields**

| Measure | Citizens | Law Students | Lawyers | Overall |
|---------|----------|--------------|---------|---------|
| Task success rate | [VALUE] | [VALUE] | [VALUE] | [VALUE] |
| Median completion time | [VALUE] | [VALUE] | [VALUE] | [VALUE] |
| Mean satisfaction | [VALUE] | [VALUE] | [VALUE] | [VALUE] |
| Mean comprehension | [VALUE] | [VALUE] | [VALUE] | [VALUE] |

---

## CHAPTER 5: DISCUSSION

### 5.1 Interpretation of the User Needs Findings

The survey indicates that legal access problems are not confined to document availability. Respondents reported difficulty with vocabulary, sentence structure, provision retrieval, and amendments. A majority preferred either bilingual access or Sinhala, and 71.0 percent were likely or very likely to try the proposed system. The results therefore support an interface that joins extraction, explanation, and version information rather than presenting these features as unrelated tools.

The citizen results show a practical confidence gap. Sixteen of 21 citizens were not at all or only slightly confident about what to do after a possible fundamental-rights violation. This does not mean that an automated system should recommend legal action. It means that the system should help users locate relevant provisions, understand introductory information, and prepare questions for a qualified service or lawyer.

### 5.2 Implications for Legal NER

The five entity classes reflect the most important concepts identified in the research objectives and survey. Highlighting rights and named offences received strong support. Temporal entities are also important because users prioritised dates and deadlines, while penalties require complete span boundaries. The annotation experience showed that random sampling produced too many empty passages. Entity-enriched sampling was therefore necessary, but keyword cues were used only for selection. Human annotators remained responsible for the labels, preventing circular evaluation.

Final performance should be interpreted using both micro and macro metrics. A model may achieve a high micro-F1 by performing well on frequent entities while failing on rare fundamental rights or constitutional bodies. Language-specific reporting is equally important. A combined bilingual score cannot establish acceptable Sinhala performance.

### 5.3 Implications for Simplification

The high usefulness rating for simpler explanations is consistent with respondents' difficulty understanding legal terminology and complex sentences. Trust responses show, however, that explanation alone is insufficient. Users want the original legal wording, exact references, official sources, review evidence, and accuracy results. The prototype should therefore show simplification as an explanatory layer attached to the source provision, not as a replacement for it.

### 5.4 Implications for Amendment Tracking

Fourteen respondents reported difficulty identifying amendments or updated provisions. The student responses also show inconsistent amendment checking. Amendment tracking can reduce the effort required to find changes, but automatic consolidation creates a higher legal risk than ordinary text highlighting. The system should expose the amending instruction, affected provision, operation type, source document, and verification status. Ambiguous operations should remain unresolved rather than being silently applied.

### 5.5 Methodological Strengths

- Source provenance connects every processed record to its legal PDF and page where recoverable.
- OCR output is separated from reviewed text, preventing corrections from destroying extraction evidence.
- The corpus uses human annotation and adjudication rather than automatically generated gold labels.
- Provision-level grouping reduces train and test leakage.
- Evaluation separates languages, document types, entity classes, and development versus final test results.
- The survey links system features to observed user needs and trust requirements.

### 5.6 Limitations

The source collection does not contain every constitutional amendment as a separate bilingual instrument. Some Sinhala documents require OCR and manual verification. The bilingual alignment baseline remains provisionally reviewed. The survey uses a small convenience sample, including only three lawyers, so subgroup percentages should not be generalised to all Sri Lankan legal professionals. Self-reported likelihood to use a system does not measure actual use.

Model results, simplification scores, amendment metrics, and usability results remain incomplete until the corresponding phases produce verified outputs. The final thesis must replace every bracketed field with traceable results or state that the evaluation was not completed. Target values in the methodology must never be described as achieved performance.

### 5.7 Threats to Validity

**Table 13: Threats to validity and controls**

| Threat | Possible Effect | Control |
|--------|----------------|---------|
| OCR errors | Incorrect entities, references, dates, or penalties | Page-level provenance, manual review, and exclusion of unverified records |
| Annotation ambiguity | Inconsistent boundaries or classes | Guidelines, shared subset, agreement measures, and adjudication |
| Sampling bias in corpus | Inflated performance on cue-rich passages | Retain negative examples and test on untouched provision groups |
| Train-test leakage | Overstated model accuracy | Group by parent provision and deduplicate before splitting |
| Survey convenience sampling | Limited population generalisability | Report descriptive findings and exact subgroup sizes |
| Expert-review subjectivity | Variable simplification ratings | Rubric, multiple reviewers, and agreement reporting |
| Incomplete amendment collection | Incomplete legal history | State collection boundaries and avoid unsupported consolidation claims |

---

## CHAPTER 6: CONCLUSION AND FUTURE WORK

### 6.1 Conclusion

This research defines and implements a staged framework for bilingual analysis of the Sri Lankan Constitution and Penal Code. The completed work establishes source provenance, extraction, OCR quality controls, provisional provision alignment, annotation guidelines, corpus preparation, and the experimental design for legal NER. The needs assessment shows that users encounter difficulties with terminology, long sentences, provision retrieval, source reliability, and amendment identification. Respondents also expressed strong interest in simpler explanations, entity highlighting, bilingual access, and source-linked information.

The contribution is therefore both technical and user-centred. The framework treats accuracy, traceability, and legal meaning as connected requirements. A useful legal NLP system must identify key information, retain the original provision, disclose its document version, and mark uncertain outputs. The final contribution will be established after the NER, simplification, amendment, and prototype evaluations are completed using the methods specified in this thesis.

### 6.2 Recommendations for Completing the Research

1. Finish adjudication and export one immutable gold corpus with version and checksum.
2. Generate leakage-controlled grouped splits and publish the split manifest.
3. Run every NER experiment using the same splits and record seeds, package versions, and checkpoints.
4. Evaluate the held-out test set only after model selection and retain raw predictions for audit.
5. Create a legal-review rubric and verified examples for simplification before citizen comprehension testing.
6. Construct a manually verified amendment gold set covering each operation type and both languages where sources permit.
7. Complete the integrated usability study and report subgroup sizes with descriptive statistics.
8. Replace every bracketed field in Chapters 4 to 6 and reconcile all tables, figures, abstract values, and conclusions.

### 6.3 Future Work

Future work may extend the corpus to Tamil, additional statutes, regulations, and selected case law. A larger expert-reviewed simplification corpus could support controlled sequence-to-sequence modelling. Active learning could reduce annotation effort by selecting uncertain and diverse provisions. Amendment graphs could represent dependencies among statutes and provisions. Any public deployment should include scheduled source updates, legal review, model monitoring, versioned outputs, and a clear process for correcting errors.

---

## REFERENCES

1. Alva-Manchego, F., Scarton, C., and Specia, L. (2020). A survey of automatic text simplification. *ACM Computing Surveys*, 53(2), 1–36.

2. Bandara, M., et al. (2022). Legal party extraction from legal opinion texts using recurrent deep neural networks. *Journal of Data Intelligence*, 3(4), 421–441.

3. Cardellino, C., Teruel, M., and Alvez, P. (2017). Legal named entity recognition for the Spanish language. *Proceedings of JURIX 2017*, 173–178.

4. Chalkidis, I., Fergadiotis, M., Malakasiotis, P., Aletras, N., and Androutsopoulos, I. (2020). LEGAL-BERT: The Muppets straight out of law school. *Findings of EMNLP 2020*, 2898–2904.

5. Dale, R. (2021). Text simplification in the legal domain. *Natural Language Engineering*, 27(3), 361–374.

6. Deusser, T., et al. (2024). A comparative study of large language models for named entity recognition in the legal domain. *IEEE International Conference on Big Data*, 4737–4742.

7. Dissanayaka, D., et al. (2024). An integrated approach to enhance legal information retrieval of Sri Lankan Supreme Court verdicts. *IEEE conference proceedings*.

8. Fernando, W. S., Handapangoda, M., Samindi, N., Gamage, M., and Alwis, D. (2024). LawKey Law Constitution Chatbot. *8th SLAAI International Conference on Artificial Intelligence*, 1–6.

9. Jayasooriya, S., et al. (2023). Automated information extraction from Supreme Court verdicts. *IEEE conference proceedings*, 1–8.

10. Kothelawala, I. (2019). *Incorporating plain legal language in mortgage bonds*. University of Kelaniya Repository.

11. Kumar, A., et al. (2022). On the effectiveness of pre-trained language models for legal natural language processing: An empirical study. *IEEE ICMLA*, 456–463.

12. Leitner, E., Rehm, G., and Moreno-Schneider, J. (2021). A survey of named entity recognition in legal documents. *JURIX*, 89–98.

13. Premasiri, D., Ranasinghe, T., Mitkov, R., El-Haj, M., and Frommholz, I. (2025). Survey on legal information extraction: Current status and open challenges. *Knowledge and Information Systems*, 67, 11287–11358.

14. Radhika, A., et al. (2024). Optimization of natural language processing models for multilingual legal document analysis. *INCOS 2024*, 1–6.

15. Senaratna, N. I. (2025). Sri Lanka Document Datasets: A large-scale multilingual resource for law, news, and policy. *arXiv preprint*.

16. Seneviratne, D., et al. (2022). Context-sensitive verb similarity dataset for legal information extraction. *Data*, 7(3), 33.

17. Smywinski-Pohl, A., Piech, M., Kaleta, Z., and Wrobel, K. (2021). Automatic extraction of amendments from Polish statutory law. *Proceedings of ICAIL*, 225–229.

18. Tulajiang, P., Sun, Y., Zhang, Y., Le, Y., Xiao, K., and Lin, H. (2025). A bilingual legal NER dataset and semantics-aware cross-lingual label transfer method for low-resource languages. *ACM Transactions on Asian and Low-Resource Language Information Processing*, 24(9), 1–21.

19. Yulianti, E., et al. (2024). Named entity recognition on Indonesian legal documents: A dataset and study using transformer-based models. *International Journal of Electrical and Computer Engineering*, 14(5), 5489–5501.

---

## APPENDICES

### Appendix A: Survey Analysis Notes

All 31 records contained affirmative consent and age confirmation. Role-specific blanks created by Google Forms branching were treated as structurally missing rather than non-response. Multiple-selection questions were counted by recognised option text. One law-student matrix response contained a non-scale phrase in several difficulty columns and was treated as invalid for ordinal summaries. No inferential test was used to compare the three lawyers with the larger groups.

**Table A1: Survey quality check**

| Check | Result |
|-------|--------|
| Valid consent | 31 of 31 |
| Age 18 or above | 31 of 31 |
| Citizens | 21 |
| Law students | 7 |
| Lawyers | 3 |
| Likely or very likely to try the system | 22 of 31 (71.0%) |

### Appendix B: Data Insertion Checklist

1. Insert gold-corpus record and entity counts by class, language, and document type.
2. Insert inter-annotator exact-span precision, recall, F1, Cohen kappa, and adjudication counts.
3. Insert split sizes and confirm that parent-provision overlap is zero.
4. Insert fold-level and held-out NER results from machine-readable experiment files.
5. Insert per-class error examples without exposing unverified legal conclusions.
6. Insert simplification readability, comprehension, preservation, and expert-review results.
7. Insert amendment reference, operation, linking, reconstruction, completeness, and unresolved-case results.
8. Insert prototype task success, completion time, satisfaction, and comprehension results.
9. Update the abstract, conclusion, lists of tables and figures, and all cross-references.
10. Verify every bibliographic record against the original publication before submission.

### Appendix C: Reproducibility Record

| Item | Required Final Value |
|------|---------------------|
| Repository commit | [GIT COMMIT HASH] |
| Gold corpus version | [VERSION AND SHA-256] |
| Split manifest | [PATH AND SHA-256] |
| Python version | 3.11.x |
| Model checkpoints | [EXACT MODEL IDENTIFIERS] |
| Random seeds | [VALUES] |
| Hardware | [CPU GPU RAM] |
| Experiment configuration | [CONFIG FILES] |
| Final result directory | [PATH] |


## APPENDIX D: EVALUATION FORMULAS AND RESULT INSERTION RULES

### D.1 Classification and NER

For every class, report true positives (TP), false positives (FP), false negatives (FN), and
support. Precision, recall, and F1 are calculated as:

\[
Precision=rac{TP}{TP+FP},\quad Recall=rac{TP}{TP+FN},\quad
F_1=rac{2	imes Precision	imes Recall}{Precision+Recall}.
\]

Micro scores pool counts across classes. Macro-F1 is the arithmetic mean of the five class-level
F1 scores. For five comparable folds:

\[
ar{x}=rac{1}{5}\sum_{i=1}^{5}x_i,\qquad
s=\sqrt{rac{\sum_{i=1}^{5}(x_i-ar{x})^2}{4}}.
\]

### D.2 Annotation agreement

\[
\kappa=rac{p_o-p_e}{1-p_e}.
\]

The pilot produced 83 exact shared spans, 188 annotator-1 spans, and 125 annotator-2 spans. The
directional exact-span comparison gives precision `83/125 = 0.6640`, recall `83/188 = 0.4415`, and
F1 `0.5304`. Token kappa was `0.6466`. Both measures must be reported.

### D.3 Simplification, amendment, and usability

\[
Preservation\ Rate=rac{Required\ source\ items\ retained}{Required\ source\ items},\quad
Comprehension=rac{Correct\ answers}{All\ questions}.
\]

\[
Linking\ Accuracy=rac{Correct\ amendment\ links}{All\ gold\ amendment\ events},\quad
Unresolved\ Rate=rac{Unresolved\ events}{All\ processed\ events}.
\]

\[
Task\ Success=rac{Successfully\ completed\ tasks}{All\ attempted\ tasks}.
\]

All currently unavailable values remain **PENDING — NOT YET MEASURED**. A value may replace a
placeholder only when its raw dataset, configuration, calculation script, and output are archived.


---

**End of Thesis**