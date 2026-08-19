---
name: deezer
description: Use when the user wants to download Deezer music as MP3.
---

# Deezer — Download & search tracks/playlists/albums/artists/flow as MP3

Use/search Deezer tracks using a personal **ARL cookie** (from your logged-in Deezer browser session). Adapted from the OVOS/Mycroft `deezer-skill` into a standalone Python CLI that runs natively under Hermes.

## When to use
- "Download this Deezer track", "get <song> off Deezer", "fetch my Deezer playlist <name>", "download my Deezer Flow".

## Prerequisites
- Your **Deezer ARL cookie** value (logged-in browser → DevTools → Cookies → `arl`).
- Python 3.13 with venv support (already on this host).
- The `py-deezer` 1.1.2 (Chr1st-oo) package. **NOT** PyPI `pydeezer` (rcrdclub) — a different API-key client with no `Deezer` class.

## Setup (one-time)
```bash
python3 -m venv ~/.venvs/deezer
~/.venvs/deezer/bin/pip install -q "py-deezer==1.1.2" mutagen requests pytest cryptography
mkdir -p ~/.config/deezer
echo 'DEEZER_ARL="<YOUR_ARL>"' > ~/.config/deezer/arl.sh
```

**Optional: configure download directory** via `~/.config/deezer/.env`:
```bash
DEEZER_MUSIC_SEED="/mnt/HDD1/nextcloud/data/aldo/files/media/music"
```
Default: `~/Music/Deezer` (falls back to home directory if not set).

Store the ARL in `~/.config/deezer/arl.sh` as `DEEZER_ARL="..."`, or export `DEEZER_ARL` yourself. Do **not** hard-code it in the skill script.

## Usage
The executable lives at `~/scripts/deezer/scripts/deezer.py` (this skill checks out the `Aldo-f/deezer` repo as a git submodule of `~/scripts`).

### CLI Commands

| Command | Purpose |
|---------|---------|
| `search "query" [--limit N]` | Search tracks. |
| `playlist <id_or_url>` | List tracks in a playlist. |
| `artist <id_or_url>` | List top tracks for an artist. |
| `download <target_list> [--out DIR] [--limit N] [--quality Q] [--workers N]` | Smart downloader (comma-separated URLs or IDs; auto-detects track/album/playlist/artist/flow). |
| `download-track <target_list>` | Explicitly download track(s). |
| `download-album <target_list>` | Explicitly download album(s). |
| `download-playlist <target_list>` | Explicitly download playlist(s). |
| `download-artist <target_list>` | Explicitly download artist top-tracks. |
| `download-flow [--out DIR] [--limit N] [--quality Q]` | Download your personalized Deezer Flow (requires ARL). |
| `whoami` | Print the Deezer account name for the ARL. |

### Environment
`DEEZER_ARL` env var, or creds file `~/.config/deezer/arl.sh` (sourced by script). Override with `--arl ARL`.

### Examples
```bash
~/scripts/deezer/scripts/deezer.py search "Daft Punk Discovery"

# Smart download an album and a track together
~/scripts/deezer/scripts/deezer.py download "3135556,https://www.deezer.com/en/album/398684"

# Smart download a playlist
~/scripts/deezer/scripts/deezer.py download "https://www.deezer.com/en/playlist/12575278323"

# Download your personalized Flow
~/scripts/deezer/scripts/deezer.py download-flow --limit 50

# Parallel downloads with 4 workers
~/scripts/deezer/scripts/deezer.py download "https://www.deezer.com/en/playlist/12575278323" --workers 4
```

## Features

- **Flat directory structure**: No messy per-track folders. Everything goes directly into your target directory.
- **Human-readable naming**: Files are saved strictly as `<Artist> - <Title>.mp3` with clean characters.
- **Complete ID3 tags**: Embeds Title, Artist, Album, Album Artist, Track/Disc numbers, Year, Genre, ISRC, Label, Copyright, Composer, BPM, and high-quality Cover Art.
- **Lyrics embedding**: Automatically fetches Deezer lyrics and embeds them as ID3 `USLT` tags.
- **Idempotent duplicate prevention**: Automatically detects and skips existing files (`SKIP`), preventing useless downloads or ` (2)` name collisions.
- **Quality fallback**: If a track fails with a rights error at the requested quality (e.g., `MP3_320`), automatically retries with `MP3_128`.
- **Parallel downloads**: Use `--workers N` to download multiple tracks in parallel for faster downloads.
- **M3U playlist generation**: Automatically creates `.m3u` files after downloading playlists, albums, artists, or Flow.

## Pitfalls
- **Package name**: install the package literally named **`py-deezer`** (hyphen) from Chr1st-oo. `pydeezer` (no hyphen) is the rcrdclub OAuth client — fails with `ImportError: cannot import name 'Deezer'`, and rcrdclub 1.0.8 also breaks on Python 3.13 (`from urllib import urlencode`).
- **Credentials**: treat the ARL as a secret; keep out of repos and shell history.
- **Downloads work via the new tokenized media API** (since Deezer retired the `e-cdns-proxy-*.dzcdn.net` CDN in Feb 2025). The script uses `license_token` + per-track `TRACK_TOKEN`, then POSTs to `media.deezer.com/v1/get_url` to get a stream URL on `cdnt-stream.dzcdn.net`, then Blowfish-decrypts (BF_CBC_STRIPE) into a valid MP3. This is fully verified on modern Python.
- **Bitrate limit**: a free-tier ARL can only get **MP3_128** (`--quality MP3_128`, default). Requesting `MP3_320` fails with `errors[0].code 1002 "License token has no sufficient rights"` unless the account has a premium/subscription tier. The script automatically falls back to `MP3_128` in this case.
- **Flow access**: Requires a valid ARL and Deezer account with Flow access.

## Verification
After a download, confirm a real `.mp3` exists (`ls -la OUT_DIR`) with a non-trivial size. Deezer can intermittently fail per-track — check per-track errors, not just exit code.

## Credits
Adapted from [Y0ngg4n/deezer-skill](https://github.com/Y0ngg4n/deezer-skill). Uses [Chr1st-oo/pydeezer](https://github.com/Chr1st-oo/pydeezer) (GPLv3).
