---
name: headless-cua-browser-setup
category: hardware
description: "Reinstall cua_* browser tools on a headless Linux server."
tags:
  - cua_driver
  - Xvfb
  - headless
  - raspberrypi
  - systemd
  - reinstall
  - runbook
trigger: Use when reinstalling or setting up cua_* computer-use browser tools on a headless Linux server (e.g. fresh Pi 5 image).
---
# Headless cua_* Browser Setup — Reinstall Runbook

Verified working on: Raspberry Pi 5, arm64, Debian 13 (trixie), cua-driver 0.14.1, Chromium from `chromium-browser` apt package, Hermes WebUI + gateway.

**The one thing that makes it all work: every Hermes process that spawns cua-driver must have `DISPLAY=:99` in its environment.** cua-driver inherits env from its parent; without DISPLAY it cannot reach X11 and its own isolated Chromium dies at launch (`browser_route_unavailable`, `browser_binding_stale`). Everything below exists to make DISPLAY persist across reboots.

## 1. Install packages

```bash
sudo apt-get update
sudo apt-get install -y xvfb xauth xdotool wmctrl imagemagick chromium-browser
# cua-driver itself: check with  hermes computer-use doctor
# if missing: hermes computer-use install  (or install.sh from trycua/cua repo)
```

## 2. Xvfb as a systemd service

Create `/etc/systemd/system/xvfb.service`:

```ini
[Unit]
Description=Xvfb virtual display :99 for headless GUI (cua-driver / computer use)
After=network.target

[Service]
Type=simple
User=aldo
ExecStartPre=/bin/rm -f /tmp/.X99-lock
ExecStart=/usr/bin/Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now xvfb.service
systemctl is-active xvfb.service   # → active
```

(`ExecStartPre` removes stale `/tmp/.X99-lock` — kills the classic "Server is already active for display 99" reboot loop.)

## 3. DISPLAY on the Hermes WebUI service

`/etc/systemd/system/app-hermes-webui.service` (system unit, `User=aldo`):

```ini
[Unit]
Description=Hermes WebUI daemon
After=network.target xvfb.service
Wants=xvfb.service

[Service]
Type=simple
User=aldo
WorkingDirectory=/home/aldo/dev/02-ai-hermes-webui
ExecStart=/home/aldo/.hermes/hermes-agent/venv/bin/python /home/aldo/dev/02-ai-hermes-webui/server.py
Restart=on-failure
RestartSec=5
Environment=HERMES_HOME=/home/aldo/.hermes
Environment=HERMES_WEBUI_HOST=0.0.0.0
Environment=DISPLAY=:99

[Install]
WantedBy=multi-user.target
```

## 4. DISPLAY on the Hermes gateway (user unit)

Drop-in `~/.config/systemd/user/hermes-gateway.service.d/override.conf`:

```ini
[Service]
Environment="API_SERVER_ENABLED=true" "API_SERVER_HOST=0.0.0.0"
Environment="DASHBOARD_HOST=0.0.0.0"
Environment="DISPLAY=:99"
EnvironmentFile=%h/.hermes/.env
After=xvfb.service
Wants=xvfb.service
```

Apply (user bus env vars needed from a root/system shell):

```bash
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
export XDG_RUNTIME_DIR=/run/user/$(id -u)
systemctl --user daemon-reload
systemctl --user restart hermes-gateway.service
```

(Do NOT put DISPLAY in `~/.hermes/.env` — that file is for secrets only.)

## 5. Restart + verify

```bash
sudo systemctl restart app-hermes-webui.service
hermes computer-use doctor
```

Doctor must end with **ok** and show:
- `✅ ax_capability: X11 reachable and org.a11y.Bus is on the session bus; AT-SPI inspection + XSendEvent input will work.`
- `✅ screen_capture_capability: X11 reachable; screen capture path is functional.`

Process-env check (both webui + gateway PIDs must show DISPLAY=:99):
```bash
tr '\0' '\n' < /proc/<pid>/environ | grep DISPLAY
```

## 6. Using the cua_* tools (proven flow)

1. **Seed browser** (anchor window for the driver):
   ```bash
   DISPLAY=:99 /usr/bin/chromium --no-sandbox --disable-gpu &
   ```
2. **Get the window owner pid — NOT pgrep** (pgrep returns transient helper pids):
   ```bash
   export DISPLAY=:99
   WID=$(xdotool search --onlyvisible --class Chromium | head -1)
   PID=$(xdotool getwindowpid "$WID")   # main browser process
   ```
3. **`cua_browser_prepare(pid=PID, window_id=WID, allow_launch=true, profile_mode="isolated_new")`**
   → driver launches its OWN isolated Chromium; returns `prepared_pid`. Status `ok`.
4. **Find the driver browser window** (NOT the seed window):
   ```bash
   for w in $(xdotool search --onlyvisible --name "."); do
     echo "$w $(xdotool getwindowpid $w) $(xdotool getwindowname $w)"
   done
   ```
   Driver window: title `about:blank - Chromium`, owner = `prepared_pid`.
   Ignore `Cua.AgentCursorOverlay.default` (cursor overlay, no pid).
5. **Bind**: `cua_browser_state(pid=prepared_pid, window_id=driver_wid)` → `binding_quality:"exact"`, `mutation_allowed:true`, mints a fresh tab_id.
6. **Snapshot** (unlocks mutations): `cua_browser_state(tab_id=<current tab_id>)` — NO pid/window_id.
7. **Mutate**: `cua_browser_navigate(tab_id=..., url=...)` → then fresh snapshot → `cua_browser_click(ref=...)` etc.

Every successful bind mints NEW tab_ids — always use the latest one. After every mutation, take a fresh snapshot (`verification_required` gate).

## 7. Pitfalls (fast reference — details in skill `headless-linux-browser-automation`)

| Symptom | Cause / fix |
|---|---|
| `browser_route_unavailable ... exit status: 1` | Driver's Chromium crashed at launch → missing DISPLAY in driver env. Fix: steps 3–4. |
| `browser_pid_required` | pid is mandatory even for isolated_new. Pass the seed window's owner pid. |
| `browser_binding_stale: process X no longer available` | X was a chromium helper (zygote/renderer). Use `xdotool getwindowpid`. |
| `browser_verification_required` | Bind ≠ snapshot. Call state with tab_id only. |
| `browser_tab_unbound` | tab_id from an older bind. Re-read latest bind/snapshot. |
| `Xvfb: Server is already active for display 99` | Stale lock; `sudo pkill -9 Xvfb; sudo rm -f /tmp/.X99-lock` (service's ExecStartPre does this automatically). |
| GPU/GCM log errors (`GpuControl.CreateCommandBuffer`, `DEPRECATED_ENDPOINT`) | Harmless on Pi with `--disable-gpu`; automation still works. |

## Verification (post-reinstall checklist)

```bash
systemctl is-active xvfb.service app-hermes-webui.service      # active
hermes computer-use doctor                                     # all ✅
export DISPLAY=:99 && xdotool search --onlyvisible --class Chromium  # after seeding browser
```
