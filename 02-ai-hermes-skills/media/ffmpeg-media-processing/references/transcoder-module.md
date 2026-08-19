# thuis-v4 Transcoder Implementation

## Module: `src/thuis/transcoder.py`

### Functions

```python
check_ffmpeg() -> bool
get_video_resolution(path: Path) -> Optional[int]
should_transcode_to_720p(path: Path) -> bool
transcode_to_720p(input_path, output_path, preset="fast", crf=23, keep_original=False) -> Tuple[bool, Optional[str]]
transcode_file_if_needed(path, keep_original=False, target_height=720) -> Tuple[bool, Optional[Path], Optional[str]]
```

### Integration in `main.py`

```python
# CLI args added:
parser.add_argument("--transcode-720p", action="store_true", help="Transcode downloaded files to 720p if they are higher resolution")
parser.add_argument("--keep-original", action="store_true", help="Keep original file when transcoding (default: replace)")
parser.add_argument("--transcode-preset", type=str, default="fast", choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"], help="FFmpeg preset for transcoding (default: fast)")
parser.add_argument("--transcode-crf", type=int, default=23, help="FFmpeg CRF quality (0-51, lower=better, default: 23)")

# Post-download logic:
if args.transcode_720p and completed.returncode == 0 and not args.dry_run:
    import transcoder
    output_files = list(args.output_dir.glob("*.mp4"))
    for f in output_files:
        if f.stat().st_mtime > (time.time() - 300):
            success, out_path, error = transcoder.transcode_file_if_needed(f, keep_original=args.keep_original, target_height=720)
            if success:
                logger.info(f"Transcoded {f.name} to 720p")
            elif error:
                logger.warning(f"Transcoding failed for {f.name}: {error}")
            break
```

### Usage

```bash
# Basic 720p transcoding
python -m thuis.main --transcode-720p "URL"

# Keep both versions
python -m thuis.main --transcode-720p --keep-original "URL"

# Custom quality
python -m thuis.main --transcode-720p --transcode-preset medium --transcode-crf 20 "URL"
```

### Decision Logic

| Source Resolution | Transcoded? |
|-------------------|-------------|
| > 720p (1080p, 1440p, 2160p) | ✅ Yes → 720p |
| 720p | ❌ Already at target |
| < 720p (540p, 480p) | ❌ Below target (no upscaling) |

### Quality Settings

| Preset | Speed | Use Case |
|--------|-------|----------|
| ultrafast | Fastest | Quick tests |
| fast | Fast | Default for batch |
| medium | Balanced | General purpose |
| slow | Slow | Archival quality |

| CRF | Quality | Bitrate |
|-----|---------|---------|
| 18-20 | Visually lossless | High |
| 23 | Default (good) | Medium |
| 28-30 | Lower quality | Low |