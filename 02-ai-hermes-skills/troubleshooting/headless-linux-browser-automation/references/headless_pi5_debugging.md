## Headless Linux Browser Automation Debugging Session

**Date:** [Current Date]

**Environment:** Headless Raspberry Pi 5, Linux, Xvfb

**Goal:** Make cua_* browser tools functional.

**Summary of Issues:**
Persistent errors like `browser_binding_stale`, `browser_route_unavailable`, and `browser_pid_required` when trying to attach cua_driver to a browser launched via Xvfb.

**Key Commands and Outputs:**

1.  **Installing inspection tools:**
    ```bash
    sudo apt-get update && sudo apt-get install -y xdotool wmctrl
    ```
    *Output:* Success.

2.  **Starting Xvfb:**
    ```bash
    Xvfb :99 -screen 0 1920x1080x24 &
    ```
    *Output:* Background process started (PID might vary).

3.  **Launching Chromium (various attempts):**
    *   `DISPLAY=:99 /usr/bin/chromium --no-sandbox &`
    *   `DISPLAY=:99 /usr/bin/chromium &`
    *   `/usr/bin/chromium --no-sandbox &`

4.  **Inspecting windows with `xdotool`:**
    ```bash
    export DISPLAY=:99 && xdotool search --onlyvisible --class Chromium
    ```
    *Example Output (Success):* `2097155`
    *Example Output (Failure):* (empty)

5.  **Attempting `cua_browser_prepare`:**
    *   `computer_use(action = "cua_browser_prepare", allow_launch = True, pid = <PID>, profile_mode = "isolated_new", window_id = <WindowID>)
    *   `computer_use(action = "cua_browser_prepare", allow_launch = True, pid = <PID>, profile_mode = "isolated_new")`

    **Observed Errors:**
    *   `refused (browser_binding_stale): browser process <PID> is no longer available`
    *   `refused (browser_route_unavailable): isolated browser exited before exposing DevTools (exit status: 1)`
    *   `refused (browser_pid_required): browser_prepare requires a positive pid.`

**Conclusions:**

-   Directly controlling browsers launched via Xvfb with `cua_*` tools is unreliable on this setup.
-   `web_extract` remains a viable alternative for content retrieval.

**Recommendations:**

-   Consult `cua_driver` documentation for headless Linux.
-   Explore alternative headless browser automation libraries (Playwright, Puppeteer).
