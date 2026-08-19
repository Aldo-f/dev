---
name: self_improving_form_automation
description: Self‑improving form bot with AI patching.
---

# Self‑Improving Form Automation

## When to use
Use this skill when you need to create a long‑running form‑filling bot that:
* Submits data to Google Forms (or similar) repeatedly.
* Must solve CAPTCHA challenges without relying on external paid services.
* Should improve its own success rate over time by learning from failures.
* Requires concise, self‑contained, evidence‑based implementation (user preference).

## Prerequisites
* Python 3.10+ and a virtual environment.
* Playwright (>=1.40) and Camoufox (>=0.5) browsers.
* Whisper.cpp (tiny model) for speech‑to‑text CAPTCHA solving.
* Tesseract OCR with language data.
* ffmpeg for audio extraction.
* Access to a FreLLM‑compatible endpoint (e.g. `https://freellm.aldof.duckdns.org/v1`).

## Directory layout (suggested)
``` 
form-automation/
├── src/
│   ├── __init__.py
│   ├── ai_improver.py          # FreLLM‑driven patching
│   ├── browser_manager.py      # Unified Playwright/Camoufox controller
│   ├── whisper_solver.py       # Local Whisper audio CAPTCHA solver
│   ├── tesseract_ocr.py        # Image CAPTCHA fallback
│   ├── logger.py               # Structured JSON logging + screenshots
│   └── submission_flow.py      # Core submission state machine
├── config/
│   └── config_v2.yaml          # Form URLs, selectors, counters
├── data/
│   ├── counter.json            # Persistent submission counter
│   └── STOP                    # Touch‑file to request graceful shutdown
├── logs/
│   ├── submissions.log         # JSON‑lines audit trail
│   ├── screenshots/            # Auto‑captured on errors
│   └── audio_buffer/           # Transient CAPTCHA audio
├── references/
│   └── implementation-notes.md # Session‑specific details and fixes
├── scripts/
│   └── verify-setup.sh         # Pre‑flight checks for binaries and permissions
├── requirements.txt
�└── README.md
```

## Step‑by‑step workflow

1. **Set up the environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium   # needed for headed mode (Buster works only headed)
   ```

2. **Prepare static assets**
   * Create the directories `data`, `logs/screenshots`, `logs/audio_buffer`, `tmp`, `references`, `scripts`.
   * Place a baseline `config_v2.yaml` (see template below).
   * Add implementation notes and verification scripts to their respective directories.

3. **Implement the core modules** (see the provided source files in the session):
   * `logger.py` – JSON‑lines logger with `capture_screenshot`.
   * `whisper_solver.py` – loads Whisper‑tiny, converts CAPTCHA audio to wav, returns transcription.
   * `tesseract_ocr.py` – image‑to‑text fallback with simple preprocessing.
   * `browser_manager.py` – starts Playwright Chromium **or** Camoufox in headed mode, detects CAPTCHA, routes to Whisper/Tesseract/manual fallback.
   * `submission_flow.py` – loads config, maintains counter, runs submission batches, triggers AI improvement after *N* failures, persists counter.
   * `ai_improver.py` – collects recent failure patterns, queries the FreLLM `/v1/chat/completions` endpoint with a prompt asking for patches (selector, timeout, retry, captcha, config), applies patches to `config_v2.yaml` (keeping a `.bak` backup).
   * `scripts/run_automation.py` – infinite loop calling `SubmissionFlow.run_continuous()`, handles SIGTERM/SIGINT via a `STOP` touch‑file.

4. **Run the daemon**
   ```bash
   source venv/bin/activate
   python scripts/run_automation.py
   ```
   The process will run forever, submitting one form every `delay` seconds (default 2 s), improving after each block of 10 failures.

5. **Observe self‑improvement**
   * Check `logs/submissions.log` for JSON lines showing success/failure.
   * After each improvement cycle, `ai_improver` logs the number of patches applied.
   * Patches are visible in `config_v2.yaml` (with a `.bak` safety copy).

6. **Graceful shutdown**
   ```bash
   touch data/STOP
   ```
   The daemon will finish the current cycle, print final stats, and exit.

## Configuration (`config_v2.yaml`) template
```yaml
form:
  url: "https://forms.gle/your-form-id"
  fields:
    email:
      selector: 'input[type="email"]'
      value: "chiefmommy@web-library.net"
    competition_question:
      selector: 'input[type="text"] >> nth=0'
      value: "Waarom bleef je niet voor mij?"
    tiebreaker_question:
      selector: 'input[type="text"] >> nth=1'
      value: "${counter}"
  submit:
    - selector: 'div[jsname="M2UYVd"]'
    - selector: 'div[role="button"]:has-text("Verzenden")'
    - selector: 'div[role="button"]:has-text("Envoyer")'
    - selector: 'div[role="button"]:has-text("Submit")'
  confirmation:
    - '.freebirdFormviewerViewResponseConfirmationMessage'

browser:
  type: "chromium"   # or "camoufox"
  headless: false    # headed required for Buster/Whisper UI
  timeout: 30000

captcha:
  use_whisper: true
  use_tesseract: true
  use_buster: true
  manual_fallback: true
  audio_timeout: 60

ai_improvement:
  enabled: true
  failure_threshold: 10   # triggers after this many failures
  model: "auto"
  endpoint: "https://freellm.aldof.duckdns.org/v1"
  auto_apply_patches: true
  patch_types:
    - selector
    - timeout
    - retry
    - captcha
    - config
```

## Key techniques & why they work
* **Whisper‑tiny for audio CAPTCHA** – extracts the spoken challenge directly from the browser’s audio element, bypassing the need for Buster or paid solving services.
* **Tesseract OCR fallback** – handles simple image‑based CAPTCHAs; basic contrast/sharpen preprocessing improves accuracy on noisy images.
* **AI‑driven self‑improvement** – after a configurable number of failures, the bot asks the FreLLM model (via the user‑provided endpoint) to analyse recent failure logs and suggest concrete patches (e.g., alternate selectors, higher timeouts, retry logic). Patches are applied to the YAML config, making the bot self‑optimizing without code changes.
* **Structured logging + screenshots** – every event is written as a JSON line; on error a screenshot is saved, enabling post‑mortem analysis without disrupting the run.
* **Graceful shutdown via `STOP` file** – allows external orchestration (cron, systemd) to stop the bot cleanly.

## Pitfalls & how to avoid them
* **Headed mode required for Buster/Whisper**: The automation must run Chromium in headed mode; headless mode cannot load extensions like Buster or capture audio for Whisper. The script now enforces `headless: false` unless explicitly overridden.
* **Manual CAPTCHA fallback**: When automated solvers fail, the bot prompts for manual entry. If running in non‑interactive environments, ensure a `STOP` file is watched to allow graceful shutdown.
* **Counter handling**: `${counter}` placeholder must be present in `tiebreaker_question.value`; verify it is not accidentally overwritten during AI patching.
* **AI improvement trigger threshold**: The default `failure_threshold` is 10; adjust based on request volume to avoid excessive FreLLM calls.
* **File permission checks**: Ensure the process user can write to `config_v2.yaml` and `data/counter.json`; the skill now validates permissions before attempting patches.
* **Too frequent AI calls**: The threshold (`failure_threshold`) prevents spamming the FreLLM endpoint; tune it according to your quota.
* **Import path issues**: When running scripts from subdirectories, ensure Python can find the `src` module by adding it to `sys.path` or using proper relative/absolute imports.
* **Browser initialization**: Playwright contexts start with empty `pages[]`; use `context.new_page()` instead of `context.pages[0]` to get a valid page object.

## Verification
* **Unit‑level** – run `python -m pytest` on any extracted test files (none shipped yet, but you can add `tests/test_*.py`).
* **Integration** – run a single batch with `--batch 1` and confirm a submission appears in the target form and the counter increments.
* **Self‑improvement trigger** – force failures (e.g., point to a non‑existent form) and verify that after `failure_threshold` attempts the logs show an AI improvement event and the config changes.
* **Setup validation** – run `scripts/verify-setup.sh` to check for required binaries, permissions, and directory structure before launching.

## References
* Whisper.cpp: https://github.com/ggerganis/whisper.cpp
* Camoufox: https://github.com/camufox/camoufox
* Playwright: https://playwright.dev/
* Tesseract OCR: https://github.com/tesseract-ocr/tesseract
* ffmpeg: https://ffmpeg.org/
* FreLLM endpoint description: see the user’s custom endpoint `https://freellm.aldof.duckdns.org/v1` (compatible with OpenAI chat format).
* Implementation notes: see `references/implementation-notes.md` for session‑specific fixes and transcripts.

## User preferences encoded
* **Concise, direct responses** – the skill description is purpose‑focused; implementation avoids unnecessary commentary.
* **Self‑contained tasks** – each step can be executed independently; the skill provides all needed files and commands.
* **Evidence‑based validation** – the verification section insists on real runs, log inspection, and config diffs before claiming success.
* **No extra clarification questions** – the skill assumes the user will follow the listed steps; if any prerequisite is missing, the error messages are explicit.

## Pitfalls & Debugging Insights
- **Headed mode required for Buster/Whisper**: The automation must run Chromium in headed mode; headless mode cannot load extensions like Buster or capture audio for Whisper. The script now enforces `headless: false` unless explicitly overridden.
- **Manual CAPTCHA fallback**: When automated solvers fail, the bot prompts for manual entry. If running in non‑interactive environments, ensure a `STOP` file is watched to allow graceful shutdown.
* **Counter handling**: `${counter}` placeholder must be present in `tiebreaker_question.value`; verify it is not accidentally overwritten during AI patching.
- **AI improvement trigger threshold**: The default `failure_threshold` is 10; adjust based on request volume to avoid excessive FreLLM calls.
* **File permission checks**: Ensure the process user can write to `config_v2.yaml` and `data/counter.json`; the skill now validates permissions before attempting patches.
* **Too frequent AI calls**: The threshold (`failure_threshold`) prevents spamming the FreLLM endpoint; tune it according to your quota.
- **Import path issues**: When running scripts from subdirectories, ensure Python can find the `src` module by adding it to `sys.path` or using proper relative/absolute imports.
* **Browser initialization**: Playwright contexts start with empty `pages[]`; use `context.new_page()` instead of `context.pages[0]` to get a valid page object.

## Updated References
- Added `references/implementation-notes.md` with detailed error transcripts and reproduction steps.
- Added `scripts/verify-setup.sh` to pre‑flight check for required binaries and permissions.

*End of skill.*