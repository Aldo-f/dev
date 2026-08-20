# AGENTS.md – 02-ai-hermes-tq

Hermes task queue — a small Python (FastAPI) work-queue service, deployed as a
container via `04-network-traefik` compose. Task records are JSON + Markdown
persisted under `tasks/` (not a SQLite DB).

## Entry points
- `entrypoint.sh` – starts the FastAPI worker then `uvicorn server:app` (internal port `8788`).
- `server.py` – FastAPI service exposing `/api/tasks`, `/api/tasks/{id}`,
  `/run`, `/reset`, `/log`, `/api/stats` CRUD endpoints.
- `worker.py` – background worker loop (filesystem locking, sequential run).
- `queue.py` – in-process queue primitive (`queue.lock` contention lock).
- `executor.py` – runs jobs via `hermes -z` headless mode; validates the
  `### VALIDATION` block to determine success.
- `state.py` – persistent task state.
- `validate.py`, `run.sh`, `start.sh` – validation + local run helpers.

## Structure
- `static/` – Neo-Brutalist vanilla JS/CSS UI served by the API.
- `tasks/` – uuid-named task state + Markdown records (runtime data, not source).
- `tests/` – pytest suite (API routes, task validation, UI rendering).
- `requirements.txt` – pinned deps; `Dockerfile` builds the image.

## Commands
```bash
# Deploy via Traefik compose (recommended)
cd ~/dev/04-network-traefik
docker compose up -d --build

# View logs
docker compose logs -f hermes-tq

# Run tests locally
python -m pytest tests/
```

## Deployment
- Service name in compose: `hermes-tq`
- Internal port: `8788`
- Traefik route: `tq.hermes.dev.aldof.duckdns.org` (with `ipAllowList` middleware)
- Networks: `traefik_net` + `docker-stack_core-network`
- Volume: `taskqueue-data` (persistent at `/app/tasks`)
- Healthcheck: `curl -f http://localhost:8788/api/stats`

## Conventions
- Do **not** run the FastAPI server as root inside Docker.
- Never store plaintext secrets in task records; use environment-injected keys.
- Avoid blocking I/O in request handlers – keep task operations async.
- Do **not** disable CORS globally; configure allowed origins.
- Keep worker (dispatch) and executor (run) responsibilities separate.
- Never commit `__pycache__` or venv dirs.
