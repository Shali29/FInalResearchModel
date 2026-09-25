# Phase 1 Project Setup

## Objective

Create a maintainable VS Code/Python project foundation before any legal extraction, annotation,
or model training begins.

## Inputs

- Phase 0 audit and approved English/Sinhala research scope
- Confirmed external paths to research and legal PDFs
- The unchanged five-class NER schema

## Outputs created

- Root metadata: `README.md`, `requirements.txt`, `pyproject.toml`, `.gitignore`
- Reproducible YAML configurations in `configs/`
- Empty, purpose-specific data and result directories
- Modular package namespaces under `src/sri_lankan_legal_nlp/`
- A safe CLI skeleton that rejects unimplemented phases
- Phase 1 scope/configuration tests in `tests/`
- VS Code interpreter, testing, UTF-8, and extension recommendations
- Initial data dictionary and annotation decision gate

## Validation result

PowerShell validation confirmed that every required Phase 1 file and directory exists. Python
3.11.0 was located directly, a project-local `.venv` was created, dependencies were installed,
and executable validation passed. The Windows `py` launcher still does not list installed
runtimes, but this does not affect the project because VS Code and commands use `.venv`.

After Python 3.11 is installed, run:

```powershell
cd "F:\Me\Research\Final\MyResearchModel"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest
python -m ruff check .
python -m sri_lankan_legal_nlp --help
```

## Completion checklist

- [x] Requested project directory structure created.
- [x] Phase configurations created with fixed random seed 2026.
- [x] English/Sinhala-only scope encoded and Tamil excluded.
- [x] Five approved entity classes encoded without silently adding a class.
- [x] Raw-source mutation disabled in configuration.
- [x] Amendment cross-document inference disabled.
- [x] README contains Windows PowerShell, VS Code, testing, and pipeline commands.
- [x] Basic configuration tests created.
- [x] Required paths verified with PowerShell.
- [x] Python 3.11 installed and detected directly.
- [x] Virtual environment created and dependencies installed.
- [x] Pytest (3 passed) and Ruff (all checks passed) executed successfully.
- [x] Exact direct dependency versions recorded in `results/environment.txt`.

Phase 1 is structurally and execution complete. No later pipeline phase or research experiment
was run.
