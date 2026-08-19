# Worked example: importing & packaging the `deezer` skill

How an existing voice-assistant skill was imported, adapted, and packaged the
way Aldo likes. Run through on 2026-08-02.

## Source
`https://github.com/Y0ngg4n/deezer-skill` is an **OVOS/Mycroft voice skill**
(Python `CommonPlaySkill` subclasses, intent handlers, `.regex`/`.dialog`
locale files, 42MB vendored Python 3.8 venv) — not a native Hermes skill. The
only reusable core is `deezer_utils.py`: `search_first_track`,
`search_first_playlist`, `download_track`, `login`, using the `py-deezer` lib.

## Adaptation
Dropped the Mycroft wrapper and vendored venv. Kept just the utility logic and
wrapped it in a small `argparse` CLI (`deezer.py`) with commands: `search`,
`download <id>`, `playlist`, `download-playlist`, `whoami`. ARL resolution:
`--arl` flag → `DEEZER_ARL` env → `~/.config/deezer/arl.sh`.

## PYTHON 3.13 DEPENDENCY TRAP (important)
The upstream `requirements.txt` pinned `py-deezer`, **but**:
- PyPI package `pydeezer` (no hyphen, rcrdclub, v1.0.8) is a **different** OAuth
  client — `from pydeezer import Deezer` fails with
  `ImportError: cannot import name 'Deezer'`. It also breaks on Python 3.13 with
  Python-2 style `from urllib import urlencode`.
- The working one is the PyPI package literally named **`py-deezer`** (hyphen,
  Chr1st-oo, v1.1.2). Verified import on Python 3.13.5.
- Lesson: when importing an adapted skill, pip-install + import-test in a
  throwaway venv (`python3 -m venv /tmp/x && /tmp/x/bin/pip install ...`) BEFORE
  committing to the dependency. The skill author's `requirements.txt` cannot be
  trusted verbatim.

Deployed venv here: `~/.venvs/deezer` with `py-deezer==1.1.2` + `mutagen`.

## Packaging (the 3-part convention)
1. Authoring copy `~/dev/deezer` → `gh repo create Aldo-f/deezer --public --source=. --remote=origin --push` (commit `3d09314`).
2. Submodule added to `~/scripts` → `git submodule add git@github.com:Aldo-f/deezer.git deezer`; committed + pushed (`6eceacc`); removed the redundant `~/dev/deezer` authoring copy.
3. Hermes skill `media/deezer` trimmed to **SKILL.md only**; `scripts/` removed; SKILL points at `~/scripts/deezer/scripts/deezer.py`.

## Resulting layout
- `github.com/Aldo-f/deezer` (public) — README, requirements, .gitignore, scripts/
- `~/scripts/deezer` — submodule checkout (canonical, executable)
- `~/.hermes/skills/media/deezer/SKILL.md` (symlinked to `~/dev/02-ai-hermes-skills`)

## Nothing filled in yet
ARL validation + live playlist download were left for the user (private
credential). Repo setup, submodule, venv install all verified working.