---
name: buster-captcha-solver
description: Load Buster extension for Playwright and Camoufox.
---

## Overview
Buster is a captcha‑solver extension (Chrome/Edge MV3, Firefox XPI). It can be used with the *form‑automation* scripts to handle visual reCAPTCHA challenges.

### Playwright (Chromium)
- Default Playwright runs headless, which **cannot load MV3 extensions** – Buster will be inert.
- Use `--headed --buster` to launch a **persistent Chromium context** with `--load‑extension=tmp/buster_chrome`.
- The helper `ensure_buster_chrome_installed()` downloads the Chrome zip from the official GitHub release (v3.4.0) and extracts it under `tmp/buster_chrome`.
- Verify the extension is active via CDP `Target.getTargets` – a `chrome‑extension://…` service worker appears.

### Camoufox (Firefox)
- Loads the Firefox XPI (`tmp/buster_firefox`) via `Camoufox(addons=[...])`.
- Works in both headless and headed modes, though some challenges still need manual interaction.
- Use `CamoufoxFormAutomation.test_buster_on_recaptcha_demo()` to confirm the UI is present on the reCAPTCHA demo page.

## Common Pitfalls
- **Headless Chromium**: extensions are silently ignored – Buster never runs.
- **Incorrect path**: ensure the directory contains `manifest.json`. The helper functions automatically reinstall if missing.
- **Version mismatch**: Buster Chrome requires Chromium ≥ 123; Playwright’s bundled Chromium 148 satisfies this.
- **Camoufox Firefox XPI**: Camoufox requires a valid Firefox addon directory with `manifest.json`. The npm build from source fails on non-x86_64 architectures (e.g., arm64). The correct approach is to download the official XPI from Mozilla Add-ons and extract it directly:
  ```bash
  rm -rf tmp/buster_firefox
  wget -O buster.xpi "https://addons.mozilla.org/firefox/downloads/latest/buster-captcha-solver/latest.xpi"
  unzip -o buster.xpi -d buster_firefox
  ```
  Verify `manifest.json` exists in `buster_firefox/` before passing the path to `Camoufox(addons=[...])`.

## References
- `references/buster-chrome-install.md`
- `references/buster-firefox-install.md`
- `references/buster-firefox-xpi-install.md` (new)

## Scripts
- `scripts/verify-buster-chrome-loaded.py` – CDP script that lists extension targets to confirm loading.