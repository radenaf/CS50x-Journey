# BioLab

BioLab is a modular computational molecular biology workspace. The first release contains the Dashboard and Module 1, PCR Assistant.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000.

## Test

```powershell
pytest
```

The development database is SQLite (`biolab.db`). Set `DATABASE_URL` to use another SQLAlchemy-supported database later. Flask-Migrate is initialized for future migration workflows.

## Current scope

- Dashboard with workspace statistics and recent experiments
- PCR Assistant landing page
- Draft PCR experiment creation, list, and detail view
- Complete editable PCR protocol editor with user-defined steps and cycle groups
- `.pcr` JSON-backed protocol save, open, duplicate, and template snapshot workflows
- Assay creation and listing
- PCR template listing
- Foundation models for samples, controls, reagents, and structured PCR programs
- Configurable calculation services for master mix scaling and PCR program duration

PCR Results and Sequence Analyzer are intentionally marked Coming Soon and are not implemented.
