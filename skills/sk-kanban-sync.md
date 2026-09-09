---
name: kanban-sync
category: devops
description: Sync Hermes Kanban tasks to Nocturna SQLite DB.
---

# Kanban Sync — Hermes to Nocturna

Used when Nocturna's DB needs to reflect Hermes Kanban board tasks (e.g., `toolbox-test`).

## When to Use
- `hermes kanban --board toolbox-test list --json` returns tasks but Nocturna `data/nocturna.db` has no `tasks` table or empty results.
- After creating test tasks on Hermes TQ board and verifying with `hermes kanban boards`.

## Always-On Rules

- **Verify sync output before claiming success.** Run `sqlite3 data/nocturna.db "SELECT id, title, status FROM tasks"` after sync. Must show tasks.
- **Never claim working without real DB verification.** Do not trust script exit code alone — check DB contents.
- **No `||` masking in CLI commands.** Always run `hermes version` directly; check `exitCode` explicitly (see `nocturna-spec-kit-bootstrap` pitfall on CLI masking).
- **Python sync script uses `python3 -c` inline** but writes to a file if persistence needed (`/tmp/do_sync.py` or `scripts/sync-kanban.js`).

## Procedure

1. Verify Hermes board has tasks: `hermes kanban --board toolbox-test list --json`
2. Check Nocturna DB schema: `sqlite3 data/nocturna.db ".schema"`
3. Create `tasks` table if missing (see reference file).
4. Execute sync (inline Python or script): reads Hermes JSON, inserts missing rows into `data/nocturna.db`.
5. Verify inserted count matches Hermes count: `SELECT COUNT(*) FROM tasks`.
6. Confirm each task's `status` matches Hermes (`done`, `blocked`, `ready`).

## Pitfalls

- **No `tasks` table in Nocturna DB.** The DB only has `users`, `sessions`, `instances`, `user_preferences`. Must `CREATE TABLE IF NOT EXISTS tasks (...)` before sync.
- **Binary `data/nocturna.db` conflicts during git pull/rebase.** Resolve by aborting rebase (`git rebase --abort`), committing sync changes, then pulling with `--rebase` after resolving file-level conflicts manually.
- **Sync script syntax errors.** Verify with `node --check` or `python3 -m py_compile` before running.
