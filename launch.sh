#!/usr/bin/env bash
# ============================================================
#  AskMyDocs - one-click launcher for Linux and macOS.
#  Checks Python, sets up the environment, repairs it if needed,
#  runs a self-test, and only then starts the app.
# ============================================================

set -e
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Python 3 not found. Install Python 3.10+ and run this script again."
  exit 1
fi

# 1. Virtual environment
if [ ! -d ".venv" ]; then
  echo "Creating the virtual environment..."
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate

# 2. First-time dependency install
if [ ! -f ".venv/.installed" ]; then
  echo "Installing dependencies. The first run can take a few minutes..."
  python -m pip install --upgrade pip >/dev/null
  python -m pip install -r requirements.txt
  touch ".venv/.installed"
fi

# 3. Self-test, with one automatic repair attempt
echo "Checking the installation..."
if ! python selftest.py; then
  echo
  echo "Some checks failed. Attempting an automatic repair..."
  python -m pip install --upgrade -r requirements.txt
  if ! python -c "from mistralai import Mistral" >/dev/null 2>&1; then
    echo "Reinstalling mistralai..."
    python -m pip uninstall -y mistralai
    python -m pip install --no-cache-dir "mistralai>=1.0"
  fi
  echo "Re-checking..."
  if ! python selftest.py; then
    echo
    echo "Automatic repair could not fix everything. See the messages above."
    exit 1
  fi
fi

# 4. Load MISTRAL_API_KEY from .env if present (the app also reads it itself)
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

echo "Starting AskMyDocs... it will open at http://localhost:8501"
exec streamlit run app.py
