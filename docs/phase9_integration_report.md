# Phase 9 — Integrated Prototype

## Objective

Provide a lightweight interface to the research components while keeping model logic separate,
showing source provenance and verification status, and displaying a legal-information disclaimer.

## Implemented components

The FastAPI backend provides:

- `POST /ner`: provisional CRF entity recognition for English or Sinhala text
- `GET /sources/search`: literal source-record and provision search with provenance
- `POST /simplification/prepare`: a blank human-review template, not generated legal meaning
- `GET /amendments`: unverified amendment candidates, optionally filtered by provision number
- `GET /health`: service health check

The Streamlit interface accepts English or Sinhala text, displays NER output, prepares a
simplification-review record, and searches amendment candidates. Every relevant response includes
the research status or legal-information disclaimer.

## Run locally

Open two VS Code PowerShell terminals. In the first terminal:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn sri_lankan_legal_nlp.api.main:app --reload
```

API documentation is then available at `http://127.0.0.1:8000/docs`.

In the second terminal:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app\streamlit_app.py
```

## Limitations

The CRF model has provisional validation micro-F1 of 0.1985 and is not suitable for authoritative
legal use. Simplification fields remain pending human and expert review. Amendment results remain
unverified candidates; the system does not automatically consolidate legislation. The prototype
provides legal information for research and is not legal advice.
