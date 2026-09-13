# AGENTS.md — 02-ai-hermes-hub

Lightweight Python FastAPI server for local GGUF model chat on port 8787. Standalone sibling to `02-ai-hermes-webui`.

## Structure

```
02-ai-hermes-hub/
├── hub.py              # FastAPI app: routes, model loading, chat logic
├── entrypoint.sh       # Container startup script
├── Dockerfile          # python:3.11-slim based image
├── requirements.txt    # Python dependencies (fastapi, uvicorn, llama-cpp-python)
└── static/             # Vanilla JS/CSS frontend
    ├── index.html
    ├── app.js
    └── style.css
```

## Commands

```bash
# Local dev
python3 hub.py

# Docker
docker compose up -d
docker logs -f hermes-hub
```

## Conventions

- Use `__HOME__` placeholder in paths (never hardcode `/home/aldo`)
- Frontend is vanilla JS — no frameworks, pure DOM manipulation
- Backend returns JSON only; frontend handles all rendering
- Model downloads go to `~/.hermes/models/`
- Healthcheck must return HTTP 200 with `{"status": "ok"}`
- All env vars in `.env` file (never in compose)
- CSS modifications in `static/style.css` only
- Never commit model files or venv directories

## Anti-patterns

- Don't add Python packages without updating requirements.txt
- Don't modify static files outside `static/`
- Don't hardcode ports in backend (use env var `HERMES_PORT`)
- Don't use async blocking calls in FastAPI endpoints
- Don't store chat history in memory; use filesystem or DB
- Don't expose internal API routes without authentication
- Don't change healthcheck endpoint path without updating Traefik label
- Don't commit `.env` files; use `.env.example`
