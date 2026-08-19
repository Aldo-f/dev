---
name: shell-logging-and-cron-jobs
description: Use when writing bash scripts or cron jobs that log output.
---

# Shell Logging & Cron Job Conventions

Conventions for writing bash scripts and cron jobs the user runs unattended. Two hard rules,
then the technique to satisfy both without breaking exit-code capture.

## Rules (user requirements — apply ALWAYS)

1. **Every line written to a log must carry a timestamp** `[YYYY-MM-DD HH:MM:SS]`.
   - "Always" and "I meant to do this always — timestamps are important when logging." Do not
     timestamp only your own `log()` messages and leave streamed child-process output bare.
     **Every line**, including output piped from the command being wrapped.
   - Propagate the rule to README/AGENTS descriptions when authoring them.

2. **Do NOT hard-time-limit jobs that legitimately run long.** A blanket `timeout N` around
   `opencode run "/init-deep"` (or similar KB/agent build commands) kills a healthy run at
   N minutes on a large workspace (e.g. 62k files, depth 16 → runs far past 5 min). Let it run
   to completion. Use `timeout` only as a deliberate watchdog when the task is known to be short.

## Pattern: stream + timestamp + capture real exit code

Do NOT put the long command inside a `{ ... }` pipeline and rely on `if cmd | tee`; the
pipeline's `$?` is the LAST command (tee), not your command. Capture the real code via `PIPESTATUS`.

Recommended structure (`init-deep-cron.sh`-style):

```bash
# standalone stamper so a long stream is timestamped line-by-line
STAMPER="${TEMP_DIR}/opencode-init-deep-stamp.sh"
cat > "$STAMPER" <<'INNER'
#!/bin/bash
while IFS= read -r line; do
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$line"
done
INNER
chmod +x "$STAMPER"

log_line() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG_FILE"; }
notify() { command -v notify-send >/dev/null 2>&1 && notify-send "job" "$*" 2>/dev/null || true; }

log_line "=== Starting ==="
opencode run "/init-deep" --dir "$DIR" 2>&1 | "$STAMPER" | tee -a "$LOG_FILE"
RC=${PIPESTATUS[0]}
if [ "$RC" -eq 0 ]; then log_line "SUCCESS: completed (exit 0).";   notify "completed (exit 0)";   exit 0
else                    log_line "ERROR: exited $RC.";              notify "failed (exit $RC)";    exit "$RC"; fi
```

Key points:
- `PIPESTATUS[0]` = the wrapped command's real exit code (stamper/tee are passthrough).
- `notify-send` guards with `command -v` and swallows failures so cron without DBus still logs cleanly.
- Empty-line echo from the streaming tool is fine; the stamper stamps every line including blanks.

## Verification
- `bash -n script.sh` for syntax before running.
- Run once, then `grep -vE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\]' log | grep -v '^$'` → must return nothing (proves every line timestamped).
- Confirm `PIPESTATUS[0]` reflects a real failure mode, not just success.

## References
- `references/init-deep-cron-example.md` — before/after of the worked example (timeout → streaming).