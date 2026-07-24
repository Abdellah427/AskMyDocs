#!/usr/bin/env bash
# Launch AskMyDocs locally on Linux or macOS.
# Creates a virtual environment, installs dependencies, then starts the app.

set -e
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  "$PY" -m venv .venv
fi

# shellcheck disable=SC1091
. .venv/bin/activate

echo "Installing dependencies..."
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt

# Load MISTRAL_API_KEY from a local .env file if present.
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

if [ -z "${MISTRAL_API_KEY:-}" ]; then
  echo "Warning: MISTRAL_API_KEY is not set. Copy .env.example to .env and add your key to enable answers."
fi

echo "Starting AskMyDocs..."
exec streamlit run app.py
