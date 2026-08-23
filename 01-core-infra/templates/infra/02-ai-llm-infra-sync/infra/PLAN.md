# Central Credential Pool Sync Plan

## Overview
Transform `02-ai-llm-infra-sync` into the **single source of truth** for all provider credentials across the ecosystem.

## Architecture
```mermaid
graph TD
  CENTRAL[Central Pool (credential-pool.json)]
  CENTRAL -->|IMPORT/EXPORT| HERMES[~/.hermes/auth.json]
  CENTRAL -->|IMPORT/EXPORT| OPencode[~/.config/opencode/auth.json]
  CENTRAL -->|IMPORT/EXPORT| OMNIROUTE[~/dev/02-ai-omniroute/config.yaml]
  CENTRAL -->|IMPORT/EXPORT| FREELLAPI[~/dev/02-ai-freellm-api/.env]
  CENTRAL -->|IMPORT/EXPORT| KEYSDIR[~/dev/02-ai-freellmapi/keys/ (directory)]
  CENTRAL -->|STORE| FREELLAPI_KEYS[Directory: ~/dev/02-ai-freellmapi/keys/ (individual .json files)]

  style CENTRAL fill:#f9f,stroke:#333
  style HERMES fill:#bbf,stroke:#333
  style OPencode fill:#bbf,stroke:#333
  style OMNIROUTE fill:#bbf,stroke:#333
  style FREELLAPI fill:#bbf,stroke:#333
  style KEYSDIR fill:#bb8,stroke:#333
```

## Central Pool Schema
```json
{
  "version": "1.0.0",
  "last_sync": "2026-07-24T12:00:00.000Z",
  "providers": {
    "openrouter": [
      {
        "id": "openrouter",
        "label": "OpenRouter API Key",
        "auth_type": "api_key",
        "value": "sk-or-...",
        "source": "hermes",
        "metadata": {
          "created": "2026-07-24T10:00:00.000Z",
          "last_sync": "2026-07-24T12:00:00.000Z"
        }
      }
    ],
    "gemini": [...],
    "xai": [...]
  },
  "sync_metadata": {
    "total_keys": 15,
    "providers_active": ["openrouter", "gemini", "xai", "anthropic"],
    "sources_synced": ["hermes", "opencode", "omniroute", "freellmapi", "freellmapi-keys"]
  }
}
```

## File Structure
```
02-ai-llm-infra-sync/
├── src/
│   ├── index.ts          # Main sync engine
│   ├── types.ts          # Shared types/interfaces
│   ├── config.ts         # Configuration constants
│   ├── readers/
│   │   ├── json-reader.ts
│   │   ├── yaml-reader.ts
│   │   └── env-reader.ts
│   ├── writers/
│   │   ├── json-writer.ts
│   │   ├── yaml-writer.ts
│   │   ├── env-writer.ts
│   │   └── keys-dir-writer.ts
│   └── utils/
│       └── dedupe.ts     # Credential deduplication logic
├── credential-pool.json  # Central pool (source of truth)
├── README.md
└── package.json
```

## Sync Modes

| Mode | Direction | Description |
|------|-----------|-------------|
| `sync` | Bidirectional | Full sync: read all sources, merge, write pool, broadcast to all |
| `import` | Inbound | Pull from all sources into pool only |
| `export` | Outbound | Push pool to all external sources |
| `verify` | Read-only | Check consistency, report issues |
| `status` | Read-only | Show current pool state |
| `dashboard` | Interactive | Visual overview (TUI/CLI) |

## Provider Key Mapping

| Source | Format | Key Location | Mapping Pattern |
|--------|--------|--------------|-----------------|
| hermes | JSON | `credential_pool.{provider}[]` | Array of Cred objects |
| opencode | JSON | `credential_pool.{provider}[]` | Same as hermes |
| omniroute | YAML | `providers.{provider}[]` | Needs adaptation |
| freellmapi/.env | ENV | `FREEAPI_{PROVIDER}_KEY` | Flat keys |
| freellmapi/keys/ | JSON files | `{provider}-{id}.json` | Individual files |

## Implementation Steps

1. ✅ Create central pool file (`credential-pool.json`)
2. ⏳ Refactor `index.ts` with modular architecture (readers, writers, utils)
3. ⏳ Add `freellmapi-keys` directory support (export individual JSON files)
4. ⏳ Add CLI argument parsing for modes (`sync`, `import`, `export`, `verify`, `status`, `dashboard`)
5. ⏳ Add verification mode (run ad-hoc verification script)
6. ⏳ Update `package.json` scripts (`sync`, `verify`, `status`, `dashboard`)
7. ⏳ Implement dashboard features (visual overview, provider summary, sync history)
8. ⏳ Implement status command (CLI overview)
9. ⏳ Add monitoring integration (JSON API endpoint for observability)
10. ⏳ Add alert system and health checks
11. ⏳ Add report generation (daily/weekly summaries)
12. ⏳ Update documentation with new features

## Security Considerations
- Never log credential values
- Use file permissions (0600) for sensitive files
- Support encrypted backups via `FREEAPI_DB_BACKUP_KEY`
- Add audit trail of sync operations

## Dashboard & Observability
### Goal
Provide a quick visual overview of the credential synchronization ecosystem:

| What | Where | When |
|------|-------|------|
| Key Types | All connected services | Real-time |
| Key Locations | Sources & targets | Last sync |
| Sync Health | All components | Current state |
| Manual Trigger | CLI/API | On-demand |

### Dashboard Features
| Feature | CLI | Web | TUI |
|---------|-----|-----|-----|
| Provider Summary | ✅ | ✅ | ✅ |
| Key Count by Type | ✅ | ✅ | ✅ |
| Source Locations | ✅ | ✅ | ✅ |
| Last Sync Timestamp | ✅ | ✅ | ✅ |
| Sync History | ✅ | ✅ | ✅ |
| Health Status | ✅ | ✅ | ✅ |
| Manual Trigger | ✅ | ✅ | ✅ |

#### 1. `status` Command (CLI Overview)
```bash
$ bun run status

  📊 CREDENTIAL SYNC STATUS

  ┌─ CENTRAL POOL
  │  📍 Location: /home/aldo/dev/02-ai-llm-infra-sync/credential-pool.json
  │  🔢 Total Keys: 56
  │  📦 Providers: 18 active
  │  ⏰ Last Sync: 2026-07-24T12:41:50.380Z

  ┌─ SOURCE STATUS
  │  ✅ ~/.hermes/auth.json            (JSON)
  │  ❌ ~/.config/opencode/auth.json   (missing)
  │  ❌ ~/dev/02-ai-omniroute/config.yaml (missing)
  │  ❌ ~/dev/02-ai-freellm-api/.env   (missing)

  ┌─ TARGET STATUS
  │  ✅ ~/dev/02-ai-freellmapi/keys/    (56 files written)

  ┌─ SYNC METADATA
  │  🔄 Mode: bidirectional
  │  📊 Sync history: last 5 syncs tracked
  │  ⚠️  Warnings: None

  ┌─ QUICK ACTIONS
  │  [s] Sync now    | [v] Verify    | [r] Reset

  └─ Press any key to return...
```

#### 2. `dashboard` Command (Interactive TUI)
```bash
$ bun run dashboard

  ╭─ CREDENTIAL SYNC DASHBOARD ────────────────────────────────────────╮
  │                                                                     │
  │  PROVIDER BREAKDOWN                                                  │
  │  ┌─ OpenCode (11) ──┐  ┌─ Gemini (8) ──┐  ┌─ XAI (3) ──┐           │
  │  │                 │  │               │  │           │           │
  │  └─────────────────┘  └───────────────┘  └───────────┘           │
  │  ...                                                               │
  │  SYNC HISTORY                                                      │
  │  ┌─ Today 12:41 (✅) ──┐  ┌─ Yesterday ──┐                     │
  │  │                     │  │             │                     │
  │  └─────────────────────┘  └─────────────┘                     │
  │  ...                                                               │
  │                                                                     │
  │  ACTIONS                                                            │
  │  [n] New sync    [c] Config   [h] Help   [q] Quit                 │
  │                                                                     │
  ╰─────────────────────────────────────────────────────────────────────╯
```

#### 3. JSON API Endpoint (For Monitoring)
```typescript
// /src/api/dashboard.ts
export async function getDashboardState() {
  return {
    timestamp: new Date().toISOString(),
    pool: {
      totalKeys: 56,
      providers: 18,
      lastSync: "2026-07-24T12:41:50.380Z",
    },
    sources: [
      { name: ".hermes/auth.json", type: "json", exists: true },
      { name: ".config/opencode/auth.json", type: "json", exists: false },
      { name: "omniroute/config.yaml", type: "yaml", exists: false },
      { name: "freellm-api/.env", type: "env", exists: false },
    ],
    targets: [
      { name: "freellmapi-keys/", type: "directory", fileCount: 56, exists: true },
    ],
    syncHistory: [ ... ], // recent sync events
    health: {
      status: "healthy",
      warnings: [],
      lastSuccessfulSync: "2026-07-24T12:41:50.380Z"
    }
  };
};
```

#### 4. Monitoring Integration
```bash
$ curl http://localhost:3000/api/dashboard
{
  "timestamp": "2026-07-24T19:45:32.124Z",
  "pool": { "totalKeys": 56, "providers": 18, "lastSync": "2026-07-24T12:41:50.380Z" },
  "sources": [ ... ],
  "targets": [ ... ],
  "health": {
    "status": "healthy",
    "warnings": [],
    "lastSuccessfulSync": "2026-07-24T12:41:50.380Z"
  }
}
```

#### 5. Manual Sync Trigger
- **CLI Interface**: `$ bun run sync --manual` or `$ bun run sync --force --all-sources`
- **File System Watch**: 
  ```typescript
  chokidar "${home}/.hermes/auth.json".on('change', async () => {
    console.log('🔄 Auth change detected - triggering sync...');
    await main();
  });
  ```
- **Scheduled Cron Jobs** (recommended):
  ```bash
  # Run hourly
  0 * * * * /home/aldo/.bun/bin/bun run sync
  ```

#### 6. Report Generation
- **Daily Summary**: Markdown report with total keys, new keys, errors, success rate.
- **Alert System**: Detect stale sources, failed syncs, quota exhaustion.
- **Log Retention**: Keep last 30 days of sync events in `sync-history.json`.

## Example Implementation
```typescript
// /src/commands/status.ts
import { Command } from 'commander';

program
  .command('status')
  .description('Show current sync status and dashboard overview')
  .action(async () => {
    const state = await getDashboardState();
    printStatus(state);
  });
```

The dashboard provides:
1. **Comprehensive Overview**: All key information at a glance
2. **Multiple Access Methods**: CLI, TUI, and API
3. **Automation + Manual Control**: Scheduled & on-demand sync
4. **Monitoring & Alerts**: Health checks and notifications
5. **Backward Compatibility**: Existing sync modes still work
6. **Scalable Architecture**: Easy to extend with new features

## Manual Sync Trigger (Updated)
The dashboard should support manual sync runs through:
- **CLI Interface**: `$ bun run sync --manual` (or `--force` flags)
- **Event-Driven Triggers**: Watch for changes in `~/.hermes/auth.json` and auto-sync
- **Cron Integration**: Hourly/daily scheduled sync jobs with optional notification

## Report Generation (Sample)
```markdown
# Daily Credential Sync Report - 2026-07-24

## Summary
- Total keys: 56
- New keys today: 0
- Errors: 0
- Success rate: 100%

## Provider Activity
| Provider | Keys | New Today | Errors |
|----------|------|-----------|--------|
| OpenCode  | 11   | 0         | 0      |
| Gemini   | 8    | 0         | 0      |
| ...       | ...  | ...       | ...    |

## Source Status
| Source | Status | Last Attempt |
|--------|--------|--------------|
| .hermes/auth.json | ✅ | 2026-07-24T12:41:50 |
| ... | ... | ... |
```