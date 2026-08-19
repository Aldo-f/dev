#!/bin/bash
# sensors-daily-summary.sh — generate daily summary from continuous sensor log.
# Called via cron (e.g. at 00:05 daily). Reads yesterday's data from sensors-continuous.log.
# Writes summary to sensors-daily.log (kept for 1 year).
set -euo pipefail

REPO_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LOG_DIR="$REPO_DIR/logs"
mkdir -p "$LOG_DIR"

CONTINUOUS_LOG="$LOG_DIR/sensors-continuous.log"
DAILY_LOG="$LOG_DIR/sensors-daily.log"

# Ensure continuous log exists
if [ ! -f "$CONTINUOUS_LOG" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Continuous log not found: $CONTINUOUS_LOG" >> "$DAILY_LOG"
  exit 1
fi

# Get yesterday's date
YESTERDAY=$(date -d "yesterday" '+%Y-%m-%d')

# Use python to parse the log properly
python3 - "$CONTINUOUS_LOG" "$YESTERDAY" "$DAILY_LOG" << 'PYEOF'
import sys
import re

input_file = sys.argv[1]
target_date = sys.argv[2]
output_file = sys.argv[3]

# Pattern to match temp values: temp1: +72.2°C
temp_pattern = re.compile(r'temp\d+:\s*\+?([\d.]+)°C')

# The log format:
# [YYYY-MM-DD HH:MM:SS] Starting continuous sensor monitor
# [HH:MM:SS] temp1: +72.2°C temp1: +59.5°C

current_date = None
cpu_temps = []
rpi_temps = []

with open(input_file, 'r') as f:
    for line in f:
        # Check for date header: [YYYY-MM-DD HH:MM:SS]
        date_match = re.match(r'\[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}\]', line)
        if date_match:
            current_date = date_match.group(1)
            continue
        
        # Check for data line: [HH:MM:SS] temp1: +72.2°C temp1: +59.5°C
        time_match = re.match(r'\[\d{2}:\d{2}:\d{2}\]', line)
        if time_match and current_date == target_date:
            matches = temp_pattern.findall(line)
            if len(matches) >= 2:
                cpu_temps.append(float(matches[0]))
                rpi_temps.append(float(matches[1]))
            elif len(matches) == 1:
                cpu_temps.append(float(matches[0]))

def stats(name, temps):
    if not temps:
        return f"{name}: no data"
    return f"{name}: min={min(temps):.1f}°C max={max(temps):.1f}°C avg={sum(temps)/len(temps):.1f}°C count={len(temps)}"

cpu_stat = stats("cpu_thermal", cpu_temps)
rpi_stat = stats("rp1_adc", rpi_temps)
sample_count = max(len(cpu_temps), len(rpi_temps))

with open(output_file, 'a') as f:
    f.write(f"=== {target_date} ===\n")
    f.write(f"{cpu_stat}\n")
    f.write(f"{rpi_stat}\n")
    f.write(f"samples: {sample_count}\n\n")

if sample_count > 0:
    print(f"Summary written for {target_date}: {sample_count} samples")
else:
    print(f"No data for {target_date}")

PYEOF

# Rotate daily log: keep 365 days
find "$LOG_DIR" -name 'sensors-daily.log' -mtime +366 -exec mv {} {}.old \; 2>/dev/null || true
find "$LOG_DIR" -name 'sensors-daily.log.old' -mtime +367 -delete 2>/dev/null || true

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Daily summary completed for $YESTERDAY" >> "$DAILY_LOG"