---
name: hermes-script-skill-packaging
description: Use when packaging a runnable script as a Hermes skill.
---

# Packaging a runnable script as a Hermes skill (Aldo's convention)

Aldo's preferred architecture for turning a standalone/executable script into a
reusable Hermes skill is a 3-part split that keeps generated/runnable artifacts
out of the skills tree:

1. **Runnable code → its own GitHub repo** (created/pushed via `gh`).
2. **Repo → git submodule of `~/scripts`** (`~/scripts/<name>`), the canonical checkout.
3. **Skill → SKILL.md only** in the Hermes skills dir, pointing at `~/scripts/<name>`.

This is the pattern used for the `deezer` skill (this umbrella's reference
file documents that concrete case end-to-end).

## Why this shape
- `~/.hermes/skills` is a **symlink** to the versioned skills repo
  `~/dev/02-ai-hermes-skills` — so anything committed there is tracked along with
  other skills, and code you keep editing should not bloat it.
- Runable code stays versioned independently (own repo) and is installable
  anywhere via the submodule URL (`git@github.com:Aldo-f/<name>.git`).
- The skill itself stays lean: just `SKILL.md` (instructions), no vendored code.

## Workflow

```bash
# 1. Create the standalone repo (authoring copy)
REPO=~/dev/<name>; rm -rf "$REPO"; mkdir -p "$REPO/scripts"; cd "$REPO"; git init -q -b main
git config user.name  "Aldo"
git config user.email "aldo-f@users.noreply.github.com"
cp <your scripts> "$REPO/scripts/"; chmod +x "$REPO/scripts/main.py"
# write README.md, requirements.txt, .gitignore (exclude __pycache__/venv/*.mp3)
git add -A && git commit -m "Initial ..."
gh repo create Aldo-f/<name> --public --source=. --remote=origin --push
```

```bash
# 2. Add as submodule of ~/scripts (records git@ URL so it works on any machine)
cd ~/scripts
git submodule add git@github.com:Aldo-f/<name>.git <name>
git add .gitmodules <name> && git commit -m "Add <name> submodule" && git push origin
```

```bash
# 3. Point the Hermes skill at the checkout; keep only SKILL.md in the skills dir
#    (mkdir ~/.hermes/skills/<category>/<name>/; write SKILL.md; then rm -rf the scripts/ copy)
# SKILL.md references: ~/scripts/<name>/scripts/<name>.py
```

## Testing & verification (Aldo requires this — skip at your peril)

Aldo repeatedly rejects work that was only verified under a non-default runtime
or claimed done without evidence. Before you report a packaged script as
working:

1. **Make plain `python3 <script>` (direct invocation) work, not just the venv
   interpreter.** If a script owns/needs a venv (e.g. `~/.venvs/<name>`), add a
   venv bootstrap at the top that re-execs the script inside the venv when the
   bare python3 lacks the dependency. If someone hits
   `ModuleNotFoundError: <dep>`, that bootstrap is broken under the real runtime
   — fix the script, don't assume a missing install. The failure the user eyes a
   `python3`-invoked CLI, not the interpreter you happened to test with.
2. **Ship hermetic unit tests** (`tests/test_<name>.py` + `pytest.ini` with
   `pythonpath = scripts tests`, `testpaths = tests`). Mock all external network
   so the suite runs offline with no credentials. Cover the logic you own: input
   parsing, the auth/token payload, any crypto/decrypt round-trip, and output
   naming/structure. Run `~/.venvs/<name>/bin/python -m pytest` and report a
   number of tests passing.
3. **Make downloads/commands idempotent** — `skip_existing` on by default:
   compute the target path *before* any network call, raise a specific
   `AlreadyDownloadedError` when the file exists, and have the CLI print
   `SKIP <path>` (and tally skipped counts) instead of re-downloading or
   creating `name (2).mp3` duplicates. Users re-run download commands; they want
   no-op re-runs, not copy after copy.
4. **Verify against the real runtime end-to-end** before claiming done: run the
   actual command (e.g. a real download) and inspect/`file`-check the artifact,
   plus re-run once to confirm skip behavior. Show this evidence in the report,
   not just "I ran it and it worked."
5. Keep a `.env.example` (or `.env`) the script can load for paths, and validate
   any CLI `--limit` type so out-of-range values (like `0`) are rejected, not
   silently producing duplicates.

## Pitfalls
- **Use `gh repo create ... --source . --push`** to push the local repo in one
  step; it also sets `origin` + upstream tracking.
- **Use a per-repo git identity** (`Aldo / aldo-f@users.noreply.github.com`), not
  the shared `Everyone / everyone@familytodo.com` from `~/scripts`, for personal
  projects.
- In `~/scripts`, **stage only your own files** when committing — Aldo keeps other
  untracked WIP there (`hermes_backup.sh`, `trigger-both.sh`, etc.).
- After moving the canonical script out of the skill dir, remove the skill's
  now-stale `scripts/` copy so there's exactly one source of truth.
- `skill_manage` **frontmatter `description` must be ≤60 chars** (else `create` is
  rejected; it truncates to 57 for the index). Keep it a single sentence, trigger
  first, ends with a period.
- Validate an imported/adapted skill's real dependency before wiring it: e.g. the
  upstream Deezer repo's `requirements.txt` said `py-deezer`, but PyPI `pydeezer`
  (no hyphen) is a different OAuth client that breaks on Python 3.13 — the working
  one is `py-deezer==1.1.2` (Chr1st-oo). Always pip-install + import-test in a
  throwaway venv before committing to a dependency.

## Reference
- `references/deezer-case.md` — worked end-to-end example (importing an OVOS
  voice skill, the packaging steps above, and the Python 3.13 `py-deezer` trap).
- `references/deezer-download-internals.md` — the current Deezer download
  mechanics (tokenized `media.deezer.com/v1/get_url` flow, cookie-domain fix,
  Blowfish-CBC strip decrypt, bitrate/rights limits, and the output contract:
  flat structure, skip-existing idempotency, full ID3 metadata). Consult when
  touching the `deezer` executable or solving any "download from a proprietary
  streaming API" task.
- `references/mail-tm-tool-case.md` — mail.tm API tooling example demonstrating
  config.yaml/.env separation, cumulative deletion tracking, and automated
  stats persistence to JSON. Useful for scripts that manage external API
  resources with quota limits.