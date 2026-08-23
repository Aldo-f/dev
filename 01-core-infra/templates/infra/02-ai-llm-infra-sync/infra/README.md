# 02‑ai‑llm‑infra‑sync

## Overview
This repository implements a **credential‑sync engine** for a local LLM infrastructure. It reads credentials from multiple local sources (Hermes, Opencode, an `.env` file, and a YAML config), merges them into a central pool (`credential‑pool.json`), de‑duplicates entries, and writes the unified pool back to each source.

## Quick start
```bash
# Clone the repo (already done in your workspace)
cd ~/dev/02-ai-llm-infra-sync

# Install dependencies (Bun)
~/.bun/bin/bun install

# Run the sync engine (full sync)
~/.bun/bin/bun run src/index.ts
```

## Command‑line interface
```bash
# Status (shows provider key counts)
~/.bun/bin/bun run src/cli.ts --mode status

# Full sync (default mode)
~/.bun/bin/bun run src/cli.ts --mode sync
```

## Dashboard (Web – Full Control Panel)

The most powerful way to interact with the sync engine:

```bash
# Start the dashboard + API server (background)
~/.bun/bin/bun run src/server.ts &
```

Open **http://localhost:3003/dashboard** in a browser for the full control panel:

### What you can do from the dashboard

| Feature | How |
|---------|-----|
| **View provider keys** | Table of all 20+ providers with key counts |
| **Add a new API key** | Click `+` on any provider row, or use the global `+ Add Key` button |
| **Remove API keys** | Click `−` to delete all keys for a provider |
| **Trigger sync** | Click `⟳ Sync Now` |
| **Enable cron sync** | Toggle the Cron Sync switch to enable/disable automated syncing |
| **Change sync schedule** | Pick from Every 15min / 30min / 1h / 6h / Daily |
| **View sync history** | Scrollable table of past syncs with duration & result |
| **Check source health** | See whether each credential file exists and when it was last synced |
| **Auto-refresh** | The dashboard refreshes every 10 seconds automatically |

### Dashboard API (JSON)

All dashboard features are accessible via JSON API too:

```bash
# Extended status
curl http://localhost:3003/api/status

# Sync history
curl http://localhost:3003/api/history

# Cron config
curl http://localhost:3003/api/cron

# Enable cron
curl -X POST http://localhost:3003/api/cron \
  -H 'Content-Type: application/json' \
  -d '{"enabled":true,"schedule":"*/30 * * * *"}'

# Add a key
curl -X POST http://localhost:3003/api/key \
  -H 'Content-Type: application/json' \
  -d '{"provider":"openrouter","label":"my-key","key":"sk-or-..."}'

# Delete a provider's keys
curl -X DELETE http://localhost:3003/api/key/openrouter

# Trigger sync
curl -X POST http://localhost:3003/sync
```

## Dashboard (TUI – Terminal UI)
```bash
~/.bun/bin/bun run src/dashboard.tsx
```
Shows a simple Ink‑based terminal dashboard with provider key counts.

## Key‑generator UI (port 3004)
```bash
# Start the UI (requires `KEYGEN_TOKEN` env var)
KEYGEN_TOKEN=secret ~/.bun/bin/bun run key-generator/server.ts &
```
Open `http://localhost:3004/keys/new?token=secret` in a browser, fill the form, and the server will:
1. Write the new key to the appropriate source files.
2. Trigger an immediate sync.

## Testing
```bash
~/.bun/bin/bun test
```
The test suite covers:
- JSON, YAML, and `.env` readers.
- Writers for each format.
- Merge/dedupe logic.
- End‑to‑end credential‑sync behavior.

## Development
- **Bun** is the primary runtime (`~/.bun/bin/bun`).
- All imports use the `.js` extension (ESM). 
- The project is **type‑safe** (TypeScript) but compiled on‑the‑fly by Bun.

## Integration with Ansible (01‑core‑infra)
- The `mesh_sync` role runs `bun run src/status.ts` after deployment to verify the sync engine works.
- The `tools` role now installs **Spec‑Kit** in a dedicated virtual‑env and adds it to `$PATH`.

## License
MIT – see `LICENSE`.
