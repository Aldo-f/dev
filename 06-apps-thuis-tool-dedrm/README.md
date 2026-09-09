# DeDRM Learning Tool

Educational tool for understanding how DRM (Widevine, etc.) works at the
file/segment level. **Strictly for legal, public test streams.** Applying
this to copyrighted material without authorization violates copyright law
(DMCA §1201, EU InfoSoc Directive Art. 6, Belgian Auteurswet Art. 80bis).

## Background

DRM is a packaging format (CENC/cbcs + PSSH) plus a license-acquisition
protocol (Widevine, PlayReady, FairPlay, ClearKey). Once the file is
decrypted, the rest of the pipeline is just MP4/CMAF.

## Public test source (verified during build)

- Bitmovin public demo manifest: `https://cdn.bitmovin.com/content/assets/art-of-motion_drm/mpds/11331.mpd`
- License server: `https://cwip-shaka-proxy.appspot.com/no_auth`
- Public test KID/Key are embedded in `credentials.txt` (do not use for
  real Bitmovin streams — they have rotating keys).

## Files

```
~/dev/06-apps-thuis-tool-dedrm/
├── README.md              ← this file
├── credentials.txt        ← public test KID/Key (gitignored)
├── scripts/
│   ├── decrypt.sh         ← mp4decrypt wrapper
│   ├── inspect.sh         ← ffprobe for PSSH/KID inspection
│   └── fetch_segments.py  ← parse MPD and download segments
├── docs/
│   └── DRM-FLOW.md        ← what we learned
└── tests/
    └── test_decrypt.sh    ← smoke test
```

## How to use

```
# 1) Download manifest + segments
python3 scripts/fetch_segments.py \
  --mpd https://cdn.bitmovin.com/content/assets/art-of-motion_drm/mpds/11331.mpd \
  --out segments/

# 2) Decrypt with the public test key
./scripts/decrypt.sh segments/ video_decrypted.mp4

# 3) Inspect
./scripts/inspect.sh video_decrypted.mp4
```

## Next step for thuis

Add DeDRM-aware transcoding to thuis-v5: when an input file's `pssh` box
contains a known CENC scheme, extract the kid, look up the key in
Vaultwarden, decrypt → re-encode → re-mux. All operations gated behind
explicit `licence_ok = True` flag in thuis config.
