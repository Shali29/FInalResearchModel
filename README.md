# Sri Lankan Legal NLP

Research implementation for **Legal Document Analysis with Efficient Key Information
Extraction: An NLP-Based Framework for the Sri Lankan Constitution and Penal Code**.

The project covers the Sri Lankan Constitution and Penal Code in English and Sinhala. It builds
a provenance-preserving corpus, Legal NER models, a Sinhala legal-text simplification component,
and amendment tracking. LawGPT is an external evaluation benchmark, not a model duplicated by
this repository.

> **Legal-information notice:** This research system provides legal information and source
> references. It does not provide legal advice. Outputs marked `pending` or `unverified` must not
> be treated as authoritative legal conclusions.

## Current status

- Phase 0: completed (research and source-document audit)
- Phase 1: completed and verified with Python 3.11.0
- Phase 2: extraction software and automated run completed; OCR corrections/manual review pending
- Phase 3: conservative alignment software and automated run completed; bilingual review pending
- Phase 4: five-part 420-task Annotator 1 expansion completed and validated; independent 84-task Annotator 2 subset pending
- Phase 5: expanded provisional 500-task leakage-safe split and five development folds completed
- Phase 6: dictionary and CRF baselines rerun on expanded provisional validation data; expanded transformer reruns pending
- Phase 7: data-readiness audit and blank expert-review workflow implemented; verified pairs and glossary pending
- Phase 8: deterministic amendment candidates and manual-review sheet implemented; gold review and consolidation pending
- Phase 9: FastAPI backend and Streamlit research interface implemented; usability evaluation pending
- Phases 10-11: not yet executed

See [the Phase 0 audit](docs/phase0_audit_and_implementation_plan.md) before changing scope or
starting annotation.

## Prerequisites for Windows

Install the following tools:

1. Python 3.11 (64-bit), including the Python launcher and PATH option.
2. Visual Studio Code with the Microsoft Python extension.
3. Git.
4. Tesseract OCR with English (`eng`) and Sinhala (`sin`) language data before Phase 2 OCR.

Verify Python from a new PowerShell window:

```powershell
py -3.11 --version
```

The project environment is currently available in `.venv` using Python 3.11.0. The commands below
remain the reproducible setup procedure for another computer or a clean rebuild.

## Environment setup in PowerShell

Open the project:

```powershell
cd "F:\Me\Research\Final\MyResearchModel"
code .
```

Create and activate a local virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

If PowerShell blocks activation for the current process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This changes policy only for the current PowerShell process.

Record the exact installed environment after a successful installation:

```powershell
python --version | Out-File -Encoding utf8 results\environment.txt
python -m pip freeze | Out-File -Encoding utf8 -Append results\environment.txt
```

## Selecting the VS Code interpreter

1. Press `Ctrl+Shift+P`.
2. Choose **Python: Select Interpreter**.
3. Select `.venv\Scripts\python.exe` from this project.
4. Open a new VS Code terminal and run `python --version`.

The workspace recommendation is stored in `.vscode/settings.json`.

## Validate Phase 1

With the environment activated:

```powershell
python -m pytest
python -m ruff check .
python -m sri_lankan_legal_nlp --help
```

## Pipeline commands

Implemented commands create provenance-preserving artifacts. Commands for unimplemented phases
stop with an explicit message rather than fabricating output.

```powershell
# Phase 2: document inventory and extraction (implemented in Phase 2)
python -m sri_lankan_legal_nlp extract --config configs\data_config.yaml

# Phase 3: bilingual alignment (implemented)
python -m sri_lankan_legal_nlp align --config configs\data_config.yaml

# Phase 4: prepare blank annotation tasks (implemented)
python -m sri_lankan_legal_nlp prepare-annotation --config configs\ner_config.yaml

# Phase 5: grouped split feasibility audit
python -m sri_lankan_legal_nlp split --config configs\ner_config.yaml

# Phase 5: create the current provisional grouped datasets
python scripts\create_grouped_splits.py data\processed\expanded_provisional_corpus.jsonl data\splits\expanded_provisional

# Phase 6: NER experiments
python -m sri_lankan_legal_nlp train-ner --config configs\ner_config.yaml

# Phase 6 transformer experiments (run separately; downloads large checkpoints)
python scripts\train_transformer_ner.py --config configs\ner_config.yaml --model bert-base-multilingual-cased
python scripts\train_transformer_ner.py --config configs\ner_config.yaml --model xlm-roberta-base

# Phase 7: simplification
python -m sri_lankan_legal_nlp simplify --config configs\simplification_config.yaml

# Phase 8: amendment tracking
python -m sri_lankan_legal_nlp track-amendments --config configs\amendment_config.yaml

# Phase 9: API (after implementation)
python -m uvicorn sri_lankan_legal_nlp.api.main:app --reload

# Phase 9: interface (run in a second terminal)
python -m streamlit run app\streamlit_app.py
python -m uvicorn sri_lankan_legal_nlp.api.main:app --reload

# Phase 10: research analysis
python -m sri_lankan_legal_nlp analyze --config configs\ner_config.yaml

# Phase 11: quality assurance
python -m sri_lankan_legal_nlp qa --config configs\data_config.yaml
```

For the entity-enriched human-annotation pilot, import
`data\annotation\label_studio_enriched_pilot_tasks.json`. The independent second annotator imports
`data\annotation\label_studio_enriched_shared_tasks.json`. These files contain selection cues but
no generated entity labels.

Validate a Doccano export and convert it to BIO CoNLL after human annotation:

```powershell
python scripts\validate_annotations.py data\annotation\annotated_export.jsonl
python scripts\export_annotations.py data\annotation\annotated_export.jsonl data\processed\ner.conll
```

Convert two Label Studio exports and calculate independent-annotator agreement:

```powershell
python scripts\convert_label_studio_export.py data\annotation\annotator1_labelstudio_export.json data\annotation\annotator1.jsonl
python scripts\convert_label_studio_export.py data\annotation\annotator2_labelstudio_export.json data\annotation\annotator2.jsonl
python scripts\validate_annotations.py data\annotation\annotator1.jsonl
python scripts\validate_annotations.py data\annotation\annotator2.jsonl
python scripts\calculate_agreement.py data\annotation\annotator1.jsonl data\annotation\annotator2.jsonl results\ner\inter_annotator_agreement.json
```

## Data policy

- Original PDFs remain outside this repository at the configured source directory.
- `data/raw/` is reserved for an optional controlled copy or links; raw legal documents are never
  overwritten.
- Generated corpora and model artifacts are ignored by Git by default.
- Every extracted record must retain document, language, provision, filename, page, extraction
  method, and verification provenance.
- UTF-8 is mandatory. Sinhala text must not be transliterated as a substitute for OCR recovery.

## Main directories

- `configs/`: reproducible pipeline settings
- `data/`: raw pointers/copies and generated corpus stages
- `docs/`: audit, assumptions, annotation guidance, and data definitions
- `src/sri_lankan_legal_nlp/`: modular Python package
- `tests/`: automated tests
- `models/`: local checkpoints (not committed)
- `results/`: metrics, reports, figures, and environment records
- `app/`: future user-interface assets
