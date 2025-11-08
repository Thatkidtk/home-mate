#!/bin/sh
set -eu

# Export env vars from .env if present
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

# Ensure runtime dirs exist
mkdir -p instance uploads

# Apply migrations (don't crash app if none)
flask --app wsgi.py db upgrade || true

# Hand off to CMD
exec "$@"
