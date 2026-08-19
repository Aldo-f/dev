# Sync Dashboard – Full Control Panel Plan

## Goal
Transform the current credential-sync dashboard into a **single-page web control panel** where you can see *everything* and *do everything* — no terminal needed.

## What the new dashboard will show

### 1. Overview / Hero
- ✅ Total credentials synced (57)
- ✅ Total providers (20)
- ✅ Last sync timestamp & duration
- ✅ Sync status (OK / Warning / Error)
- ✅ Uptime / health of all upstream source files

### 2. Provider Table (main content)
Each provider row shows:
- **Provider name** (with colour-coded health dot)
- **Key count** (clickable to expand the list)
- **Source distribution** (how many keys came from Hermes / Opencode / Omniroute / .env)
- **Last updated** (timestamp)
- **Actions**: Add key, Remove key, Copy to clipboard

### 3. Source Status Panel
For each source file (`~/.hermes/auth.json`, `~/.config/opencode/auth.json`, `~/dev/02-ai-omniroute/config.yaml`, `~/dev/02-ai-freellm-api/.env`):
- **File exists?** (yes/no)
- **Last modified** (human-readable)
- **File permissions** (0600? 0644?)
- **Last sync result** (success/failure)
- **Reachable** (is the parent directory there?)

### 4. Sync History Table
- Timestamp, duration (ms), total providers, total keys, result (✅/❌)
- Stored in `logs/sync-history.json`
- Filterable / sortable

### 5. Cron Sync Controls
- **Toggle switch**: Enable / Disable scheduled sync (writes/removes a crontab line)
- **Schedule selector**: Every 15min / 30min / 1h / 6h / daily / custom cron expression
- **Last cron run** (timestamp + result)
- **Next scheduled run** (calculated)

### 6. Key Management (inline)
- **Add key**: Provider dropdown + label + key value + optional source target
- **Remove key**: Select provider → select key → confirm delete
- **Bulk import**: Paste multiple keys (one per line: `provider:label:key`)
- All actions trigger an immediate sync

### 7. Settings / Configuration
- **Central pool path** (editable)
- **Source files** (enable/disable individual sources)
- **Max sync history** entries
- **Auto-refresh** interval (seconds)

---

## Technical Architecture

```
src/
  server.ts             ← Hono API server (port 3003) — already exists, extend
  dashboard/
    api.ts              ← /api/* route handlers (status, sync, cron, keys, history)
    admin.ts            ← /api/admin/* (settings, reset, diagnostic)
    html.ts             ← HTML template rendering (single HTML payload, no build step)
    components/         ← HTML partials (JS-free, server-rendered)
      header.ts
      overview.ts
      provider-table.ts
      source-status.ts
      sync-history.ts
      cron-controls.ts
      key-manager.ts
    styles.css           ← Inline in HTML or served as /dashboard.css
    dashboard.js         ← Client-side interactivity (HTMX-like, plain JS)
```

### Approach
**Vanilla HTML + JS** — no React build step, no bundler. The server renders full HTML fragments (like HTMX), and a small `<script>` tag adds:
- Auto-refresh every N seconds (configurable)
- Modal popups for Add/Remove key
- Confirmation dialogs for destructive actions
- Toast notifications for async operations (sync started, key added)
- Toggle switches for cron control

The API returns JSON for programmatic clients and HTML for the browser dashboard.

---

## Data Model (extended `credential-pool.json`)

```json
{
  "version": "1.0.0",
  "last_sync": "2026-07-30T10:00:00.000Z",
  "last_sync_duration_ms": 1234,
  "last_sync_result": "ok",
  "providers": { ... },
  "sync_metadata": {
    "total_keys": 57,
    "providers_active": ["openrouter", ...],
    "sources_synced": [
      { "file": "~/.hermes/auth.json", "fmt": "json", "exists": true, "last_ok": "2026-07-30T10:00:00.000Z" },
      ...
    ]
  },
  "cron": {
    "enabled": false,
    "schedule": "*/30 * * * *",
    "last_run": null,
    "next_run": null
  }
}
```

### Sync history log (`logs/sync-history.json`)
```json
[
  {
    "timestamp": "2026-07-30T10:00:00.000Z",
    "duration_ms": 1234,
    "providers": 20,
    "keys": 57,
    "result": "ok",
    "sources_ok": 4,
    "sources_total": 4
  }
]
```

---

## Implementation Steps

| # | Milestone | What it delivers | Files |
|---|-----------|-----------------|-------|
| **1** | **Extend pool with cron & source metadata** | `credential-pool.json` now stores cron config + per-source status + last sync duration | `src/index.ts` — update `writeCentralPool()`, add `writeCronConfig()` |
| **2** | **Sync history logging** | Every sync appends to `logs/sync-history.json`; API exposes `/api/history` | `src/writers/history-writer.ts`, `src/api.ts` |
| **3** | **Cron management API** | `GET/POST /api/cron` — read config, enable/disable, update schedule | `src/api.ts` |
| **4** | **Rich HTML dashboard** | Full single-page dashboard replacing the basic `/dashboard` endpoint | `src/dashboard/html.ts` (and component files) |
| **5** | **Client-side interactivity** | Auto-refresh, toasts, modals, toggle switches → no manual page reloads | `src/dashboard/dashboard.js` |
| **6** | **Inline key management** | Add/remove keys directly from the dashboard UI | `src/dashboard/components/key-manager.ts` |
| **7** | **Source status panel** | Shows live health of every upstream credential file | `src/dashboard/components/source-status.ts` |
| **8** | **Ansible integration** | Deploy the cron-enable toggle via Ansible cron role update | `dev/01-core-infra/ansible/roles/cron/` updates |
| **9** | **Tests for new endpoints** | Test suite covers API routes, cron logic, and history | `tests/api.test.ts`, `tests/cron.test.ts` |

---

## File changes checklist

### New files to create
- `src/dashboard/api.ts` — API route handlers
- `src/dashboard/admin.ts` — Admin/settings endpoints
- `src/dashboard/html.ts` — Main HTML template renderer
- `src/dashboard/dashboard.js` — Client-side JS
- `src/dashboard/styles.css` — Dashboard CSS
- `src/dashboard/components/header.ts`
- `src/dashboard/components/overview.ts`
- `src/dashboard/components/provider-table.ts`
- `src/dashboard/components/source-status.ts`
- `src/dashboard/components/sync-history.ts`
- `src/dashboard/components/cron-controls.ts`
- `src/dashboard/components/key-manager.ts`
- `src/writers/history-writer.ts`
- `tests/api.test.ts`
- `tests/cron.test.ts`

### Existing files to modify
- `src/server.ts` — Reorganize routes, mount dashboard API
- `src/index.ts` — Update `writeCentralPool()`, expose cron config functions
- `package.json` — Add scripts for dashboard
- `credential-pool.json` — Add new fields

---

## Timeline

| Phase | What | Est. time |
|-------|------|-----------|
| **Phase 1** | Backend APIs (history, cron, extended status) | 2h |
| **Phase 2** | HTML dashboard template + components | 2h |
| **Phase 3** | Client-side JS interactivity | 1.5h |
| **Phase 4** | Key management UI | 1h |
| **Phase 5** | Testing + Ansible integration | 1.5h |
| **Total** | | **8h** |

---

## Visual mockup (text-only)

```
┌─────────────────────────────────────────────────────────┐
│  🔐 LLM‑Infra‑Sync Dashboard                    [⏻]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─ Provider Summary ────────────────────────────────┐  │
│  │  ● 57 total keys  ● 20 providers  ● 4 sources     │  │
│  │  Last sync: 30s ago (✅) • Duration: 412ms        │  │
│  └────────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─ Source Health ────────────────────────────────────┐  │
│  │  ✅ ~/.hermes/auth.json          (2 min ago)       │  │
│  │  ✅ ~/.config/opencode/auth.json (2 min ago)       │  │
│  │  ⚠️  ~/dev/02-ai-omniroute/...  (file missing)    │  │
│  │  ✅ ~/dev/02-ai-freellm-api/.env (2 min ago)       │  │
│  └────────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─ Providers ────────────────────────────────────────┐  │
│  │  Provider        │ Keys │ Sources        │ Actions │  │
│  │  ────────────────┼──────┼────────────────┼──────── │  │
│  │  🟢 openrouter   │  10  │ Herm, Open, Env│ [+][−]  │  │
│  │  🟢 gemini       │   8  │ Herm, Open     │ [+][−]  │  │
│  │  🟡 xai          │   3  │ Herm, Env      │ [+][−]  │  │
│  │  ...                                                     │
│  └────────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─ Sync Controls ────────────────────────────────────┐  │
│  │  [────────── Sync Now ──────────]                  │  │
│  │  Cron: [🔘] Enabled  Schedule: [Every 30 min ▾]   │  │
│  │  Last cron: 10:00 ✅  Next: 10:30                  │  │
│  └────────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─ Sync History ─────────────────────────────────────┐  │
│  │  Time          │ Result │ Prov. │ Keys │ Duration │  │
│  │  10:00:12      │ ✅     │ 20    │ 57   │ 412ms    │  │
│  │  09:30:05      │ ✅     │ 20    │ 57   │ 389ms    │  │
│  │  09:00:18      │ ❌     │ —     │ —    │ 0ms      │  │
│  └────────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## How to start

```bash
cd ~/dev/02-ai-llm-infra-sync

# Phase 1 – Extend backend
# 1a. Update writeCentralPool in src/index.ts
# 1b. Add history-writer.ts
# 1c. Add cron API routes

# Phase 2 – Dashboard
# 2a. Create src/dashboard/html.ts (main template)
# 2b. Create components/*.ts

# Phase 3 – Client JS
# 3a. Create src/dashboard/dashboard.js

# Phase 4 – Wire into server.ts
# 4a. Mount /api/* and /dashboard routes

# Phase 5 – Test & verify
# 5a. bun test
# 5b. curl http://localhost:3003/dashboard
```

---

Ready to proceed. Shall I start implementing **Phase 1** (backend APIs for history, cron, and extended status)?