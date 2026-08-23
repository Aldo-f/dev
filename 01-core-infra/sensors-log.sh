#!/bin/bash
# sensors-log.sh — log sensor readings (temp, fan, voltage) for trend analysis.
# Called via cron (e.g. every 5 minutes). Appends to ./logs/sensors.log.
set -euo pipefail

REPO_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LOG_DIR="$REPO_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/sensors.log"

# Ensure sensors command exists
if ! command -v sensors >/dev/null 2>&1; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARN: sensors command not found" >> "$LOG_FILE"
  exit 0
fi

# Capture sensor output with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
SENSORS_OUTPUT=$(sensors 2>/dev/null || echo "ERROR: sensors failed")

# Log in a structured format: timestamp | key=value pairs
# Extract key metrics we care about
echo "=== $TIMESTAMP ===" >> "$LOG_FILE"
echo "$SENSORS_OUTPUT" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Rotate logs older than 30 days
find "$LOG_DIR" -name 'sensors.log' -mtime +30 -exec mv {} {}.old \; 2>/dev/null || true
find "$LOG_DIR" -name 'sensors.log.old' -mtime +31 -delete 2>/dev/null || true