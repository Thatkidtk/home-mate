
import os
from pathlib import Path
from flask import Flask
from .extensions import db, migrate, csrf, login_manager
from .blueprints.main import bp as main_bp
from .blueprints.assets import bp as assets_bp
from .blueprints.tasks import bp as tasks_bp
from .blueprints.files import bp as files_bp
from .errors import bp as errors_bp
from .logging_utils import setup_logging
from .cli import register_cli
from .filters import register_filters
from .scheduler import start_scheduler

BASE_DIR = Path(__file__).resolve().parent.parent

def _resolve_sqlite_uri(uri: str, instance_path: str) -> str:
    """Ensure sqlite URIs that use relative paths become absolute paths."""
    prefix = "sqlite:///"
    if not uri.startswith(prefix):
        return uri
    raw_path = uri[len(prefix):]
    if raw_path.startswith("/") or raw_path.startswith("file:"):
        return uri
    rel_path = Path(raw_path)
    if rel_path.parts and rel_path.parts[0] == "instance":
        rel_path = Path(*rel_path.parts[1:])
        abs_path = Path(instance_path) / rel_path
    else:
        abs_path = (BASE_DIR / rel_path)
    return f"{prefix}{abs_path.resolve()}"

def create_app():
    app = Flask(__name__, instance_relative_config=True, template_folder="templates", static_folder="static")
    setup_logging(app)
    register_cli(app)
    register_filters(app)

    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret")
    default_db_uri = f"sqlite:///{(Path(app.instance_path) / 'app.db').resolve()}"
    configured_uri = os.getenv("SQLALCHEMY_DATABASE_URI", default_db_uri)
    app.config["SQLALCHEMY_DATABASE_URI"] = _resolve_sqlite_uri(configured_uri, app.instance_path)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", str(Path(app.instance_path) / "uploads"))
    max_content = os.getenv("MAX_CONTENT_LENGTH")
    try:
        app.config["MAX_CONTENT_LENGTH"] = int(max_content) if max_content else 16 * 1024 * 1024
    except (TypeError, ValueError):
        app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    is_dev = app.config.get("ENV") == "development" or bool(app.config.get("DEBUG")) or os.getenv("FLASK_DEBUG") == "1"
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("SESSION_COOKIE_SECURE", not is_dev)
    app.config.setdefault("REMEMBER_COOKIE_HTTPONLY", True)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "error"

    from .models import User  # noqa: WPS433

    @login_manager.user_loader
    def load_user(user_id: str):
        if not user_id:
            return None
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None

    app.register_blueprint(main_bp)
    app.register_blueprint(assets_bp, url_prefix="/assets")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    from .blueprints.auth import bp as auth_bp  # noqa: WPS433
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(errors_bp)
    app.register_blueprint(files_bp)
    start_scheduler(app)

    @app.after_request
    def secure_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )
        return response

    return app
