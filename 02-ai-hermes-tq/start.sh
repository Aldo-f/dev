#!/usr/bin/env bash
set -e

# Helper to start the PoC services (FastAPI + worker) in the background.
# Uses the same virtualenv created by `python -m venv .venv`.

if [ -z "$VIRTUAL_ENV" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
fi

# Install deps if not present (quietly)
pip install -q -r requirements.txt || pip install -r requirements.txt

# Start FastAPI server (background, notify on exit)
.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8788 &
SERVER_PID=$!

echo "FastAPI server PID $SERVER_PID"

# Start worker loop (foreground – will run until stopped)
python worker.py

# When worker exits, stop the server
kill $SERVER_PID || true
