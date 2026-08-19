# Deezer download internals (how actual MP3 downloads work now)

Verified working on 2026-08. This is the "how it actually works" reference for
the `Aldo-f/deezer` repo — the tokenized API flow, the crypto, and the fixes
that made it run. Complements `deezer-case.md` (packaging).

## Why old pydeezer broke
Since **Feb 2025**, Deezer retired the `e-cdns-proxy-*.dzcdn.net` download CDN
that old pydeezer/streamrip/deemix/deezloader targeted. That host now fails DNS
(`Name or service not known`). Login/search still worked; actual download broke.
Today the working mechanism is a **tokenized media API**.

## Two separate pydeezer gotchas (both bit us)

1. **Wrong package**: PyPI `pydeezer` (no hyphen, rcrdclub v1.0.8) is an OAuth
   client, broken on Python 3.13 (`from urllib import urlencode` is Py2-style),
   has no `Deezer` class → `ImportError`. Correct package = **`py-deezer`**
   (hyphen, Chr1st-oo, v1.1.2).
2. **Cookie-domain bug (the "Arl is invalid" error)**: pydeezer 1.1.2 hardcodes
   `api_urls.DEEZER_URL = "https://www.deezer.com"` (scheme included). `requests`
   never sends a cookie whose domain contains a scheme → the ARL never reaches
   Deezer → `LoginError("Arl is invalid.")` despite a valid ARL. Fix: patch the
   constant to a bare `"deezer.com"` **before importing `pydeezer.Deezer`**
   (the class reads the const at import time, so patching after the import is
   a no-op):
   ```python
   from pydeezer.constants import api_urls
   api_urls.DEEZER_URL = "deezer.com"   # must precede `from pydeezer import Deezer`
   ```

## The working download flow (4 steps)

1. **`license_token`** — from logged-in user data:
   `POST www.deezer.com/ajax/gw-light.php` method `deezer.getUserData`
   (params `api_version=1.0&api_token=null&input=3&method=...`). The session
   must carry the `arl` cookie set on a SENDABLE domain (`deezer.com`, and the
   UA should be modern, `Chrome/132.0` not the bundled Chrome 67). Response
   gives `checkForm` (the API token for subsequent calls) and
   `USER.OPTIONS.license_token`.
2. **Per-track `TRACK_TOKEN`** — `deezer.pageTrack` with `{"SNG_ID": <id>`}`
   using the `checkForm` as `api_token`. Track data also carries
   `SNG_TITLE`, `SNG_CONTRIBUTORS[]/main_artist`, `ALB_TITLE`, `ART_NAME`,
   `TRACK_NUMBER`, `DISK_NUMBER`, `PHYSICAL_RELEASE_DATE`, `ISRC`,
   `COPYRIGHT`, `LABEL_NAME`, `ALB_PICTURE`.
3. **Stream URL** — `POST https://media.deezer.com/v1/get_url` with:
   ```json
   { "license_token": "<LT>",
     "media": [{ "type": "FULL",
                 "formats": [{ "cipher": "BF_CBC_STRIPE", "format": "MP3_128" }]}],
     "track_tokens": ["<TRACK_TOKEN>"] }
   ```
   Response: `data[0].media[0].sources[0].url` → a URL on
   `cdnt-stream.dzcdn.net/media/...` . The stream is encrypted
   (`BF_CBC_STRIPE`).
4. **Blowfish-CBC strip decrypt** — every 3rd 2048-byte block is encrypted, the
   rest pass through. Key from `pydeezer.util.get_blowfish_key(str(track_id))`;
   CBC IV 8 zero bytes; chunk size 2048. Loop in 2048*3 buffers, decrypt only
   the first 2048 bytes of each, write the rest untouched. Produce a real MP3.

### Bitrate / rights
Free-tier ARL ⇒ only `MP3_128`. Requesting `MP3_320`/`FLAC` returns
`errors[0].code 1002 "license token has no sufficient rights"` — an account
subscription limit, not a code bug. Default to `MP3_128` unless you know the ARL
is premium.

## Output requirements (Aldo's)
- **Flat** — `<Artist> - <Title>.mp3` directly in `--out`, no per-track
  subdirs. Sanitize illegal filename chars; append ` (2)` only if collision +
  forced re-download.
- **Idempotent** — `skip_existing=True` default: compute the path *before* any
  network call, raise `AlreadyDownloadedError` if it exists, CLI prints
  `SKIP <path>`. Re-running a playlist must download nothing new (0 downloaded,
  N skipped) and create no duplicates.
- **Full metadata** — ID3 title/artist/album/albumartist/track+disc/year/
  genre/isrc/label/copyright/composer/bpm + embedded cover art (image fetched
  from `e-cdns-images.dzcdn.net` cover ID, APIC frame).
- `--limit` must be ≥ 1; parser rejects `--limit 0` (was silently making `(2)`
  copies).

## Tests
Hermetic suite (`tests/`, `pytest.ini` `pythonpath = scripts tests`, `testpaths
tests`) mocking all network: ARL resolution, cookie-domain fix, get_url payload,
Blowfish round-trip, flat/named output, ID3 tagging, skip-existing. Run:
`~/.venvs/deezer/bin/python -m pytest` (17 tests).