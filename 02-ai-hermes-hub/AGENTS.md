# AGENTS.md — 02-ai-hermes-hub

## Overview
Hermes Hub: Python FastAPI backend + vanilla JS frontend for local LLM chat on port 8787.

## Structure
```
02-ai-hermes-hub/
├── Dockerfile              # Container definition
├── entrypoint.sh           # Container entrypoint
├── hub.py                  # Main FastAPI application
├── requirements.txt        # Python dependencies
└── static/                 # Vanilla JS/CSS assets (index.html, app.js, style.css)
```

## WHERE TO LOOK
| File | Purpose |
|------|---------|
| `hub.py` | Main FastAPI application (routes, models) |
| `static/app.js` | Frontend chat UI logic |
| `static/index.html` | Frontend HTML structure |
| `requirements.txt` | Python package dependencies |
| `Dockerfile` | Container image definition |
| `entrypoint.sh` | Container startup script |

## CONVENTIONS
- Use `__HOME__` placeholder in paths (never hardcode `/home/aldo`)
- Keep frontend vanilla JS — no frameworks, pure DOM manipulation
- Backend returns JSON only; frontend handles rendering
- Model downloads go to `~/.hermes/models/` via hub.py
- Healthcheck must return HTTP 200 with `{"status": "ok"}`
- All environment variables in `.env` file (never in compose)
- CSS modifications in `static/style.css` only
- Never commit model files or venv directories

## ANTI-PATTERNS
- Don't add Python packages without updating requirements.txt
- Don't modify static files outside static/ directory
- Don't hardcode ports in backend (use env var HERMES_PORT)
- Don't use async blocking calls in FastAPI endpoints
- Don't store chat history in memory; use filesystem or DB
- Don't expose internal API routes without authentication
- Don't change healthcheck endpoint path without updating traefik
- Don't commit .env files; use .env.example instead