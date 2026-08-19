#!/bin/bash
# Download VRT MAX shows (FC De Kampioenen, Flikken, Flikken Maastricht)
# Runs hourly via cron job. Skips already downloaded episodes.
# Retries on failure automatically on next run.
#
# Usage:
#   ./download-vrt-shows.sh              # Download all shows from config
#   ./download-vrt-shows.sh --urls list.txt  # Download specific URLs from file
#   ./download-vrt-shows.sh "url1" "url2"   # Download specific URLs directly

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Output directory - use the project-specific path
OUTPUT_DIR="$PROJECT_DIR/media/tv"

# Create output directory if it doesn't exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR" || {
        echo "ERROR: Cannot create output directory $OUTPUT_DIR"
        echo "Please ensure the path exists and is writable."
        exit 1
    }
fi

# Show configuration: URL, name, and schedule type
# Schedule types:
#   - "completed" : Show is finished, download all episodes
#   - "weekly"    : New episode weekly, download new ones
#   - "daily"     : New episode daily, download new ones
#   - "weekday"   : New episodes on weekdays (Mon-Fri)
declare -A SHOW_URLS=(
    ["fc-de-kampioenen"]="https://www.vrt.be/vrtmax/a-z/fc-de-kampioenen/"
    ["flikken"]="https://www.vrt.be/vrtmax/a-z/flikken/"
    ["flikken-maastricht"]="https://www.vrt.be/vrtmax/a-z/flikken-maastricht/"
)
declare -A SHOW_SCHEDULE=(
    ["fc-de-kampioenen"]="completed"
    ["flikken"]="weekly"
    ["flikken-maastricht"]="weekly"
)

# Create output directory if it doesn't exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR" || {
        echo "ERROR: Cannot create output directory $OUTPUT_DIR"
        echo "Please ensure the path exists and is writable."
        exit 1
    }
fi

# Log file
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/download-$(date +%Y%m%d-%H%M%S).log"

echo "Starting VRT MAX download at $(date)" | tee "$LOG_FILE"
echo "Output directory: $OUTPUT_DIR" | tee -a "$LOG_FILE"
echo "Profile: 1080p" | tee -a "$LOG_FILE"

# Function to download a show (all seasons)
download_show() {
    local url="$1"
    local show_name="$2"

    echo "----------------------------------------" | tee -a "$LOG_FILE"
    echo "Downloading $show_name from $url" | tee -a "$LOG_FILE"
    echo "----------------------------------------" | tee -a "$LOG_FILE"

    cd "$PROJECT_DIR"

    # Run huis.sh with --profile 1080 and the output directory
    # The script will:
    # - Expand the show URL to all seasons/episodes
    # - Skip already downloaded episodes (pre-download dedup)
    # - Download missing episodes at 1080p
    # - Log everything
    # Use PYTHONPATH to ensure the module is found
    PYTHONPATH="$PROJECT_DIR/src${PYTHONPATH:+:$PYTHONPATH}" ./thuis.sh --profile 1080 --output-dir "$OUTPUT_DIR" "$url" 2>&1 | tee -a "$LOG_FILE"

    local exit_code=${PIPESTATUS[0]}
    if [ $exit_code -ne 0 ]; then
        echo "WARNING: Download for $show_name exited with code $exit_code" | tee -a "$LOG_FILE"
        echo "Will retry on next hourly run." | tee -a "$LOG_FILE"
    else
        echo "Completed $show_name successfully" | tee -a "$LOG_FILE"
    fi
    return $exit_code
}

# Function to download URLs from a file
download_from_file() {
    local url_file="$1"

    if [ ! -f "$url_file" ]; then
        echo "ERROR: URL file not found: $url_file" | tee -a "$LOG_FILE"
        return 1
    fi

    echo "----------------------------------------" | tee -a "$LOG_FILE"
    echo "Downloading URLs from file: $url_file" | tee -a "$LOG_FILE"
    echo "----------------------------------------" | tee -a "$LOG_FILE"

    cd "$PROJECT_DIR"

    local line_num=0
    while IFS= read -r url || [ -n "$url" ]; do
        # Skip empty lines and comments
        [[ -z "$url" || "$url" =~ ^# ]] && continue
        line_num=$((line_num + 1))
        echo "[$line_num] Processing: $url" | tee -a "$LOG_FILE"
        PYTHONPATH="$PROJECT_DIR/src${PYTHONPATH:+:$PYTHONPATH}" ./thuis.sh --profile 1080 --output-dir "$OUTPUT_DIR" "$url" 2>&1 | tee -a "$LOG_FILE"
    done < "$url_file"
}

# Main logic
if [ $# -eq 0 ]; then
    # No arguments: download all configured shows
    echo "Downloading all configured shows..." | tee -a "$LOG_FILE"
    for show in "${!SHOW_URLS[@]}"; do
        url="${SHOW_URLS[$show]}"
        schedule="${SHOW_SCHEDULE[$show]}"
        echo "Show: $show (Schedule: $schedule)" | tee -a "$LOG_FILE"
        download_show "$url" "$show"
    done
elif [ "$1" = "--urls" ] && [ $# -ge 2 ]; then
    # Download from URL file
    download_from_file "$2"
elif [ $# -ge 1 ]; then
    # Download specific URLs passed as arguments
    for url in "$@"; do
        download_show "$url" "URL: $url"
    done
fi

echo "========================================" | tee -a "$LOG_FILE"
echo "All downloads completed at $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"