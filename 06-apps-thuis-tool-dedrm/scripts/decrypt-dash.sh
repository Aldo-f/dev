#!/usr/bin/env bash
# Decrypt a DASH/CENC stream using mp4decrypt (shaka-packager)
# Usage: ./decrypt-dash.sh <init.mp4> <segment1.m4s> [segment2.m4s ...] <output.mp4>
# Assumes single track (video+audio combined or separate)
set -euo pipefail

# Check arguments: at least init + one segment + output
if [ "$#" -lt 3 ]; then
  echo "Usage: decrypt-dash.sh <init.mp4> <segment1.m4s> [segment2.m4s ...] <output.mp4>"
  exit 1
fi

INIT="${1:?init.mp4 missing}"
shift
OUTPUT="${!#:?output.mp4 missing}"  # last arg
SEGMENTS=("$@")  # all except first and last
unset 'SEGMENTS[${#SEGMENTS[@]}-1]'  # remove last element (output)

# Public test credentials (Bitmovin demo). Rotate for real streams.
KID="e3b6f6c38c4f4d5b9e6c3d7b8a5f2e1d"
KEY="d0ad3aef3c4f4d5b9e6c3d7b8a5f2e1d"

if ! command -v mp4decrypt >/dev/null 2>&1; then
  echo "ERROR: mp4decrypt not found. Install shaka-packager." >&2
  exit 1
fi

# Create temp combined file
TMP="$(mktemp --suffix=.mp4)"
trap 'rm -f "$TMP"' EXIT

# Build concatenated stream: init + all segments
echo "Building combined stream from $INIT + ${#SEGMENTS[@]} segments..."
{
  cat "$INIT"
  for seg in "${SEGMENTS[@]}"; do
    cat "$seg"
  done
} > "$TMP"

echo "Decrypting with KID=$KID..."
mp4decrypt --key "${KID}:${KEY}" "$TMP" "$OUTPUT"

echo "Done. Output: $(ls -lh "$OUTPUT" | awk '{print $5, $9}')"