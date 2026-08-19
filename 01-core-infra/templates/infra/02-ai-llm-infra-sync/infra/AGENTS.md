# AGENTS.md

## Purpose

This repository is a credential sync engine for a local LLM infrastructure. The goal is to keep provider credentials in sync across several local sources and expose sync/status/dashboard access.

## Key entrypoints

- `src/index.ts`
  - Primary sync logic.
  - Reads credentials from multiple local sources and merges them into a unified per-provider pool.
  - Writes merged credentials back to the existing sources while preserving each source's structure.
  - Supports JSON, YAML, and `.env` input formats.

- `src/cli.ts`
  - CLI wrapper for the sync engine.
  - Parses `--mode` and supports at least `sync` and `status`.
  - Delegates `sync` to `src/index.ts` and uses the same local sources for `status`.

- `src/server.ts`
  - HTTP API server on port `3003`.
  - Exposes `/sync`, `/status`, `/dashboard`, `/api/key`, `/api/free-keys`.
  - Uses `hono` and `bun serve`.

- `src/dashboard.tsx`
  - Ink-based TUI dashboard that reads `credential-pool.json`.

## Important files and directories

- `credential-pool.json`
  - Central credential pool / source of truth.
  - Used by the dashboard and server.

- `src/readers/`
  - `json-reader.ts`
  - `yaml-reader.ts`
  - `env-reader.ts`
  - Format-specific reader logic.

- `src/writers/`
  - `json-writer.ts`
  - `yaml-writer.ts`
  - `env-writer.ts`
  - Format-specific writer logic.

- `key-generator/server.js`
  - A Node-based key generator server separate from the main Bun/TS workflow.

- `test/`
  - Contains tests for credential pool and sync behavior.

## Execution and development commands

Use the repository `package.json` scripts as the primary commands.

- `bun run src/index.ts` — run the sync engine directly.
- `bun run src/cli.ts` — run the CLI wrapper.
- `bun run src/cli.ts -- -m status` — show credential counts from available sources.
- `bun run src/dashboard.tsx` — launch the Ink dashboard.
- `bun run src/server.ts` — start the HTTP API server.
- `node key-generator/server.js` — start the key generator server.

## Conventions

- The repository is ESM-only (`type: module` in `package.json`).
- Source imports use `.js` extensions for local modules, even though the files are TypeScript.
- Credential sources are read from absolute user-local paths under `process.env.HOME`.
- The sync engine is designed to merge provider credential arrays without destroying existing metadata.
- Avoid exposing or logging actual credential values.

## Agent guidance

When editing or extending this repository:

- Preserve source file structure when writing back to existing credential files.
- Prefer reuse of the existing reader/writer abstraction.
- Keep sync behavior idempotent and metadata-safe.
- If adding new source formats, add corresponding reader/writer modules and update `src/index.ts` and `src/cli.ts` accordingly.
- If changing runtime behavior, verify with the local `status` and `dashboard` flows.

## Notes

- There is no `README.md` or other project documentation in this repo beyond `PLAN.md` and the source files.
- `PLAN.md` contains architecture notes and target workflows, but it is not executable documentation.
