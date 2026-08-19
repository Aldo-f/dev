# HTTP API specification

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/status` | Full JSON with all providers, key counts, and sync metadata |
| `POST` | `/sync` | Trigger a sync (fire‑and‑forget), returns `{ started: true }` |
| `GET` | `/dashboard` | HTML dashboard page with provider table |
| `POST` | `/api/key` | Add a key — body `{ provider, label, key }` |
| `GET` | `/api/free-keys` | Returns mock demo keys for OpenRouter, Gemini, xAI |

## Examples
```bash
# Status
curl http://localhost:3003/status

# Trigger sync
curl -X POST http://localhost:3003/sync -d '{"mode":"sync"}'

# Add a key
curl -X POST http://localhost:3003/api/key \
  -H 'Content-Type: application/json' \
  -d '{"provider":"openrouter","label":"my-key","key":"sk-or-abc123"}'

# HTML dashboard (open in browser)
open http://localhost:3003/dashboard
```

## Notes
- The server runs on port **3003** by default (configurable via `PORT` env var).
- `POST /api/key` writes to all source files and triggers an immediate background sync.
- The `/dashboard` endpoint returns a complete HTML page — no build step needed.
