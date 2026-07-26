#!/usr/bin/env bash
# ============================================================
#  AskMyDocs - uninstall the local environment (Linux/macOS).
#  Removes the Python virtual environment and caches.
#  Your source code, documents and .env file are kept.
# ============================================================

set -e
cd "$(dirname "$0")"

echo "This removes the local Python environment (.venv) and caches."
echo "Your source code, documents and .env file are kept."
echo
read -r -p "Continue? (y/N): " CONFIRM
case "$CONFIRM" in
  y | Y) ;;
  *)
    echo "Cancelled."
    exit 0
    ;;
esac

rm -rf .venv .pytest_cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

echo
echo "Done. Run ./launch.sh to set it up again."
echo "Downloaded models are cached in ~/.cache/huggingface (delete that folder to reclaim space)."
