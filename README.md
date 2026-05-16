# halprog - Eticket sample app

This repository contains a small Flask + SQLAlchemy event/reservation application used for a coursework project.

Quick start:

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r backend/requirements.txt`.
3. Run the app: `cd backend && python app.py`.

Repository layout after reorganization:

- `backend/` — Python backend code (Flask app, models, migrations, scripts).
- `frontend/` — Jinja templates and static assets (CSS/JS/images).
- `tests/` — Test scripts and integration test helpers.

To run locally (from project root):

```powershell
cd backend
python app.py
```

Configuration like database credentials should be placed in `config.ini` or environment variables and must NOT be checked into git.
