---
name: headless-linux-browser-automation
category: troubleshooting
description: Make cua_* browser tools work on headless Linux (Xvfb + systemd DISPLAY).

tags:
  - cua_driver
  - Xvfb
  - headless
  - browser
  - automation
  - linux
  - raspberrypi
trigger: Use when cua_* browser automation fails on a headless Linux server, especially with Xvfb, or when Camoufox/Buster automation needs headless CAPTCHA handling.
---
# Headless Linux cua_* Browser Automation (SOLVED)

**Root cause of all `browser_binding_stale` / `browser_route_unavailable` / `browser_pid_required` failures on headless Linux: the cua-driver MCP child process had no `DISPLAY`. The driver inherits the env of the process that spawns it (Hermes WebUI server or gateway). On a headless box that env has no `DISPLAY`, so the driver cannot reach any X server — its own isolated Chromium dies instantly with `exit status: 1` before exposing DevTools.**

## The Fix (persistent, reboot-safe)

1. **Xvfb as a systemd service** — `/etc/systemd/system/xvfb.service`:
   ```ini
   [Unit]
   Description=Xvfb virtual display
   After=network.target

   [Service]
   Type=simple
   User=aldo
   ExecStart=/usr/bin/Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```
   `sudo systemctl enable --now xvfb.service`

2. **Give every Hermes service `DISPLAY=:99`** — add to the WebUI unit (`/etc/systemd/system/app-hermes-webui.service`) and the gateway unit/drop-in (`~/.config/systemd/user/hermes-gateway.service.d/*.conf` via `EnvironmentFile=%h/.hermes/.env` or `Environment=`):
   ``` 
   Environment=DISPLAY=:99
   Environment=HERMES_WEBUI_HOST=0.0.0.0
   ```
   Restart both services. Verify with `tr '\\0' '\\n' < /proc/<pid>/environ | grep DISPLAY` and `hermes computer-use doctor` — it must print `ax_capability: X11 reachable` and `screen_capture_capability: X11 reachable` with **ok** status.

## Working cua_* Flow (proven on Pi 5, arm64, Debian trixie)

1. **Launch a seed browser on :99** (the driver needs a live `pid`+`window_id` anchor):
   ```bash
   DISPLAY=:99 /usr/bin/chromium --no-sandbox --disable-gpu &
   ```
2. **Get the window owner pid** — critical pitfall: `pgrep -f chromium` returns transient helper pids that die. Use `xdotool`:
   ```bash
   export DISPLAY=:99
   WID=$(xdotool search --onlyvisible --class Chromium | head -1)
   PID=$(xdotool getwindowpid \"$WID\")   # the MAIN browser process
   ```
3. **Prepare** — driver launches its OWN isolated browser (needs `allow_launch=true` + `isolated_new`):
   `cua_browser_prepare(pid=PID, window_id=WID, allow_launch=true, profile_mode=\"isolated_new\")` → returns `prepared_pid` (e.g. 9202), status ok.
4. **Find the driver browser window** — it is NOT the seed window. List windows by owner pid:
   ```
   for w in $(xdotool search --onlyvisible --name \".\"); do echo \"$w $(xdotool getwindowpid $w) $(xdotool getwindowname $w)\"; done
   ```
   The driver window has `about:blank - Chromium` title and is owned by `prepared_pid`. (A `Cua.AgentCursorOverlay.default` window also exists — that is the cursor overlay, not the browser.)  
   **Camoufox note:** When using Camoufox as the seed browser, replace `chromium` with `firefox --headless --show-label` and ensure the `--load-extension=.../buster_firefox` path is correct; the extension loads in headless mode but may be unreliable on some evasion checks.

5. **Bind exactly** — `cua_browser_state(pid=prepared_pid, window_id=driver_wid)` → `binding_quality: \"exact\"`, `mutation_allowed: true`, mints a **fresh tab_id** (new id on every bind call).
6. **Snapshot before first mutation** — `cua_browser_state(tab_id=<current tab_id>)` (NO pid/window_id → snapshot mode). Clears `verification_required`.
7. **Mutate** — `cua_browser_navigate(tab_id=<current tab_id>, url=...)`, then `cua_browser_click(ref=...)`, etc.

## New Camoufox‑specific pitfalls added by this session

- **CAPTCHA solved but submission still fails** – Buster can solve the challenge in headless mode, but Google Forms may still reject the POST if the submission occurs before the final confirmation overlay disappears. Insert a `time.sleep(2)` after `wait_for_challenge_solved` or wait for the selector `div[aria-label='Submit success']` before clicking submit again.
- **Selector drift after CAPTCHA** – The DOM can change *after* the challenge is solved (e.g., a new reCAPTCHA widget is injected). Reload the selector map from `config.yaml` immediately before the second click, rather than re‑using the stale Selenium element reference.
- **Headless Buster extension load order** – On some Pi 5 OS builds the extension is not loaded early enough when using `addons=[...]` in headless mode. Force the load by passing `--load-extension=/home/aldo/scripts/form-automation/tmp/buster_firefox` explicitly in the Camoufox launch command, then verify with `browser_vision question: "show overlay for captcha solved"` before proceeding.
- **Driver env mismatch** – When using Camoufox the `DISPLAY` variable must be exported *in the same shell* that runs `cua_browser_prepare`. If you spawn a background process (e.g., via `systemd`), the child may lose the variable and the driver will abort with `browser_route_unavailable`. Use `Environment=DISPLAY=:99` in the systemd service that starts the Camoufox automation script.

## Verification

```bash
hermes computer-use doctor        # must be all ✅, ax + screen capture “X11 reachable”
xdotool search --onlyvisible --class Chromium
```

</details>

### Add linked reference for this update

Create a reference file that records the exact session‑specific error transcript and debugging steps that led to the Camoufox‑headless patch.

</details>

<references>

</references>

*Update guidance*: Keep this skill under version control (`git add` in `~/.hermes/skills/...`) and tag the commit with `headless-camoufox-update-20260806` so future agents can retrieve the exact state that fixed the test run.
</references>