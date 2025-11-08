from datetime import date


def register_filters(app):
    def money(value):
        try:
            number = float(value or 0)
        except (TypeError, ValueError):
            number = 0
        return f"${number:,.2f}"

    def task_badge(task, today=None):
        today = today or date.today()
        if task.status == "done":
            return {"class": "text-bg-success", "label": "Done"}
        if task.due_date and task.due_date < today:
            return {"class": "text-bg-danger", "label": "Overdue"}
        if task.due_date and (task.due_date - today).days <= 7:
            return {"class": "text-bg-warning text-dark", "label": "Due soon"}
        if task.due_date:
            return {"class": "text-bg-secondary", "label": "Scheduled"}
        return {"class": "text-bg-secondary", "label": "Open"}

    app.jinja_env.filters["money"] = money
    app.jinja_env.globals["task_badge"] = task_badge
