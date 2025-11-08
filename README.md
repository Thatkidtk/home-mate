
# Home Maintenance Tracker

Local-first Flask + SQLite app for tracking assets (home, vehicles, appliances), maintenance tasks, and attachments (receipts/photos).

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
# First run will apply migrations and start the server at http://localhost:8000
```

### Sign in
- Visit `http://localhost:8000/auth/register` to create the first household user, or use the seeded account `household@example.com / change-me-now` and update the password immediately.

### Default paths
- DB: `instance/app.db`
- Uploads: `uploads/` (mounted as a volume)

### Sample data (optional)
```bash
FLASK_APP=wsgi.py flask seed-data
# or python scripts/seed_data.py
```
Seeds assets & tasks for your first user so the dashboard isn't empty while designing.

### Handy commands
```bash
make run      # dev server with auto-reload
make seed     # seed demo data
make fmt      # Ruff + Black
```

## Local dev (optional)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app wsgi.py db upgrade
flask --app wsgi.py run --debug
```

## App structure

```
app/
  __init__.py         # app factory, config, blueprints
  extensions.py       # db, migrate, csrf
  models.py           # SQLAlchemy models
  blueprints/
    main.py           # dashboard
    assets.py         # assets CRUD
    tasks.py          # tasks CRUD
  templates/          # Jinja2 templates
  static/
instance/             # SQLite DB lives here (created at runtime)
uploads/              # receipt/photo uploads
migrations/           # Alembic migrations (Flask-Migrate)
```

## Notes
- This is a scaffold with working CRUD for Assets and Tasks (minimal UI) plus local account auth (Flask-Login + CSRF).
- Tasks list supports instant HTMX filters/search/sort and CSV export.
- Attachments (images/PDFs) can be uploaded per task; files stay under `instance/uploads`.
- A background reminder thread logs upcoming tasks daily (wire in email later).
- Attachments endpoints and OCR are stubbed for later.
- Upcoming roadmap: reminders, attachment uploads, backups/export tooling.
