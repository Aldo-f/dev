---
name: llm-credential-sync
description: Sync AI credentials across sources via CLI, UI, API.
category: devops
---

# LLM Credential Sync Engine

## Overview
A unified credential pool (`credential-pool.json`) that aggregates API keys from multiple sources (Hermes, OpenCode, Omniroute, Freellmapi). Deduplicates keys, preserves metadata, and writes back to each source in its native format (JSON, YAML, `.env`).

The complete design document for the next evolution (rich web dashboard) lives in [`DASHBOARD-PLAN.md`](DASHBOARD-PLAN.md).

## Components
| Component | File | Description |
|-----------|------|-------------|
| **Sync engine** | `src/index.ts` | Core: reads sources → merges → writes pool → distributes back |
| **CLI** | `src/cli.ts` | Commander‑based entry point (`--mode sync|status`) |
| **Status** | `src/status.ts` | Quick provider‑key table from all sources |
| **Dashboard (TUI)** | `src/dashboard.tsx` | Ink‑based interactive UI showing provider key counts |
| **HTTP API** | `src/server.ts` | Hono server on port 3003 (`/status`, `/sync`, `/dashboard`, `/api/*`) |
| **Key‑generator UI** | `key-generator/server.ts` | Express form on port 3004 with human‑verification checkbox |
| **Readers** | `src/readers/*` | JSON, YAML, `.env` format readers |
| **Writers** | `src/writers/*` | JSON, YAML, `.env` format writers |
| **Tests** | `tests/*.test.ts` | Bun test suite (run with `bun test`) |

## Usage
```bash
# Install dependencies (run once)
bun install

# Full sync
bun run src/index.ts

# CLI wrapper
bun run src/cli.ts --mode sync
bun run src/cli.ts --mode status

# Status (quick)
bun run src/status.ts

# Dashboard (TUI)
bun run src/dashboard.tsx

# HTTP API (background)
bun run src/server.ts &

# Key‑generator UI
KEYGEN_TOKEN=secret bun run key-generator/server.ts &

# Run tests
bun test
```

## HTTP API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/status` | Full JSON with all providers and sync metadata |
| `POST` | `/sync` | Trigger a sync (fire‑and‑forget), returns `{ started: true }` |
| `GET` | `/dashboard` | HTML dashboard page |
| `POST` | `/api/key` | Add a key (`{ provider, label, key }`) – writes to all sources + triggers sync |
| `GET` | `/api/free-keys` | Returns mock demo keys |

## CI
- `.github/workflows/ci.yml` runs `bun install`, `bun test`, `bun run src/status.ts` on every push.

## References
- [Pitfalls & fixes](references/pitfalls.md)
- [HTTP API spec](references/api.md)
- [Dashboard usage](references/dashboard.md)
- [Key‑generator UI guide](references/keygen.md)
- [Style preferences](references/style-preferences.md)
