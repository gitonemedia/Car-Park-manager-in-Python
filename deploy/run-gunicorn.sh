#!/usr/bin/env bash
set -euo pipefail

# Small helper to run gunicorn from the project's virtualenv.
# Assumes repository layout: <repo>/venv and <repo>/app.py

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$BASE_DIR/venv"
GUNICORN_BIN="$VENV_DIR/bin/gunicorn"

if [ ! -x "$GUNICORN_BIN" ]; then
  echo "ERROR: gunicorn not found at $GUNICORN_BIN" >&2
  echo "Install it with: $VENV_DIR/bin/pip install gunicorn" >&2
  exit 1
fi

cd "$BASE_DIR"

# Ensure log directory exists (may require appropriate permissions)
LOG_DIR="/var/log/carpark"
mkdir -p "$LOG_DIR" || true

exec "$GUNICORN_BIN" \
  --workers 3 \
  --bind 127.0.0.1:5000 \
  --access-logfile "$LOG_DIR/gunicorn.access.log" \
  --error-logfile "$LOG_DIR/gunicorn.error.log" \
  app:app
