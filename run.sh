#!/usr/bin/env bash
# One-click launcher for AskMyDocs on Linux or macOS.
# Checks Python, creates the virtual environment, installs the dependencies
# (once), loads the API key, and starts the app.

set -e
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Python 3 not found. Install Python 3.10+ and run this script again."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creating the virtual environment..."
  "$PY" -m venv .venv
fi

# shellcheck disable=SC1091
. .venv/bin/activate

# Dependencies are installed once; delete .venv/.installed to force a reinstall.
if [ ! -f ".venv/.installed" ]; then
  echo "Installing dependencies. The first run can take a few minutes..."
  python -m pip install --upgrade pip >/dev/null
  python -m pip install -r requirements.txt
  touch ".venv/.installed"
fi

# Self-heal a broken mistralai install (the "cannot import name 'Mistral'" case).
if ! python -c "from mistralai import Mistral" >/dev/null 2>&1; then
  echo "Repairing the mistralai package..."
  python -m pip install --force-reinstall --no-cache-dir "mistralai>=1.0"
fi

# Load MISTRAL_API_KEY from a local .env file if present.
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

if [ -z "${MISTRAL_API_KEY:-}" ]; then
  echo "Note: MISTRAL_API_KEY is not set. Search works, but answer generation is disabled."
  echo "To enable it, copy .env.example to .env and put your key in it."
fi

echo "Starting AskMyDocs..."
exec streamlit run app.py
