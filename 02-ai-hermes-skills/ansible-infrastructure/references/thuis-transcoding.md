# thuis-v4 Transcoding Feature (2026-08-09)

## Overview

Implemented flexible transcoding in thuis-v4 with CLI arguments and smart source selection.

## New CLI Arguments

```bash
--transcode TARGET       Target resolution (e.g., '720p', '1080p')
--allow-upscale          Allow upscaling (540p → 720p)
--keep-original          Keep both original and transcoded versions
--transcode-preset       FFmpeg preset (default: fast)
--transcode-crf          Quality 0-51 (default: 23)
```

## Key Features

### 1. Flexible Target Resolution
- `--transcode 720p` or `--transcode 1080p`
- Parses via `parse_target_height()` → extracts numeric height

### 2. Upscaling Support
- `--allow-upscale` enables 540p → 720p conversion
- Default: no upscaling (only downscale)

### 3. Smart Source Selection
When multiple resolutions exist (1080p + 540p), picks **highest available** for downscaling:
- 1080p → 720p (preferred over 540p → 720p)
- 540p → 720p (only with `--allow-upscale`)

**Algorithm** (`find_best_source_for_transcoding`):
1. Filter files with resolution > target (downscale candidates)
2. Return the one closest to target
3. If none higher, return highest available (for upscale)

### 4. Related File Detection
`find_related_files(dir, base_name)` finds same episode at different resolutions (e.g., S01E01 in 1080p and 540p).

## Module: `src/thuis/transcoder.py`

| Function | Purpose |
|----------|---------|
| `parse_target_height()` | '720p' → 720 |
| `should_transcode(path, target, allow_upscale)` | Decision logic |
| `find_best_source_for_transcoding(files, target)` | Prefers highest > target |
| `find_related_files(dir, base_name)` | Finds same episode diff resolutions |
| `transcode_file_if_needed()` | Main entry point |
| `transcode_to_target()` | FFmpeg execution |

## FFmpeg Command (720p target)

```bash
ffmpeg -y -i input.mp4 \
  -vf "scale=1280:720" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a copy -movflags +faststart \
  output_720p.mp4
```

## Usage Examples

```bash
# Downscale 1080p to 720p
python -m thuis.main --transcode 720p "URL"

# Allow upscaling 540p to 720p
python -m thuis.main --transcode 720p --allow-upscale "URL"

# Keep both versions
python -m thuis.main --transcode 720p --keep-original "URL"

# Custom quality
python -m thuis.main --transcode 1080p --transcode-preset medium --transcode-crf 20 "URL"
```

## Test Results

- ✅ All 196 existing tests pass
- ✅ Transcoder module functions verified
- ✅ CLI arguments available and working
- ✅ FFmpeg integration working (tested 1080p → 720p conversion)

## Behavior Table

| Source Resolution | `--transcode 720p` | `--transcode 720p --allow-upscale` |
|-------------------|---------------------|-----------------------------------|
| 1080p, 1440p, 2160p | ✅ Downscale to 720p | ✅ Downscale to 720p |
| 720p | ❌ Already at target | ❌ Already at target |
| 540p, 480p | ❌ Below target | ✅ Upscale to 720p |