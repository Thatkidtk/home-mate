
from collections import Counter
from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, url_for
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Task, Asset

bp = Blueprint("main", __name__)


def _month_start(base: date, months_back: int) -> date:
    year = base.year
    month = base.month
    for _ in range(months_back):
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return date(year, month, 1)


def _next_month(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)


@bp.get("/")
@login_required
def index():
    today = date.today()
    week_ahead = today + timedelta(days=7)
    first_of_month = today.replace(day=1)
    first_of_prev_month = _month_start(first_of_month, 1)

    pending_count = (
        Task.query.filter_by(user_id=current_user.id, status="pending")
        .count()
    )

    overdue_query = Task.query.filter(
        Task.user_id == current_user.id,
        Task.status == "pending",
        Task.due_date != None,  # noqa: E711
        Task.due_date < today,
    )
    overdue_count = overdue_query.count()
    oldest_overdue = overdue_query.order_by(Task.due_date.asc()).with_entities(Task.due_date).first()

    asset_count = Asset.query.filter_by(user_id=current_user.id).count()
    warrantied = Asset.query.filter(
        Asset.user_id == current_user.id,
        Asset.warranty_expiration != None,  # noqa: E711
        Asset.warranty_expiration >= today,
    ).count()

    def _sum_cost(start_date: date, end_date: date | None = None) -> float:
        query = Task.query.filter(
            Task.user_id == current_user.id,
            Task.status == "done",
            Task.updated_at != None,  # noqa: E711
            Task.updated_at >= datetime.combine(start_date, datetime.min.time()),
        )
        if end_date:
            query = query.filter(
                Task.updated_at < datetime.combine(end_date, datetime.min.time())
            )
        total = 0
        for task in query.all():
            if task.cost:
                total += float(task.cost)
        return round(total, 2)

    month_cost = _sum_cost(first_of_month)
    prev_month_cost = _sum_cost(first_of_prev_month, first_of_month)

    upcoming_tasks = (
        Task.query.filter(
            Task.user_id == current_user.id,
            Task.status == "pending",
            Task.due_date != None,  # noqa: E711
            Task.due_date <= week_ahead,
        )
        .order_by(Task.due_date.asc())
        .limit(8)
        .all()
    )
    upcoming = []
    for task in upcoming_tasks:
        due_dt = task.due_date
        upcoming.append(
            {
                "id": task.id,
                "title": task.title,
                "asset_name": task.asset.name if task.asset else "",
                "due_label": due_dt.strftime("%b %d") if due_dt else None,
                "is_overdue": bool(due_dt and due_dt < today),
                "due_date": due_dt,
                "is_soon": bool(due_dt and due_dt >= today and due_dt <= week_ahead),
            }
        )

    due_next_week = sum(
        1 for item in upcoming if item["due_date"] and not item["is_overdue"] and item["due_date"] <= week_ahead
    )

    chart_start_month = _month_start(first_of_month, 11)
    chart_months = []
    cursor = chart_start_month
    for _ in range(12):
        chart_months.append(cursor)
        cursor = _next_month(cursor)

    chart_start_dt = datetime.combine(chart_months[0], datetime.min.time())
    completed_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.status == "done",
        Task.updated_at != None,  # noqa: E711
        Task.updated_at >= chart_start_dt,
    ).all()
    month_counter = Counter()
    for task in completed_tasks:
        stamp = task.updated_at or task.created_at
        if stamp:
            month_counter[(stamp.year, stamp.month)] += 1

    chart_labels = [month.strftime("%b %Y") for month in chart_months]
    chart_values = [month_counter.get((month.year, month.month), 0) for month in chart_months]

    recent_tasks = (
        Task.query.filter(Task.user_id == current_user.id)
        .order_by(Task.updated_at.desc())
        .limit(5)
        .all()
    )
    activity = []
    for task in recent_tasks:
        timestamp = task.updated_at or task.created_at
        activity.append(
            {
                "icon": "bi-clipboard-check" if task.status == "done" else "bi-clipboard-plus",
                "text": f"<strong>{task.title}</strong> {'completed' if task.status == 'done' else 'updated'}",
                "when": timestamp.strftime("%b %d, %I:%M %p") if timestamp else "—",
                "link": url_for("tasks.edit_task", task_id=task.id),
            }
        )

    stats = {
        "pending": pending_count,
        "due_7d": due_next_week,
        "overdue": overdue_count,
        "oldest_overdue": oldest_overdue[0].strftime("%b %d") if oldest_overdue and oldest_overdue[0] else None,
        "asset_count": asset_count,
        "warrantied": warrantied,
        "month_cost": month_cost,
        "prev_month_cost": prev_month_cost,
    }

    return render_template(
        "dashboard/index.html",
        stats=stats,
        upcoming=upcoming,
        activity=activity,
        chart_labels=chart_labels,
        chart_values=chart_values,
    )
