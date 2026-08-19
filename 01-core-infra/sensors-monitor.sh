#!/bin/bash
# sensors-monitor.sh — continuous sensor logging (every second) for trend analysis.
# Runs as a systemd service, starts on boot. Logs to ./logs/sensors-continuous.log
set -euo pipefail

REPO_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LOG_DIR="$REPO_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/sensors-continuous.log"

# Ensure sensors command exists
if ! command -v sensors >/dev/null 2>&1; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: sensors command not found" >> "$LOG_FILE"
  exit 1
fi

# Log rotation: keep only last 7 days of data (604800 seconds)
# We'll truncate the file periodically to avoid unbounded growth
ROTATE_INTERVAL=3600  # check every hour
last_rotate=$(date +%s)

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting continuous sensor monitor" >> "$LOG_FILE"

while true; do
  TIMESTAMP=$(date '+%H:%M:%S')
  # Get only temperature lines from sensors output
  TEMPS=$(sensors 2>/dev/null | grep -i temp | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr '\n' ' | ' | sed 's/ | $//')
  
  if [ -n "$TEMPS" ]; then
    echo "[$TIMESTAMP] $TEMPS" >> "$LOG_FILE"
  else
    echo "[$TIMESTAMP] No temperature sensors found" >> "$LOG_FILE"
  fi

  # Periodic log rotation - keep last 7 days (~604800 lines at 1/sec, but we'll be more conservative)
  now=$(date +%s)
  if [ $((now - last_rotate)) -ge $ROTATE_INTERVAL ]; then
    # Keep last 100800 lines (7 days * 24 hours * 60 min * 60 sec / 60 = 100800 if we logged every minute, but we log every second)
    # Actually at 1/sec: 7 days = 604800 lines. Keep 604800 lines.
    tail -n 604800 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE" 2>/dev/null || true
    last_rotate=$now
  fi

  sleep 1
done