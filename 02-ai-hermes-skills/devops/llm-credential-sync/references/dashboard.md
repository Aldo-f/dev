# Dashboard usage details

## Ink TUI (terminal)
```bash
bun run src/dashboard.tsx
```
Shows a concise table of providers and the number of stored keys. Auto-updates when `credential-pool.json` changes. Press **Ctrl C** to exit.

## HTML dashboard (browser)
```bash
# Requires the API server to be running
bun run src/server.ts &
# Then open
open http://localhost:3003/dashboard
```
Serves a clean HTML table of provider key counts — no JavaScript required.

## DASHBOARD-PLAN.md
The file [`DASHBOARD-PLAN.md`](../DASHBOARD-PLAN.md) contains the full specification for a future single-page web control panel with:
- Overview hero panel (total keys, sync health)
- Provider table with colour-coded health dots
- Source status panel (✅/⚠️/❌ per upstream file)
- Sync history log
- Cron sync controls (enable/disable, schedule selector)
- Inline key management (add, remove, bulk import)
- Auto-refresh, modals, toasts, toggle switches

## Dependencies
- `react`, `react-dom`, `ink` for the TUI — all installed via `bun install`.
