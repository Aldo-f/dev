---
name: hermes-home-backup
category: devops
description: "Use when backing up or restoring Hermes home (~/.hermes)."
tags:
  - hermes
  - backup
  - restore
  - skills
  - disaster-recovery
  - github
  - cron
trigger: Use when backing up/restoring ~/.hermes (skills, config, memories, sessions) after reinstall, migration, or disk failure.
---
# Hermes Home Backup & Restore

Covers `~/.hermes` — the user-owned Hermes state: config.yaml, custom skills, memories, cron jobs, sessions, auth. The hermes-agent codebase is NOT included (reinstalled separately).

## What lives in ~/.hermes (loss risk)

| Path | Contents | Recoverable without backup? |
|---|---|---|
| `skills/` | custom + hub skills (this box: ~9 MB, 600+ files) | hub skills reinstall via `hermes skills install`; **custom skills lost** |
| `config.yaml` (+ `.bak.*`) | settings, providers, custom_providers | lost |
| `memories/`, user profile | memory store | lost |
| `cron/` | scheduled jobs | lost |
| `sessions/`, `state.db` | conversation history | lost |
| `.env`, `auth.json` | secrets | lost — and must NEVER go into git |

## Two-layer backup scheme (as deployed on the Pi 5)

1. **Skills → private GitHub repo** `Aldo-f/hermes-skills`, daily auto-commit via cron. Skills contain no secrets, so version control is safe. First push: `git init -b main` in `~/.hermes/skills` (gitignore: `*.lock`, `.usage.json.lock`), then `gh repo create hermes-skills --private --source . --push`.
2. **Full zip → local `~/backups/`**, weekly via `hermes backup`. The zip contains `.env`/auth secrets → stays local, never pushed off-box.

Cron entry (03:30 — between the SSD health check 03:00 and git_push 04:00):
```
30 3 * * * /home/aldo/scripts/hermes_backup.sh >> /home/aldo/scripts/cron.log 2>&1
```
Script: `scripts/hermes_backup.sh` in this skill; installed copy at `/home/aldo/scripts/hermes_backup.sh`. It is quiet (empty output, exit 0) when nothing changed; any output = action taken, non-zero exit = real failure.

## Restore after total loss (fresh Pi / reinstall)

1. Install hermes-agent + `hermes setup`.
2. Restore skills: `git clone git@github.com:Aldo-f/hermes-skills.git` → copy contents into `~/.hermes/skills/` (or `hermes skills tap <repo>`).
3. Restore the rest: `hermes import ~/backups/hermes-backup-<date>.zip`. If the whole disk died and no off-box copy exists, only the skills repo survives — warn the user about that gap and offer off-box zip sync (e.g. rsync to their Fedora box).
4. Verify: `hermes skills list`, `crontab -l` (jobs restored), spot-check config/memories.

## Built-in commands

```bash
hermes backup              # full zip → ~/hermes-backup-<timestamp>.zip (config, skills, sessions, data; excludes hermes-agent codebase)
hermes backup -o out.zip   # custom path
hermes backup --quick      # critical state only (config, state.db, .env, auth, cron)
hermes import backup.zip   # restore
```

## Pitfalls

- **`hermes sync` is inert without a Nous Portal login** (`hermes sync status` → `logged_in: false`). Do not rely on cloud skill-sync for this user.
- The backup zip contains `.env` secrets → keep local, or encrypt before moving off-box.
- Bundled skills re-seed automatically when hermes-agent installs; hub skills need `hermes skills install` again. Only **custom** skills are unique — those are the ones the git repo protects.
- After restore, check `hermes skills list-modified` — bundled skills the user edited are preserved by `hermes update` and may differ from stock.
- Global git identity is a placeholder (`assistant@example.com`); set repo-local `user.name`/`user.email` (noreply: `<gh-user-id>+<user>@users.noreply.github.com`) instead of touching global config.
- `hermes backup` may warn about skipped files (e.g. missing `webui/models_cache.json`) — harmless; verify content with `unzip -l`.

## Verification checklist

```bash
cd ~/.hermes/skills && git status --porcelain   # empty after backup push
ls -lt ~/backups/                                # newest weekly zip present
unzip -l <zip> | grep -c "SKILL.md"             # sanity: skills inside the zip
```
