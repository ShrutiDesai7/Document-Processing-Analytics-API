# Document Processing API (FastAPI Starter)

Production-ready FastAPI starter with modular routers, config management, and `.env` support.

## Tech

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic v2 + pydantic-settings
- python-dotenv

## Project structure

```
app/
  core/        # settings, logging, dependencies
  database/    # db init/teardown placeholders
  models/      # persistence models (add later)
  routers/     # API routers
  schemas/     # request/response schemas
  services/    # business logic
  utils/       # shared helpers
  main.py      # FastAPI entrypoint
```
## Screenshots 
---
<img width="1710" height="648" alt="image" src="https://github.com/user-attachments/assets/a9188c61-2f5b-45d2-997a-7e92528ac108" />

---
<img width="925" height="532" alt="image" src="https://github.com/user-attachments/assets/62ab620d-ca75-4796-a5f1-44f2e8af7788" />

---
## Setup

1) Create and activate a virtual environment

Windows (PowerShell):
```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

2) Install dependencies
```powershell
pip install -r requirements.txt
```

Optional (dev/testing):
```powershell
pip install -r requirements-dev.txt
```

3) Configure environment variables
```powershell
Copy-Item .env.example .env
```

## Run

```powershell
uvicorn app.main:app --reload
```

## Frontend

Start the API, then open:
- `http://127.0.0.1:8000/` (dashboard)
- Static files: `http://127.0.0.1:8000/frontend/`

## Tests

```powershell
pytest
```

Open:
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/v1/health`
- Upload: `POST http://127.0.0.1:8000/api/v1/documents/upload` (form field: `file`)
- Extract: `POST http://127.0.0.1:8000/api/v1/documents/{document_id}/extract`
- Analyze: `POST http://127.0.0.1:8000/api/v1/documents/{document_id}/analyze`

## Environment variables

- `APP_NAME` (default: `Document Processing API`)
- `APP_VERSION` (default: `0.1.0`)
- `ENVIRONMENT` (default: `development`)
- `API_V1_PREFIX` (default: `/api/v1`)
- `ENABLE_DOCS` (default: `true`)
- `LOG_LEVEL` (default: `INFO`)
- `UPLOADS_DIR` (default: `uploads`)
- `DB_HOST` (default: `localhost`)
- `DB_PORT` (default: `3306`)
- `DB_USER` (default: `root`)
- `DB_PASSWORD` (default: `root`)
- `DB_NAME` (default: `document_db`)
