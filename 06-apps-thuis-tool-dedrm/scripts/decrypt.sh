#!/usr/bin/env bash
# Decrypt a CENC-encrypted MP4 using mp4decrypt (shaka-packager)
# Usage: ./decrypt.sh <input.mp4> <output.mp4>
set -euo pipefail

IN="${1:?Usage: decrypt.sh <input.mp4> <output.mp4>}"
OUT="${2:?Usage: decrypt.sh <input.mp4> <output.mp4>}"

# Public test credentials (Bitmovin demo). Rotate for real streams.
KID="e3b6f6c38c4f4d5b9e6c3d7b8a5f2e1d"
KEY="d0ad3aef3c4f4d5b9e6c3d7b8a5f2e1d"

if ! command -v mp4decrypt >/dev/null 2>&1; then
  echo "ERROR: mp4decrypt not found. Install shaka-packager." >&2
  exit 1
fi

echo "Decrypting $IN -> $OUT"
mp4decrypt --key "${KID}:${KEY}" "$IN" "$OUT"
echo "Done. Size: $(du -h "$OUT" | cut -f1)"