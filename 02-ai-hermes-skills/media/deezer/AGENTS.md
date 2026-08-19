# Deezer Skill — Agent Guidance

This skill provides Deezer music download and search capabilities for Hermes.

## When to Use
- User wants to download Deezer tracks, albums, playlists, or artist top-tracks
- User wants to download their personalized Deezer Flow
- User wants to search for Deezer tracks
- User needs to list tracks in a playlist or from an artist

## Commands

### Search
```bash
~/scripts/deezer/scripts/deezer.py search "query" [--limit N]
```

### Smart Download (auto-detects resource type)
```bash
~/scripts/deezer/scripts/deezer.py download <URL_or_ID[,URL_or_ID,...]> [--out DIR] [--limit N] [--quality MP3_128|MP3_320] [--workers N]
```
Examples:
- `deezer.py download 3135556` — download a track by ID
- `deezer.py download https://www.deezer.com/en/album/398684` — download an album
- `deezer.py download https://www.deezer.com/en/playlist/12575278323` — download a playlist
- `deezer.py download https://www.deezer.com/en/artist/1188009` — download artist top tracks
- `deezer.py download "3135556,78527813"` — download multiple tracks

### Explicit Download Commands
```bash
~/scripts/deezer/scripts/deezer.py download-track <target_list> [--out DIR] [--quality Q]
~/scripts/deezer/scripts/deezer.py download-album <target_list> [--out DIR] [--limit N] [--quality Q]
~/scripts/deezer/scripts/deezer.py download-playlist <target_list> [--out DIR] [--limit N] [--quality Q]
~/scripts/deezer/scripts/deezer.py download-artist <target_list> [--out DIR] [--limit N] [--quality Q]
~/scripts/deezer/scripts/deezer.py download-flow [--out DIR] [--limit N] [--quality Q]
```

### Metadata Commands
```bash
~/scripts/deezer/scripts/deezer.py playlist <id_or_url> [--limit N]
~/scripts/deezer/scripts/deezer.py artist <id_or_url> [--limit N]
~/scripts/deezer/scripts/deezer.py whoami [--arl ARL]
```

## Features
- **Flat directory structure**: Files go directly to target directory
- **Proper naming**: `<Artist> - <Title>.mp3`
- **Full ID3 metadata**: Title, Artist, Album, Genre, Year, ISRC, Cover Art
- **Lyrics embedding**: Auto-fetches and embeds Deezer lyrics
- **Quality fallback**: Auto-downgrades from MP3_320 to MP3_128 on rights errors
- **Parallel downloads**: `--workers N` for faster downloads
- **M3U generation**: Auto-creates playlists for all batch downloads
- **Idempotent**: Skips already-downloaded tracks

## ARL Resolution Order
1. `--arl` flag
2. `DEEZER_ARL` environment variable
3. `~/.config/deezer/arl.sh` file

## Testing
```bash
cd ~/scripts/deezer
~/.venvs/deezer/bin/python -m pytest
```

## Default Output Directory
`~/Music/Deezer` (configurable via `DEEZER_MUSIC_SEED` env var or `~/.config/deezer/.env`)

## Notes
- Requires valid Deezer ARL cookie
- Free-tier ARLs limited to MP3_128 (MP3_320 requires premium)
- Flow requires Deezer subscription with Flow access
- All downloads are individual track downloads with proper metadata tagging
