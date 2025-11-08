
# Home Maintenance Tracker

Local-first household maintenance journal built with Flask + SQLite. Track every asset (home, HVAC, vehicles, appliances), schedule recurring tasks, upload receipts, and export everything when you need it.

## Highlights

- **Dashboard KPIs** – Pending/overdue counts, warranty stats, monthly spend sparkline.
- **HTMX-powered lists** – Instant filters, search, and sortable tables for both assets and tasks.
- **Task attachments** – Upload PDFs or images (receipts, manuals, warranties) per task and open them securely.
- **CSV export** – One click to download your entire task history.
- **Seedable demo data** – Populate a fake household to try out the UI in seconds.
- **Docker-first** – `docker compose up --build` runs migrations, seeds volumes, and serves via Gunicorn.
- **Secure defaults** – CSRF protection, safe cookie flags, per-user file access, and structured logging.

---

## 1. Quick Start (Docker)

```bash
cp .env.example .env       # edit FLASK_SECRET_KEY before going public
docker compose up --build
```

First boot applies migrations and hosts the app at [http://localhost:8000](http://localhost:8000).

### Accounts
- Visit `/auth/register` to create your household login, **or**
- Sign in with the seeded account `household@example.com / change-me-now` (change the password immediately).

### Default paths
| Item | Location |
| --- | --- |
| SQLite DB | `instance/app.db` |
| Uploads | `instance/uploads/` (mounted in Docker) |

---

## 2. Local Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app wsgi.py db upgrade
make run       # or flask --app wsgi.py run --debug
```

### Handy `make` targets
| Command | Description |
| --- | --- |
| `make run` | Dev server with debug + reload |
| `make seed` | Seed demo assets/tasks (`flask seed-data`) |
| `make fmt` | Ruff + Black (auto-fix) |
| `make db-up` | Apply pending migrations |

### Sample data
```bash
make seed           # or FLASK_APP=wsgi.py flask seed-data
```
Populates the first user with assets + tasks so the dashboard isn’t empty.

---

## 3. Features & Usage

### Dashboard
- KPI cards link to filtered task views.
- Upcoming section highlights due-soon or overdue work.
- Recent activity feed surfaces latest edits/completions.

### Tasks
- Status + time-window filters (`All`, `Open`, `Overdue`, `Done`, `7 days`, `30 days`).
- Search box (title or asset name) and sortable columns (Title, Due, Created).
- CSV export button downloads everything with one click.
- Attachments panel (on edit) for uploading receipts/manuals; files stay private per-user.

### Assets
- HTMX search with live results.
- Type-specific icons for quick scanning.
- Floating-label forms with validation-friendly date inputs.

### Reminders
A lightweight nightly thread logs due-tomorrow tasks (`INFO Reminder: ...`). Swap the logger with your email/SMS service when you’re ready.

### Security & Backups
- CSRF protection on every form, session cookies are HTTP-only + SameSite.
- File downloads check ownership before serving.
- Everything lives in SQLite + `instance/uploads`, making backups as easy as copying that folder or running `docker compose down && tar instance uploads`.

---

## 4. Configuration

| Variable | Description | Default |
| --- | --- | --- |
| `FLASK_SECRET_KEY` | Session & CSRF secret | `dev-secret` (change!) |
| `SQLALCHEMY_DATABASE_URI` | DB connection | `sqlite:///instance/app.db` |
| `UPLOAD_FOLDER` | Where attachments live | `instance/uploads` |
| `MAX_CONTENT_LENGTH` | Upload cap (bytes) | `16777216` (16 MB) |
| `DISABLE_SCHEDULER` | Skip reminder thread | unset |

Set these in `.env` before deploying.

---

## 5. Project Structure

```
app/
  blueprints/          # dashboard, assets, tasks, auth, files
  utils/               # date parsing, file storage
  scheduler.py         # nightly reminder thread
  filters.py           # money + badge helpers
  logging_utils.py     # shared logging formatter
  cli.py               # flask seed-data command
  models.py            # SQLAlchemy models (User/Asset/Task/Attachment)
  templates/           # Jinja2 views (Bootstrap 5 + HTMX)
  static/style.css     # custom styling
migrations/            # Alembic revisions
scripts/seed_data.py   # standalone seeding script
docker-compose.yml     # Gunicorn + Flask service
docker-entrypoint.sh   # runs migrations + launches Gunicorn
```

---

## 6. Development Tips

- **Pre-commit** – Run `pre-commit install` to lint before every commit (`ruff`, `black`, `pyupgrade`).
- **Tests** – (Add Pytest soon) start with smoke tests for CRUD endpoints.
- **Attachments** – Allowed types are `png`, `jpg`, `jpeg`, `pdf`. Adjust in `app/utils/storage.py`.
- **Production** – Swap the reminder logger with your mailer, point SQLite to a network path (or move to Postgres by updating `SQLALCHEMY_DATABASE_URI`), and rotate secrets via env vars.

---

## 7. Roadmap Ideas

- Receipt gallery & inline previews
- Automatic recurrence generation
- Email/SMS delivery for reminders
- Off-site backup/restore bundle (DB + uploads + manifest)
- Multi-user roles (household vs. guests)

Contributions welcome—open an issue or PR if you build something cool.
