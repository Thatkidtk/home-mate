import logging
import sys


def setup_logging(app):
    """Attach a stdout logger so Gunicorn/Flask share the same format."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)

    if not app.logger.handlers:
        app.logger.addHandler(handler)
    else:
        # Replace default handler formatting.
        for existing in app.logger.handlers:
            existing.setFormatter(formatter)

    app.logger.setLevel(logging.INFO)
