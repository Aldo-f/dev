# Credential Sync Dashboard Architecture Reference

## Complete API Surface

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/status` | GET | Extended status (providers, cron, source health) | JSON with `providers`, `cron`, `sync_metadata` |
| `/sync` | POST | Trigger full sync (fire-and-forget) | `{ "started": true }` |
| `/api/history` | GET | Sync history (last 50 entries) | JSON array |
| `/api/cron` | GET | Read cron config | `{ enabled, schedule, next_run, readable }` |
| `/api/cron` | POST | Update cron config | `{ ok, cron: {...} }` |
| `/api/key` | POST | Add credential | `{ ok }` |
| `/api/key/:provider` | DELETE | Remove all keys for a provider | `{ ok }` |
| `/dashboard` | GET | Full HTML dashboard | HTML page |

## Data Model (`credential-pool.json`)

```json
{
  "version": "1.0.0",
  "last_sync": "ISO8601",
  "last_sync_duration_ms": 123,
  "last_sync_result": "ok",
  "providers": { "openrouter": [{ "id": "...", "label": "...", "value": "..." }] },
  "cron": {
    "enabled": false,
    "schedule": "*/30 * * * *",
    "last_run": null,
    "next_run": null
  },
  "sync_metadata": {
    "total_keys": 57,
    "providers_active": ["openrouter"],
    "sources_synced": [
      { "file": "~/.hermes/auth.json", "fmt": "json", "exists": true, "last_ok": "ISO8601" }
    ]
  }
}
```

## History Log (`logs/sync-history.json`)

```json
[
  {
    "timestamp": "ISO8601",
    "duration_ms": 412,
    "providers": 20,
    "keys": 57,
    "result": "ok",
    "sources_ok": 4,
    "sources_total": 4
  }
]
```

## Dashboard Context Interface

```typescript
interface DashboardContext {
  version: string;
  providers: Record<string, any[]>;
  sync_metadata: {
    total_keys: number;
    providers_active: string[];
    sources_synced: Array<{ file: string; fmt: string; exists: boolean; last_ok: string | null }>;
  };
  last_sync: string;
  last_sync_duration_ms: number;
  last_sync_result: string;
  cron: { enabled: boolean; schedule: string; last_run: string | null; next_run: string | null };
  history: SyncHistoryEntry[];
}
```

## Color Palette (Dark Theme)

| Usage | Hex |
|-------|-----|
| Page background | `#0d1117` |
| Card/section background | `#161b22` |
| Border | `#30363d` |
| Primary text | `#c9d1d9` |
| Secondary text | `#8b949e` |
| Success | `#3fb950` / `#238636` |
| Warning | `#d29922` |
| Error | `#f85149` / `#da3633` |
| Accent (headings) | `#58a6ff` |

## Multi-Source Reader/Writer Pattern

```
Sources: Hermes (JSON) ─┐
         Opencode (JSON) ─┤
         Omniroute (YAML) ─┤── readSources() ──► mergePools() ──► writeCentralPool()
         .env (env)      ─┘                                     │
                                                     writeSource() ◄── per source
```

- Each reader normalizes its format into `{ credential_pool: { provider: Cred[] } }`
- `mergePools()` deduplicates by `credKey()` (id → source → label → value)
- `writeSource()` denormalizes per format (YAML uses `providers:` key instead of `credential_pool:`)
