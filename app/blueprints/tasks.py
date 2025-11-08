
import csv
import io
from datetime import date, timedelta
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from flask_login import login_required, current_user
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import joinedload
from ..extensions import db
from ..models import Task, Asset, Attachment
from ..utils.dates import parse_iso_date
from ..utils.storage import save_upload

bp = Blueprint("tasks", __name__)

@bp.get("/")
@login_required
def list_tasks():
    status = request.args.get("status", "all")
    window = request.args.get("window")
    search = (request.args.get("q") or "").strip()
    sort = request.args.get("sort", "due")
    direction = request.args.get("dir", "asc")

    query = (
        Task.query.options(joinedload(Task.asset))
        .filter(Task.user_id == current_user.id)
    )

    today = date.today()
    if status == "open":
        query = query.filter(Task.status == "pending")
    elif status == "overdue":
        query = query.filter(Task.status == "pending", Task.due_date != None, Task.due_date < today)  # noqa: E711
    elif status == "done":
        query = query.filter(Task.status == "done")

    if window == "7d":
        query = query.filter(Task.due_date != None, Task.due_date <= today + timedelta(days=7))  # noqa: E711
    elif window == "30d":
        query = query.filter(Task.due_date != None, Task.due_date <= today + timedelta(days=30))  # noqa: E711

    if search:
        query = query.join(Asset, isouter=True).filter(
            or_(
                Task.title.ilike(f"%{search}%"),
                Asset.name.ilike(f"%{search}%"),
            )
        )

    sort_map = {
        "title": Task.title,
        "created": Task.created_at,
        "due": Task.due_date,
    }
    sort_col = sort_map.get(sort, Task.due_date)
    order_func = asc if direction == "asc" else desc
    query = query.order_by(order_func(sort_col).nullslast())

    tasks = query.limit(250).all()
    template = "tasks/_table.html" if request.headers.get("HX-Request") else "tasks/list.html"
    return render_template(
        template,
        tasks=tasks,
        status=status,
        window=window,
        sort=sort,
        dir=direction,
        search=search,
        today=today,
    )

@bp.route("/create", methods=["GET","POST"])
@login_required
def create_task():
    assets = Asset.query.filter_by(user_id=current_user.id).order_by(Asset.name.asc()).all()
    if not assets:
        flash("Create an asset first.", "error")
        return redirect(url_for("assets.create_asset"))
    if request.method == "POST":
        asset_id = request.form.get("asset_id", type=int)
        title = request.form.get("title","").strip()
        if not title or not asset_id:
            flash("Asset and title are required.", "error")
            return redirect(request.url)
        Asset.query.filter_by(id=asset_id, user_id=current_user.id).first_or_404()
        task = Task(
            user_id=current_user.id,
            asset_id=asset_id,
            title=title,
            description=request.form.get("description") or None,
            due_date=parse_iso_date(request.form.get("due_date")),
            recurrence_rule=request.form.get("recurrence_rule") or None,
            priority=request.form.get("priority", type=int, default=0),
            estimated_minutes=request.form.get("estimated_minutes", type=int, default=0),
            cost=request.form.get("cost") or None,
            vendor=request.form.get("vendor") or None,
        )
        db.session.add(task)
        db.session.commit()
        flash("Task created", "success")
        return redirect(url_for("tasks.list_tasks"))
    return render_template("tasks/form.html", assets=assets, task=None)

@bp.route("/<int:task_id>/edit", methods=["GET","POST"])
@login_required
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    assets = Asset.query.filter_by(user_id=current_user.id).order_by(Asset.name.asc()).all()
    if request.method == "POST":
        task.asset_id = request.form.get("asset_id", type=int) or task.asset_id
        Asset.query.filter_by(id=task.asset_id, user_id=current_user.id).first_or_404()
        task.title = request.form.get("title","").strip() or task.title
        task.description = request.form.get("description") or None
        task.due_date = parse_iso_date(request.form.get("due_date"))
        task.recurrence_rule = request.form.get("recurrence_rule") or None
        task.priority = request.form.get("priority", type=int, default=0)
        task.estimated_minutes = request.form.get("estimated_minutes", type=int, default=0)
        task.cost = request.form.get("cost") or None
        task.vendor = request.form.get("vendor") or None
        db.session.commit()
        flash("Task updated", "success")
        return redirect(url_for("tasks.list_tasks"))
    return render_template("tasks/form.html", assets=assets, task=task)

@bp.post("/<int:task_id>/complete")
@login_required
def complete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.status = "done"
    db.session.commit()
    flash("Task completed", "success")
    return redirect(url_for("tasks.list_tasks"))

@bp.post("/<int:task_id>/delete")
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted", "success")
    return redirect(url_for("tasks.list_tasks"))


@bp.get("/export.csv")
@login_required
def export_tasks():
    query = Task.query.filter_by(user_id=current_user.id).options(joinedload(Task.asset))
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["Title", "Asset", "Due", "Status", "Completed"])
    for task in query.order_by(Task.due_date.asc().nullslast()):
        writer.writerow([
            task.title,
            task.asset.name if task.asset else "",
            task.due_date.isoformat() if task.due_date else "",
            task.status,
            task.updated_at.isoformat() if task.status == "done" and task.updated_at else "",
        ])
    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=tasks.csv"},
    )


@bp.post("/<int:task_id>/attachments")
@login_required
def upload_attachment(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    file = request.files.get("file")
    try:
        saved = save_upload(file)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("tasks.edit_task", task_id=task.id))
    attachment = Attachment(
        user_id=current_user.id,
        task_id=task.id,
        key=saved["key"],
        original_name=saved["original"],
        mime=saved["mime"],
        size=saved["size"],
    )
    db.session.add(attachment)
    db.session.commit()
    flash("Attachment uploaded.", "success")
    return redirect(url_for("tasks.edit_task", task_id=task.id))


@bp.post("/attachments/<int:attachment_id>/delete")
@login_required
def delete_attachment(attachment_id):
    attachment = Attachment.query.filter_by(id=attachment_id, user_id=current_user.id).first_or_404()
    task_id = attachment.task_id
    _delete_file(attachment.key)
    db.session.delete(attachment)
    db.session.commit()
    flash("Attachment removed.", "success")
    return redirect(url_for("tasks.edit_task", task_id=task_id))


def _delete_file(key):
    filepath = Path(current_app.config["UPLOAD_FOLDER"]) / key
    try:
        filepath.unlink(missing_ok=True)  # type: ignore[arg-type]
    except OSError:
        current_app.logger.warning("Could not delete file %s", filepath)
