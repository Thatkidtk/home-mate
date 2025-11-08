import secrets
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_DEFAULT = {"png", "jpg", "jpeg", "pdf"}


def save_upload(file_storage):
    if not file_storage or not file_storage.filename:
        raise ValueError("Select a file to upload.")
    filename = secure_filename(file_storage.filename)
    if not filename:
        raise ValueError("Invalid file name.")

    allowed = current_app.config.get("ALLOWED_EXTENSIONS", ALLOWED_DEFAULT)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if allowed and ext not in allowed:
        raise ValueError("Unsupported file type.")

    key = f"{secrets.token_hex(8)}_{filename}"
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / key
    file_storage.save(path)
    size = path.stat().st_size
    return {"key": key, "size": size, "mime": file_storage.mimetype or "application/octet-stream", "original": filename}
