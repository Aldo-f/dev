#!/usr/bin/env python3
"""Inspect an MP4/CENC file for PSSH box and KID.

Usage:
  ./inspect.sh <input.mp4>
"""
import subprocess, sys, json
from pathlib import Path

IN = Path(sys.argv[1]) if sys.argv[1] else None
if not IN or not IN.exists():
    print("Usage: inspect.sh <input.mp4>", file=sys.stderr)
    sys.exit(1)

# Try mp4info first, then ffprobe
for tool in ["mp4info", "ffprobe"]:
    try:
        result = subprocess.run(
            [tool, "-show_format", "-show_streams", str(IN)],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout + result.stderr
        # Look for pssh in the full output
        pssh_matches = re.findall(r'pssh[^\n]{0,200}', output, flags=re.IGNORECASE)
        if pssh_matches:
            print(f"=== {tool} output (first pssh found) ===")
            for m in pssh_matches[:3]:
                print(m.strip())
            break
        else:
            print(f"No PSSH found in {tool} output")
    except FileNotFoundError:
        continue
    except Exception as e:
        print(f"{tool} error: {e}")

# Also check raw hex of first 200 bytes for pssh box
try:
    with open(IN, "rb") as f:
        header = f.read(200)
    # cenc PSSH box starts with "pssh" and version+flags
    if b"pssh" in header.lower():
        print("\n=== Raw hex near pssh ===")
        idx = header.lower().find(b"pssh")
        print(header[idx:idx+80].hex())
        print("ASCII:", repr(header[idx:idx+80]))
except Exception as e:
    print(f"Hex read error: {e}")

import re  # loaded late for safety