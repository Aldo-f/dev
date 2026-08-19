# Deezer CLI — Configurable Paths Pattern (Reference)

## Applied In This Project
- `scripts/deezer.py`: Lines 52-59 (dotenv loading), Line 67 (MUSIC_SEED constant)
- `~/.config/deezer/.env`: User's Nextcloud path
- Tested: 41 tracks downloaded to configured path, Nextcloud scan verified

## Key Lines in deezer.py
```python
# Load optional .env config (ARL and custom paths)
DOTENV_PATH = os.path.expanduser("~/.config/deezer/.env")
if os.path.isfile(DOTENV_PATH):
    for line in open(DOTENV_PATH):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"\'')

# Default music seed directory - can be overridden via DEEZER_MUSIC_SEED env var or .env
MUSIC_SEED = os.path.expanduser(os.environ.get("DEEZER_MUSIC_SEED", "~/Music/Deezer"))

# CLI argument with constant as default
sp.add_argument("--out", default=MUSIC_SEED)
```

## User Config
```bash
# ~/.config/deezer/.env
DEEZER_MUSIC_SEED="/mnt/HDD1/nextcloud/data/aldo/files/Media/music"
```

**⚠️ Case sensitivity matters!** The user's Nextcloud directory structure uses `Media/music` (uppercase M), not `media/music` (lowercase). Using the wrong case will create a non-existent directory and cause permission errors.

## Test Verification
```bash
# Test env var override
DEEZER_MUSIC_SEED="/tmp/test" ~/.venvs/deezer/bin/python ~/scripts/deezer/scripts/deezer.py download-playlist "https://www.deezer.com/playlist/..." --limit 1

# Test CLI override
~/.venvs/deezer/bin/python ~/scripts/deezer/scripts/deezer.py download-playlist "..." --out /custom/path
```