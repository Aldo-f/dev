---
name: thuis-v4-transcoding
description: "Batch video transcoding to 720p with FFmpeg."
tags: [thuis, transcoding, ffmpeg, batch]
---

# thuis-v4 Transcoding

Use when transcoding video files to 720p with the thuis-v4 tool.

## Overview

The `thuis-v4` project (`~/dev/06-apps-thuis-v4`) includes FFmpeg-based transcoding for:
- Post-download transcoding (auto-convert after yt-dlp download)
- Batch transcoding of existing media libraries

## CLI Usage

```bash
# Transcode downloaded files to 720p
python -m thuis.main --transcode 720p "URL"

# Batch transcode existing files
python -m thuis.main --input-dir /path/to/media \
    --transcode 720p \
    --filter "kampioenen" \
    --allow-upscale \
    --keep-original \
    --recursive \
    --parallel 2 \
    --dry-run  # Preview first

# Higher quality (lower CRF = better)
python -m thuis.main --transcode 720p --transcode-crf 18 --transcode-preset medium
```

## Key Features

| Feature | Flag | Description |
|---------|------|-------------|
| Target resolution | `--transcode 720p` | Downscale/upscale to target |
| Allow upscaling | `--allow-upscale` | Enable 540p → 720p |
| Keep original | `--keep-original` | Preserve both versions |
| Filter | `--filter "pattern"` | Substring match (case-insensitive) |
| Recursive | `--recursive` | Scan subdirectories |
| Parallel | `--parallel N` | Concurrent jobs |
| Dry run | `--dry-run` | Preview without executing |

## Decision Logic

| Source | Target | Action |
|--------|--------|--------|
| 1080p+ | 720p | Downscale (preferred) |
| 720p | 720p | Skip (already target) |
| 540p/480p | 720p | Upscale (if `--allow-upscale`) |

## Smart Source Selection

When multiple resolutions exist for same episode:
- Prefers **highest resolution** for downscaling (1080p → 720p)
- Only upscales with `--allow-upscale`

## Implementation

Files:
- `src/thuis/transcoder.py` - FFmpeg integration module
- `src/thuis/main.py` - CLI integration

## Quality Settings

| Preset | Use Case |
|--------|----------|
| fast | Default (good balance) |
| medium | Better quality |
| slow | Archival quality |

| CRF | Quality |
|-----|---------|
| 18-20 | Visually lossless |
| 23 | Default |
| 28-30 | Smaller files |

## Testing

All 196 existing tests pass. New functionality tested with:
- Resolution detection
- Batch scanning
- Filter matching
- Dry-run mode

## References

- Source: `~/dev/06-apps-thuis-v4/`
- Docs: `~/dev/06-apps-thuis-v4/README.md`
- Commit: `432a7d0` on `v4/main`
- Reference: `references/media-file-organization.md` (file organization pitfalls, verification patterns, backup verification)

## Pitfalls

### Directory Restructuring
When reorganizing media directories:
- Files are NOT automatically moved - they stay in original location
- Symlinks point from new location to old location
- **Always verify file existence** before assuming relocation

### Backup Verification
Always check what's in backups before relying on them:
```bash
unzip -l /home/aldo/backups/hermes-backup-*.zip | grep -E "\.mp4$|\.mkv$"
```
Expected: Backup contains ONLY JSON logs, NO video files