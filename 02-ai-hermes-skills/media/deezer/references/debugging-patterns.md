# Deezer CLI — Debugging Patterns

## When Patches Create Structural Conflicts

If you've made multiple `patch` operations and the file ends up with:
- Duplicate function definitions
- Orphaned code blocks (code after a `return` or inside another function)
- `NameError` for functions that were defined earlier
- Indentation errors from misaligned patches

**The reliable recovery pattern:**

1. **Read the full file** with `read_file` to see actual state
2. **Don't keep patching** — the conflicts compound
3. **Use `write_file` to rewrite the entire file** from scratch with the correct structure
4. **Verify syntax** before running:
   ```bash
   python -c "import ast; ast.parse(open('scripts/deezer.py').read()); print('syntax OK')"
   ```
5. **Run tests**: `~/.venvs/deezer/bin/python -m pytest -q`
6. **Test real usage**: `~/scripts/deezer/scripts/deezer.py whoami`

## Common Pitfalls Fixed in This Session

### Duplicate `HANDLERS` dict
If you see `HANDLERS = {` appearing twice, or functions defined AFTER the `HANDLERS` dict that should be BEFORE it, rewrite the file cleanly.

### Missing function definitions
If `NameError: name 'cmd_download_track' is not defined` appears:
- Check if the function is defined BEFORE the `HANDLERS` dict
- Check if `write_file` or patch operations accidentally deleted the definition
- Rewrite the complete function in the correct location

### Broken parser `return p`
If `AttributeError: 'NoneType' object has no attribute 'parse_args'`:
- The `build_parser()` function is missing `return p` at the end
- Check the last few lines of the function

### Missing helper functions
If `AttributeError: module 'deezer_utils' has no attribute 'get_user_info'`:
- Some helper functions may have been accidentally deleted during refactoring
- Check `deezer_utils.py` for all expected functions: `album_tracks`, `flow_tracks`, `get_lyrics`, `get_user_info`

## Test-Verify Workflow

Always follow this sequence:
1. Syntax check: `python -c "import ast; ast.parse(open('file.py').read())"`
2. Unit tests: `pytest -q`
3. CLI help: `deezer.py --help`
4. Real command test: `deezer.py whoami`
5. Real download test: `deezer.py download-track <id> --out /tmp/test`

If any step fails, fix BEFORE proceeding to the next.
