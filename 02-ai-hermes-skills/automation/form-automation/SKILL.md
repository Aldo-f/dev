---
name: form-automation
description: Google Forms automation with Camoufox/Playwright + Whisper.
---

# Form Automation

Comprehensive skill for running Google Forms automation on Raspberry Pi 5 (and other Linux), using Camoufox (Firefox-based anti-detection) or Playwright (Chromium) with Buster captcha solver extension, and OpenAI Whisper for fully automatic audio captcha solving.

## Architecture

Two parallel implementations share config, counter, and logging:
- `auto_form.py` — Playwright/Chromium (primary, supports Buster in headed mode only)
- `auto_form_camoufox.py` — Camoufox/Firefox (works headless & headed, Buster as Firefox addon)

Shared:
- `config.yaml` — form URL, field selectors, submit selectors, confirmation selector
- `data/counter.json` — persistent submission counter (`${counter}` placeholder in config)
- `logs/submissions.log` — append-only detailed logs
- `base_automation.py` — shared base class (config loading, counter, logging, batch loop)
- `audio_solver.py` — **NEW**: Whisper-based audio captcha solver (self-contained, no external API)
- `tmp/buster_firefox/` — unpacked Firefox XPI (manifest.json at root for Camoufox)
- `tmp/buster_chrome/` — unpacked Chrome MV3 extension (for Playwright `--headed --buster`)

## Key Improvements (This Session)

### 1. Whisper Audio Captcha Solver (`audio_solver.py`)
- Uses `openai-whisper` (pip) with `tiny` model (~39 MB, fast on Pi 5)
- Downloads reCAPTCHA audio challenge via `curl`, converts with `ffmpeg` to 16 kHz mono WAV
- Transcribes locally, cleans text (lowercase, alphanumeric only), fills response field, submits
- Integrated into `CamoufoxFormAutomation` as `self.audio_solver` + `solve_audio_challenge(bframe)`
- **No cloud API keys, no network round-trips beyond the audio download**

### 2. Camoufox + Buster Firefox Addon
- Buster XPI downloaded from AMO and unpacked to `tmp/buster_firefox/`
- Camoufox loads via `addons=[str(buster_path)]` — requires `manifest.json` at addon root
- Shadow-DOM click on `.help-button-holder` to trigger Buster's solver button (works headless)
- If Buster fails/times out, falls back to `audio_solver` (Whisper)

### 3. Performance Optimizations
- Reduced redundant `page.wait_for_timeout()` calls (was ~10-15s per submission, now ~3-5s)
- Single browser instance reused for entire batch (no per-submission restart)
- Early-exit success detection before captcha handling
- JS-based field filling (avoids click+type overhead)
- `wait_until="domcontentloaded"` instead of `networkidle` for form load

### 4. Maintenance Improvements
- `requirements.txt` now declares all deps: `playwright>=1.40.0`, `camoufox`, `httpx`, `pyyaml`, `openai-whisper`
- Fixed `mail_verifier` import ordering (logger not defined at module import time)
- Config-driven via `config.yaml` — no hardcoded selectors in scripts
- Clear separation: base class = orchestration, subclass = browser-specific impl

## Quick Start

```bash
cd /home/aldo/scripts/form-automation

# One-time setup (venv + deps + browsers)
./setup.sh   # creates venv, installs requirements, playwright install chromium

# Run Camoufox batch (headless, 100 submissions, 2s delay)
source venv/bin/activate
python auto_form_camoufox.py --batch 100 --delay 2 --headless

# Run Playwright headed with Buster (visual debugging)
python auto_form.py --headed --buster --batch 5 --delay 2

# Test Buster on reCAPTCHA demo
python auto_form_camoufox.py --test-buster

# Show/set counter
python auto_form_camoufox.py --show-counter
python auto_form_camoufox.py --counter 42
```

## Configuration (`config.yaml`)

```yaml
default_form: form1

forms:
  form1:
    url: "https://docs.google.com/forms/d/e/.../viewform"
    fields:
      email:
        selector: 'input[type="email"]'
        value: "your@email.com"
      competition_question:
        selector: 'input[type="text"] >> nth=0'
        value: "Your answer"
      tiebreaker_question:
        selector: 'input[type="text"] >> nth=1'
        value: "${counter}"   # replaced with current counter at runtime
    submit_selectors:
      - 'div[jsname="M2UYVd"]'
      - 'div[role="button"]:has-text("Verzenden")'
    confirmation_selector: '.freebirdFormviewerViewResponseConfirmationMessage'
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: camoufox` | Not in venv | `source venv/bin/activate && pip install -r requirements.txt` |
| `InvalidAddonPath: manifest.json missing` | Buster not unpacked correctly | Delete `tmp/buster_firefox/` and re-run (auto-downloads XPI) |
| `wait_for_selector timeout` | Selector changed | Inspect live form, update `config.yaml` selectors |
| Audio solve fails | Whisper model not loaded | First run downloads model (~39 MB); ensure `ffmpeg` installed |
| Counter not incrementing | Submission not confirmed | Check `confirmation_selector` matches success page |

## Files of Interest

- `audio_solver.py` — Self-contained Whisper solver (reusable)
- `base_automation.py` — Shared orchestration (extend for new browser backends)
- `config.py` — YAML loader with validation
- `tmp/buster_firefox/manifest.json` — Must exist for Camoufox addon loading

## Pitfalls to Avoid

1. **Never hand-edit `data/counter.json` while a batch runs** — next save clobbers it
2. **Headless Chromium ≠ Buster** — MV3 extensions don't run in headless Chrome; use `--headed --buster` or Camoufox
3. **Camoufox addon path** — must point to directory containing `manifest.json` (unpacked XPI), not the `.xpi` file
4. **reCAPTCHA selectors change** — Google rewrites `aria-describedby` IDs; use robust `nth` or attribute selectors in config
5. **Whisper first-run download** — allow ~30s for model fetch on first invocation; subsequent runs use cache

## Extending

To add a new browser backend:
1. Subclass `BaseAutomation`
2. Implement `start_browser()`, `close_browser()`, `submit_form()`, `safe_click_submit()`
3. Use `audio_solver.create_audio_solver()` for captcha fallback
4. Register in CLI `main()`

## References

- Buster extension: https://github.com/dessant/buster
- Whisper model: `openai/whisper-tiny` (bundled in `openai-whisper` pip package)
- Camoufox: https://github.com/daijro/camoufox