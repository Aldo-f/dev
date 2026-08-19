# thuis-v4 Case-Insensitive Pre-Download Deduplication (2026-08-10)

## Problem

The VRT MAX API returns inconsistent casing for show names:
- "FC De Kampioenen" (uppercase FC) for some episodes
- "Fc De Kampioenen" (lowercase fc) for other episodes

On Linux's case-sensitive filesystem, the glob pattern `Fc.De.Kampioenen.S02E13*.mp4` would not match existing file `FC.De.Kampioenen.S02E13.1080p.WEB-DL.AAC.x264.mp4`, causing unnecessary re-downloads.

## Solution

Changed the pre-download deduplication logic in `src/thuis/main.py` (lines 1109-1129) from case-sensitive `Path.glob()` to case-insensitive `Path.iterdir()` with manual comparison.

### Before (Case-Sensitive)
```python
search = f"{show_norm}.S{season_num:02d}E{episode_num:02d}{res_part}*.mp4"
matches = list(args.output_dir.glob(search))
```

### After (Case-Insensitive)
```python
expected_prefix = f"{show_norm}.S{season_num:02d}E{episode_num:02d}{res_part}".lower()
expected_suffix = ".mp4"
matches = [
    f for f in args.output_dir.iterdir()
    if f.is_file() and f.name.lower().startswith(expected_prefix) and f.name.lower().endswith(expected_suffix)
]
```

## Files Modified

1. **src/thuis/main.py** - Updated dedup logic (lines 1109-1129)
2. **tests/thuis/test_resolution_and_retry.py** - Updated test to mock `iterdir()` instead of `glob()`

## Verification

- All 196 tests pass
- Manual testing: S02E13 correctly skipped when 1080p file exists (tested with both 1080p and 720p profile flags)
- Case-insensitive matching works for any VRT API casing variation

## Pitfall: Test Mocking

When testing the dedup logic, mock `Path.iterdir()` instead of `Path.glob()`. The mock should return `Path` objects with `.is_file()` and `.name` attributes.

```python
# Correct mock for case-insensitive implementation
mock_file = MagicMock(spec=Path)
mock_file.is_file.return_value = True
mock_file.name = "Test.Show.S01E01.mp4"  # Must match normalized show name

with patch("thuis.main.Path.iterdir", return_value=[mock_file]):
    # test code
```

## Related Files

- `src/thuis/main.py` - Main implementation
- `src/thuis/scene_namer.py` - `normalize_show_name()` function used for show name normalization
- `tests/thuis/test_resolution_and_retry.py` - Test coverage