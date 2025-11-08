from datetime import date, timedelta
import threading
import time

from flask import current_app

from .extensions import db
from .models import Task, User


def start_scheduler(app):
    if app.config.get("DISABLE_SCHEDULER"):
        app.logger.info("Scheduler disabled via config.")
        return

    def worker():
        while True:
            try:
                with app.app_context():
                    send_due_reminders()
            except Exception:  # pragma: no cover
                app.logger.exception("Reminder job failed")
            time.sleep(24 * 60 * 60)

    thread = threading.Thread(target=worker, daemon=True, name="reminder-thread")
    thread.start()
    app.logger.info("Background reminder thread started.")


def send_due_reminders():
    tomorrow = date.today() + timedelta(days=1)
    rows = (
        db.session.query(User.email, Task.title, Task.due_date)
        .join(Task, Task.user_id == User.id)
        .filter(Task.status == "pending", Task.due_date == tomorrow)
        .all()
    )
    for email, title, due in rows:
        current_app.logger.info("Reminder: %s has '%s' due on %s", email, title, due)
