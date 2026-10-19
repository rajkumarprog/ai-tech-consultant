#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv"

if [[ ! -f "$VENV/bin/activate" ]]; then
  echo "ERROR: Virtual environment not found at $VENV"
  echo "Create it with: python3 -m venv .venv"
  echo "Then install dependencies with: .venv/bin/pip install -r requirements.txt"
  exit 1
fi

source "$VENV/bin/activate"

if [[ ! -f "$ROOT/.env" ]]; then
  echo "WARNING: Root .env file not found."
  echo "LLM-powered features may not work until you configure your API credentials."
fi

cleanup() {
  echo
  echo "Stopping application services..."
  [[ -z "${API_PID:-}" ]] || kill "$API_PID" 2>/dev/null || true
  [[ -z "${UI_PID:-}" ]] || kill "$UI_PID" 2>/dev/null || true
  [[ -z "${API_PID:-}" ]] || wait "$API_PID" 2>/dev/null || true
  [[ -z "${UI_PID:-}" ]] || wait "$UI_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting Knowledge Brain API on http://localhost:8001"
(
  cd "$ROOT/task1-knowledge-brain"
  exec uvicorn app.main:app --host 0.0.0.0 --port 8001
) &
API_PID=$!

echo "Starting Inbox Review UI on http://localhost:8501"
(
  cd "$ROOT/task2-inbox-agent"
  exec streamlit run review_app.py --server.address 0.0.0.0 --server.port 8501
) &
UI_PID=$!

echo
echo "Knowledge Brain: http://localhost:8001"
echo "API documentation: http://localhost:8001/docs"
echo "Inbox Review UI: http://localhost:8501"
echo "Press Ctrl+C to stop both services."

wait -n "$API_PID" "$UI_PID"
