#!/usr/bin/env python3
"""Parse DASH MPD manifest, extract segment URLs, download them.

Usage:
  python3 fetch_segments.py --mpd <URL> --out <dir>
"""
import argparse, os, sys, re
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

try:
    import requests
except ImportError:
    print("Installing requests…", file=sys.stderr)
    os.system(f"{sys.executable} -m pip install requests --quiet")
    import requests

NS = {"mpd": "urn:mpeg:dash:schema:mpd:2011"}

def fetch(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.text

def parse_mpd(text, base):
    root = ET.fromstring(text)
    urls = []
    for rep in root.findall(".//mpd:Representation", NS):
        base_url = rep.findtext("mpd:BaseURL", default="", namespaces=NS)
        for seg in rep.findall(".//mpd:SegmentTemplate", NS):
            media = seg.get("media", "")
            if not media:
                continue
            init = seg.get("initialization", "")
            if init:
                urls.append(urljoin(base, init.replace("$RepresentationID$", rep.get("id", ""))))
            # Handle $Number$ and $Bandwidth$
            media_resolved = media.replace("$RepresentationID$", rep.get("id", ""))
            media_resolved = media_resolved.replace("$Bandwidth$", str(rep.get("bandwidth", "0")))
            # For simplicity, download first N numbered segments
            n = min(3, int(seg.get("startNumber", "1")))
            for i in range(n, n+1):
                seg_url = media_resolved.replace("$Number$", str(i))
                urls.append(urljoin(base, seg_url))
        for seg in rep.findall(".//mpd:SegmentBase", NS):
            init = seg.get("indexRange", "")
            if init:
                urls.append(urljoin(base, base_url) if base_url else base)
    return urls

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mpd", required=True)
    p.add_argument("--out", default="segments")
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    text = fetch(args.mpd)
    urls = parse_mpd(text, args.mpd.rsplit("/", 1)[0] + "/")
    print(f"Found {len(urls)} segment URLs:")
    for u in urls:
        print(f"  {u}")
        fname = os.path.join(args.out, os.path.basename(u.split("?")[0]))
        r = requests.get(u, timeout=60)
        r.raise_for_status()
        with open(fname, "wb") as f:
            f.write(r.content)
        print(f"  → saved {fname} ({len(r.content)} bytes)")

if __name__ == "__main__":
    main()