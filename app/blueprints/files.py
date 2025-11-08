from pathlib import Path
from flask import Blueprint, current_app, send_from_directory, abort
from flask_login import login_required, current_user

from ..models import Attachment

bp = Blueprint("files", __name__)


@bp.get("/files/<int:attachment_id>")
@login_required
def get_attachment(attachment_id):
    attachment = Attachment.query.filter_by(id=attachment_id, user_id=current_user.id).first_or_404()
    directory = Path(current_app.config["UPLOAD_FOLDER"])
    file_path = directory / attachment.key
    if not file_path.exists():
        abort(404)
    return send_from_directory(
        directory,
        attachment.key,
        mimetype=attachment.mime or "application/octet-stream",
        as_attachment=False,
        download_name=attachment.original_name or attachment.key,
        max_age=300,
    )
