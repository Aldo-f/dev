---
name: configurable-paths-pattern
description: Use when scripts need configurable paths via .env/env/CLI.
---

# Configurable Paths Pattern — `.env` + CLI + Env Var Fallback

## Problem
Scripts with hardcoded absolute paths break when used by other users or environments.

## Solution: Layered Configuration Priority
1. **CLI `--out` argument** — explicit per-run override
2. **Environment variable** — `DEEZER_MUSIC_SEED`, `APP_OUTPUT_DIR`
3. **Config file** — `~/.config/<app>/.env` with `KEY="/path"`
4. **Hardcoded default** — safe fallback (e.g., `~/Music/Deezer`)

## Implementation
```python
# Load .env early
DOTENV_PATH = os.path.expanduser("~/.config/<app>/.env")
if os.path.isfile(DOTENV_PATH):
    for line in open(DOTENV_PATH):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"\'')

# Constant with env fallback
OUTPUT_DIR = os.path.expanduser(os.environ.get("APP_OUTPUT_DIR", "~/Default/Path"))

# CLI arg with constant default
parser.add_argument("--out", default=OUTPUT_DIR)
```

## User Config
```bash
APP_OUTPUT_DIR="/mnt/storage/user/files"
```

## Testing Checklist
- [ ] CLI override: `--out /custom/path`
- [ ] Env var: `APP_OUTPUT_DIR=/tmp python script.py`
- [ ] `.env` file: echo '...' > ~/.config/app/.env
- [ ] Default fallback works
- [ ] **Case sensitivity**: Verify exact path case on Linux filesystems (e.g., `Media/` vs `media/`)

## Applied In
- Deezer CLI: `DEEZER_MUSIC_SEED` → `~/Music/Deezer` default