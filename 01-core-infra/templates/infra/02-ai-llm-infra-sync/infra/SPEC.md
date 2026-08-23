# Specification Kit

This specification captures the implementation intent from `PLAN.md` as a concise reference for development, validation, and review.

## Goal

Create a credential synchronization engine that acts as the single source of truth for provider credentials across local LLM infrastructure.

## Scope

- Read credentials from local source files in JSON, YAML, and `.env` formats.
- Merge credentials into a central pool with provider-based arrays.
- Write credential updates back to source files without destroying source-specific metadata.
- Provide CLI, status, dashboard, and HTTP API access to sync and monitor state.

## Central Pool

The central credential pool is stored in `credential-pool.json`.

Schema:

- `version`: string
- `last_sync`: timestamp
- `providers`: object keyed by provider name
  - each provider maps to an array of credential objects
- `sync_metadata`: summary data about sync state

Credential object fields:

- `id`
- `label`
- `auth_type`
- `value`
- `source`
- `metadata` (created, last_sync, etc.)

## Supported Sources

1. `~/.hermes/auth.json` — JSON source
2. `~/.config/opencode/auth.json` — JSON source
3. `~/dev/02-ai-omniroute/config.yaml` — YAML source
4. `~/dev/02-ai-freellm-api/.env` — ENV source
5. `~/dev/02-ai-freellmapi/keys/` — optional individual JSON key files

## Provider Mapping

Source formats must be normalized into `credential_pool` shape.

- `hermes` / `opencode` JSON: `credential_pool.{provider}[]`
- `omniroute` YAML: `providers.{provider}[]`
- `.env`: flat key/value pairs mapped to provider names
- `keys/` directory: optional individual key files by provider

## Operation Modes

The engine should support the following modes:

- `sync`: bidirectional full sync across sources and central pool
- `import`: read all sources into the central pool only
- `export`: write the central pool back to all sources only
- `verify`: read-only consistency check and issue report
- `status`: overview of current pool and source health
- `dashboard`: interactive visual summary

## Behavior Contract

- Merge per-provider credential arrays without losing existing metadata.
- Deduplicate credentials using stable fingerprints.
- Preserve source structure and non-credential fields when writing back.
- Treat source reads as tolerant and non-fatal; missing sources should not break the sync.
- Never log actual credential values.

## CLI and API

### CLI

Supported commands:

- `bun run src/index.ts`
- `bun run src/cli.ts -- -m sync`
- `bun run src/cli.ts -- -m status`
- `bun run src/cli.ts -- -m dashboard`

### HTTP API

Server exposes:

- `POST /sync`
- `GET /status`
- `GET /dashboard`
- `POST /api/key`
- `GET /api/free-keys`

## Dashboard Requirements

The dashboard should provide:

- Provider key count summary
- Source sync status
- Last sync timestamp
- Manual sync trigger support
- Health and warning indicators

Paths:

- TUI: `src/dashboard.tsx`
- HTTP dashboard: `/dashboard`

## Validation Criteria

- `credential-pool.json` reflects merged provider credential arrays
- Source files remain readable and preserve metadata after sync
- `.env` writer round-trips provider keys correctly
- Status mode reports available sources and counts
- Dashboard mode loads provider counts from the central pool

## Security and Reliability

- Do not print sensitive values in logs or API responses.
- Prefer file permission safety for credential outputs.
- Keep the sync process idempotent.
- Handle parse errors gracefully and continue with available sources.

## Implementation Notes

- Use reader modules for JSON, YAML, and env formats.
- Use writer modules for JSON, YAML, and env output.
- Keep local source imports using `.js` extensions for ESM compatibility.
- Use `process.env.HOME` for path resolution.
- If adding support for new source formats, add a reader/writer pair and register it in the sync pipeline.

## Future Enhancements

- `freellmapi-keys` directory support for per-provider JSON files.
- scheduled or watch-based automatic sync.
- richer sync history and reporting artifacts.
- verification and alerting on stale or missing sources.
