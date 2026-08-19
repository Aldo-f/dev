---
name: headless-gui-automation-xvfb
description: Set up Xvfb for headless GUI; note cua_driver integration.
trigger: Use when needing to run GUI apps (like browsers) on a headless server for automation.
---

# Headless GUI Automation with Xvfb and cua_driver

This skill details the process of setting up a virtual framebuffer (`Xvfb`) to run GUI applications (such as Chromium) on a headless server, and the observed difficulties in integrating `cua_driver` for automation.

## Workflow Overview

1.  **Install Dependencies:** Ensure necessary packages for GUI applications and virtual displays are installed.
2.  **Start Xvfb:** Launch a virtual X server instance in the background.
3.  **Launch GUI Application:** Run the target GUI application (e.g., Chromium) directed towards the virtual display.
4.  **Integrate with cua_driver:** Attempt to use `cua_driver` commands (`cua_browser_prepare`, `cua_browser_state`, etc.) to interact with the launched application.

## Steps and Commands

### 1. Install Dependencies
Install `xvfb`, `x11-utils`, and other essential libraries for GUI rendering.

```bash
sudo apt-get update && sudo apt-get install -y xvfb x11-utils libxcursor-dev libxcomposite-dev libxdamage-dev libxi-dev libxtst-dev libnss3 libxrandr2 libasound2 libpangocairo-1.0-0 libatk-bridge2.0-0 libgtk-3-0 libgbm1
```

### 2. Start Xvfb
Run `Xvfb` in the background, creating a virtual display (e.g., `:99`) with a specified resolution and color depth.

```bash
Xvfb :99 -screen 0 1920x1080x24 &
```

### 3. Launch GUI Application
Launch the GUI application, ensuring it uses the virtual display (`DISPLAY=:99`) and any necessary flags (e.g., `--no-sandbox` for Chromium when run with `sudo`).

```bash
# Example for Chromium
DISPLAY=:99 sudo /usr/bin/chromium --no-sandbox &
```
*Note: Ensure Chromium executable path is correct and use `sudo` if required.*

### 4. Integrate with cua_driver (Challenges and Observations)

During integration attempts, the following issues were encountered:

*   **Window Detection Failure:** `cua_driver` commands like `list_windows` often return empty, or `capture` fails with "capture targeting requires both pid and window_id". This indicates `cua_driver` is not reliably detecting windows created by `Xvfb`.
*   **Binding Errors:** Attempts to attach to the browser process using `cua_browser_prepare` or `cua_browser_state` with a PID failed with errors like:
    *   `browser_launch_not_approved`: Requires `allow_launch=true` for isolated profiles, which may not be directly configurable for `cua_browser_prepare`.
    *   `browser_exact_target_required`: Needs an exact PID and window ID pair, which `cua_driver` fails to provide.
    *   `browser_binding_stale`: Indicates that the identified window (if any) is not correctly associated with the process.

*   **PID Identification:** Finding the correct PID for the GUI application might require careful use of `pgrep` or `find`.

*   **`allow_launch=True` for `cua_browser_prepare`:** This parameter appears crucial for launching new browser instances but is not directly supported by `cua_browser_prepare` in the current `computer_use` tool schema.

*   **`web_extract` Backend:** While `web.backend: firecrawl` is set in `~/.hermes/config.yaml`, `web_extract` might require `web.extract_backend: firecrawl` to be explicitly defined.

## Pitfalls & Workarounds

*   **Headless Environment:** GUI applications require a virtual display server like `Xvfb`.
*   **`cua_driver` Integration:** The primary challenge is establishing a reliable connection between `cua_driver` and GUI windows managed by `Xvfb`. Further investigation into `cua_driver`'s X11 integration or alternative headless browser automation tools might be necessary if direct `cua_*` command usage remains elusive.
*   **Permissions:** Running GUI apps as root might require `--no-sandbox`.
*   **Configuration:** Ensure `.env` files and other configurations are correctly set up for the applications running within the `Xvfb` environment.

## Related Skills

*   `headless-server-setup` (hypothetical)
*   `browser-automation-troubleshooting` (hypothetical)

## Notes for Future Sessions

*   If `cua_driver` integration remains problematic with `Xvfb`, consider alternative web scraping libraries (`requests`, `BeautifulSoup` via `execute_code`) if only data extraction is needed.
*   Explore if there are specific `cua_driver` configurations or alternative methods to establish a connection to Xvfb-created windows.
