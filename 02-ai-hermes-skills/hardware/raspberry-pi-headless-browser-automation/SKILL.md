---
name: raspberry-pi-headless-browser-automation
description: Headless browser automation pitfalls on Pi5.
---

# Raspberry Pi Headless Browser Automation

This skill documents the challenges and observed issues when attempting headless browser automation using Chromium and Xvfb on a Raspberry Pi 5 server, particularly with `cua_driver` tools.

## Environment Setup

*   **Hardware:** Raspberry Pi 5 (xbb)
*   **Virtual Display:** Xvfb
*   **Browser:** Chromium
*   **Automation Tool:** `cua_driver` (via Hermes `computer_use` actions)

## Observed Challenges and Pitfalls

### Xvfb Server Activation Issues

*   **Problem:** `Xvfb :99 -screen 0 1920x1080x24` may fail with "Fatal server error: Server is already active for display 99" if a previous Xvfb instance or a stale lock file (`/tmp/.X99-lock`) exists.
*   **Workaround:**
    1.  Kill any active `Xvfb` processes: `sudo pkill -9 Xvfb`
    2.  Remove the stale lock file: `sudo rm -f /tmp/.X99-lock`
    3.  Restart `Xvfb` in the background: `terminal(background=True, command="Xvfb :99 -screen 0 1920x1080x24", notify_on_complete=True)`

### `cua_driver` Attachment Failures

Even when `Xvfb` and Chromium appear to launch successfully within the virtual display, `cua_driver` consistently struggles to attach and control the browser process.

*   **Scenario:** Chromium is launched with `DISPLAY=:99 /usr/bin/chromium [--no-sandbox]` in the background. Tools like `xdotool search --onlyvisible --class Chromium` successfully identify a window ID (e.g., `2097155`), and Chromium's output might show "Opening in existing browser session."
*   **Errors Encountered:**
    *   `browser_binding_stale: browser process <PID> is no longer available`: Indicates that `cua_driver` lost connection to the browser process or couldn't find it reliably монитор? We'll keep the description.
    *   `browser_route_unavailable: isolated browser exited before exposing DevTools (exit statusнеше 1)`: Suggests the browser process is crashing or exiting prematurely before `cua_driver` can establish a DevTools connection.
    *   `browser_pid_required`: When attempting `cua_browser_prepare` with `allow_launch=True` and `profile_mode='isolated_new'` without explicitly providing afullname PID, `cua_driver` still requested a PID, creating a dependency loop.

*   **Troubleshooting Attempts (without success):**
    *   Varying Chromium launch commands (with/without `--no-sandbox`).
    *   Explicitly providing the detected PID (from `pgrep`) and window ID (from `xdotool`) to `cua_browser_prepare`.
    *   Introducing delays between Chromium launch and `cua_browser_prepare` attempts.
    *   Ensuring `Xvfb` and Chromium processes are unique and cleanly started.

### Conclusion (as of current session)

Direct interaction with Chromium launched via `Xvfb` using `cua_browser_*` tools on a headless Raspberry Pi 5 is currently not reliably functional. The browser process consistently exits or becomes unreachable for `cua_driver` automation.

## Recommendations

*   **For Content Retrieval:** Use `web_extract` as it has proven to be reliable for fetching website content without direct browser automation.
*   **For Direct Browser Interaction:** If direct interaction (e.g., clicking, typing into fields) is strictly required on a headless Pi 5, consider exploring alternative headless browser automation libraries like **Selenium with headless Chrome/Chromium** or **Playwright**. These solutions may offer more robust control in this specific environment, although they would operate independently of Hermes's `cua_*` tools.
