#!/usr/bin/env bash
set -e

# Ensure virtualenv is active
if [ -z "$VIRTUAL_ENV" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
fi

# Install deps if missing
pip install -r requirements.txt >/dev/null 2>&1 || pip install -r requirements.txt

# Start FastAPI server in background
uvicorn server:app --host 127.0.0.1 --port 8788 &
SERVER_PID=$!

echo "FastAPI server PID $SERVER_PID"

# Start worker loop (foreground) – will run indefinitely
python worker.py

# When worker exits, kill server
kill $SERVER_PID
