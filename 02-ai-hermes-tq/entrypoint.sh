#!/bin/bash
set -e

# Start worker in background
python worker.py &

# Start FastAPI server (foreground)
exec uvicorn server:app --host 0.0.0.0 --port 8788