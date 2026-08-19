# Recovering a lost/overwritten .env (gitignored secrets)

Scenario: a gitignored `.env` disappears during a git pull / reset / clean.
Forensics first: a plain `git pull` CANNOT delete untracked files — something
destructive ran (`git reset --hard`, `git clean -fdx`, or a manual rm). Check
`git reflog` for the command sequence before blaming the pull; verify `.env` was
never tracked (`git log --all --oneline -- .env` empty + `.gitignore` entry).

## Recovery sources (in order of reliability)

1. **Running container env** — the best snapshot when docker-compose uses
   `env_file: .env`: the container was started with exactly those values.
   ```bash
   docker inspect <container> --format '{{json .Config.Env}}' | python3 -m json.tool
   ```
   Cross-check against the compose `environment:` block to separate hardcoded
   vars from `.env`-sourced ones, then validate with `docker compose config`
   (resolved values). If the container is still healthy with matching values,
   no restart is needed after recreating `.env`.
2. **Ansible vault** (if integrated) — decrypt and re-render via the render task.
3. **Backup copies** — after any recovery, save to `~/backups/env/<app>.env`
   (chmod 600). Cheap insurance; restore with `cp`.

## Critical secret: ENCRYPTION_KEY
Apps like FreeLLMAPI encrypt stored API keys in SQLite with ENCRYPTION_KEY; the
DB lives in a docker volume (survives repo wipes). Losing the key = losing the
stored keys. The container env is the recovery source — grab it before any
container recreation.

## Validation after recreate
- `docker compose config --quiet` parses
- `docker compose config` shows resolved host_ip/port as before
- container still `healthy`; `docker inspect` env matches the new `.env`

## gitignore negation pitfalls (making a `*.env.j2` template committable)
- Broad rules (`02-*/` sibling-dir patterns, `.env.*`) shadow template files.
- To negate a file under an EXCLUDED DIRECTORY, re-include the directory itself
  first, then the file: `!dir/` + `!dir/file`.
- Nested `.gitignore` files win over the repo-root one — add the exception at
  the deepest level that shadows the path.
- `git check-ignore -v` output is ambiguous for negation rules (prints the `!`
  pattern as the last match). Definitive test: `git add --dry-run <path>`.