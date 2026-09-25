"""Build an evidence-controlled thesis draft as Markdown, HTML, and PDF."""

# ruff: noqa: E501,I001

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


STATUS_NOTICE = """
> **DOCUMENT STATUS — EVIDENCE-CONTROLLED DRAFT (25 September 2026).**  
> This document is formatted as a thesis, but it is not yet submission-ready. Values marked
> **PENDING — NOT YET MEASURED** require completed human annotation or evaluation. The existing NER
> values are provisional validation results and are not final held-out-test performance. External
> QA benchmark evaluation has been removed from the final scope.
"""

ABSTRACT = """## ABSTRACT

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
"""

SURVEY_PENDING = """### 4.2 User Needs and Usability Evidence

**PENDING — NOT YET VERIFIED.** The working manuscript contained numerical claims for a
31-participant survey, but the anonymised raw questionnaire export and analysis script were not
available in the research repository when this draft was generated. Those claims are therefore
excluded. If the study was conducted with appropriate consent, the raw anonymised data must be
supplied, quality checked, and recalculated before respondent profiles, percentages, charts, or
conclusions are inserted.

Required reporting will include recruitment and consent procedures, exact subgroup sizes, missing
data rules, descriptive distributions, task definitions, and the limitations of convenience
sampling. No inferential population claim will be made from a small non-probability sample.
"""

NER_RESULTS = """### 4.8 NER Experimental Results

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
P=\frac{TP}{TP+FP},\qquad
R=\frac{TP}{TP+FN},\qquad
F_1=\frac{2TP}{2TP+FP+FN}.
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
"""

FORMULAS_APPENDIX = """## APPENDIX D: EVALUATION FORMULAS AND RESULT INSERTION RULES

### D.1 Classification and NER

For every class, report true positives (TP), false positives (FP), false negatives (FN), and
support. Precision, recall, and F1 are calculated as:

\[
Precision=\frac{TP}{TP+FP},\quad Recall=\frac{TP}{TP+FN},\quad
F_1=\frac{2\times Precision\times Recall}{Precision+Recall}.
\]

Micro scores pool counts across classes. Macro-F1 is the arithmetic mean of the five class-level
F1 scores. For five comparable folds:

\[
\bar{x}=\frac{1}{5}\sum_{i=1}^{5}x_i,\qquad
s=\sqrt{\frac{\sum_{i=1}^{5}(x_i-\bar{x})^2}{4}}.
\]

### D.2 Annotation agreement

\[
\kappa=\frac{p_o-p_e}{1-p_e}.
\]

The pilot produced 83 exact shared spans, 188 annotator-1 spans, and 125 annotator-2 spans. The
directional exact-span comparison gives precision `83/125 = 0.6640`, recall `83/188 = 0.4415`, and
F1 `0.5304`. Token kappa was `0.6466`. Both measures must be reported.

### D.3 Simplification, amendment, and usability

\[
Preservation\ Rate=\frac{Required\ source\ items\ retained}{Required\ source\ items},\quad
Comprehension=\frac{Correct\ answers}{All\ questions}.
\]

\[
Linking\ Accuracy=\frac{Correct\ amendment\ links}{All\ gold\ amendment\ events},\quad
Unresolved\ Rate=\frac{Unresolved\ events}{All\ processed\ events}.
\]

\[
Task\ Success=\frac{Successfully\ completed\ tasks}{All\ attempted\ tasks}.
\]

All currently unavailable values remain **PENDING — NOT YET MEASURED**. A value may replace a
placeholder only when its raw dataset, configuration, calculation script, and output are archived.
"""

CSS = """
@page { size: A4; margin: 25mm 22mm 25mm 30mm;
  @bottom-center { content: counter(page); font-size: 9pt; color: #555; } }
@page:first { @bottom-center { content: none; } }
body { font-family: "Times New Roman", "Nirmala UI", serif; font-size: 11.5pt;
  line-height: 1.55; color: #111; text-align: justify; }
h1 { font-size: 18pt; text-transform: uppercase; text-align: center; page-break-before: always;
  margin-top: 0; margin-bottom: 18pt; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 15pt; margin-top: 18pt; color: #111; }
h3 { font-size: 12.5pt; margin-top: 14pt; }
p { margin: 0 0 9pt; }
blockquote { border: 2px solid #a33; padding: 10pt; background: #fff5f5; margin: 12pt 0; }
table { width: 100%; border-collapse: collapse; margin: 12pt 0; font-size: 9.5pt; page-break-inside: avoid; }
th, td { border: 0.7pt solid #555; padding: 5pt; vertical-align: top; }
th { background: #e8edf3; text-align: left; }
pre { white-space: pre-wrap; font-family: Consolas, "Nirmala UI", monospace; font-size: 8.5pt;
  background: #f5f5f5; padding: 8pt; }
code { font-family: Consolas, "Nirmala UI", monospace; font-size: 9pt; }
.title-page { page-break-after: always; text-align: center; padding-top: 45mm; }
.title-page h1 { page-break-before: avoid; font-size: 20pt; }
.title-page p { text-align: center; margin: 16pt 0; }
.toc { page-break-after: always; }
a { color: #111; text-decoration: none; }
"""


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    """Replace a Markdown section from its start heading up to the next known heading."""
    pattern = re.compile(rf"{re.escape(start)}.*?(?={re.escape(end)})", re.DOTALL)
    updated, count = pattern.subn(lambda _match: replacement.rstrip() + "\n\n", text, count=1)
    if count != 1:
        raise ValueError(f"Could not replace section beginning {start!r}")
    return updated


def build(source: Path, output: Path) -> None:
    """Create corrected Markdown/HTML/PDF artifacts from the supplied working draft."""
    try:
        import markdown
    except ImportError as error:
        raise RuntimeError("Install Markdown before building the thesis") from error

    text = source.read_text(encoding="utf-8")
    text = re.sub(r"\A.*?(?=## DECLARATION)", "", text, count=1, flags=re.DOTALL)
    text = STATUS_NOTICE + "\n\n" + text
    text = replace_section(text, "## ABSTRACT", "## ACKNOWLEDGEMENTS", ABSTRACT)
    text = replace_section(
        text,
        "## TABLE OF CONTENTS",
        "## LIST OF TABLES",
        "## TABLE OF CONTENTS\n\n[TOC]\n\n---",
    )
    text = replace_section(
        text,
        "### 4.2 Survey Respondent Profile",
        "### 4.7 Corpus Engineering Results",
        SURVEY_PENDING,
    )
    text = replace_section(
        text,
        "### 4.8 NER Experimental Results",
        "### 4.9 Text Simplification Results",
        NER_RESULTS,
    )
    text = text.replace(
        "\n---\n\n**End of Thesis**", "\n\n" + FORMULAS_APPENDIX + "\n\n---\n\n**End of Thesis**"
    )
    text = re.sub(r"\bLawGPT\b", "external QA benchmark", text)

    output.mkdir(parents=True, exist_ok=True)
    markdown_path = output / "IM_2021_118_thesis_evidence_controlled_draft.md"
    html_path = output / "IM_2021_118_thesis_evidence_controlled_draft.html"
    pdf_path = output / "IM_2021_118_thesis_evidence_controlled_draft.pdf"
    markdown_path.write_text(text, encoding="utf-8", newline="\n")
    body = markdown.markdown(
        text,
        extensions=["extra", "toc", "sane_lists"],
        extension_configs={"toc": {"title": "Contents"}},
    )
    title_block = """
    <div class="title-page">
      <h1>Legal Document Analysis with Efficient Key Information Extraction</h1>
      <h2>An NLP-Based Framework for the Sri Lankan Constitution and Penal Code</h2>
      <p><strong>Shalika Ramanayaka - IM/2021/118</strong></p>
      <p>Supervisor: Mr. Dinesh Asanka</p>
      <p>Department of Industrial Management, Faculty of Science<br>
      University of Kelaniya, Sri Lanka</p><p>2026</p>
    </div>
    """
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
    <body>{title_block}{body}</body></html>"""
    html_path.write_text(html, encoding="utf-8", newline="\n")
    edge = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    if not edge.exists():
        edge = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if not edge.exists():
        raise RuntimeError("Microsoft Edge or Google Chrome is required for PDF rendering")
    subprocess.run(
        [
            str(edge),
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path.resolve()}",
            html_path.resolve().as_uri(),
        ],
        check=True,
    )
    print(pdf_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path, nargs="?", default=Path("docs/thesis/build"))
    args = parser.parse_args()
    build(args.source, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
