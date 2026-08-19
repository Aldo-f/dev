---
name: headless-browser-automation
description: Automate browser actions in headless environments.
---

*   **Problem:** Automating browser interactions via `cua_driver` on headless systems (like Raspberry Pi OS) requires careful setup, as direct browser instances may not be readily available or discoverable.

*   **Scenario:** User requested web browsing on a headless Pi.

*   **Steps Taken:**
    1.  **Browser Installation:** Identified the need for a browser and installed `chromium-browser` using `sudo apt-get install -y chromium-browser`.
    2.  **Executable Discovery:** Used `find` command (`sudo find /usr -name chromium 2>/dev/null`) to locate the browser executable (`/usr/bin/chromium`).
    3.  **Background Launch:** Launched the browser in the background using `sudo /usr/bin/chromium &` via the `terminal` tool to obtain a PID.
    4.  **`cua_driver` Integration Attempt:** Tried to use `computer_use(action='cua_browser_prepare', pid=<PID>, profile_mode='isolated_new')`.

*   **Challenge Encountered:** The `cua_browser_prepare` action requires `allow_launch=True` for isolated setups, but this parameter cannot be passed directly to `cua_browser_prepare`. This prevents `cua_driver` from properly managing the launched browser instance in a headless context.

*   **Current Status:** Blocked due to the inability to satisfy the `allow_launch=True` requirement for `cua_browser_prepare`.

*   **Potential Solutions/Next Steps:**
    *   Investigate if `cua_driver` has an alternative method for initiating a controllable browser session in headless environments.
    *   Explore if launching the browser with specific flags or through a different mechanism might make it discoverable and controllable by `cua_driver`.
    *   Manual user intervention might be required to start the browser in a way that `cua_driver` can hook into.

*   **User Correction/Instruction:** User explicitly stated the system was headless and that a browser could be installed.

## reCAPTCHA v2 Invisible — Known Blocker (see `references/google-forms-recaptcha-v2-invisible.md`)

When automating Google Forms with reCAPTCHA v2 invisible (`size=invisible`, callback-based):
- Playwright + xvfb-run fills form fields correctly
- First submit triggers challenge in bframe iframe
- **Token handshake fails**: `grecaptcha.getResponse()` returns empty, `#g-recaptcha-response` stays empty, callback (`fpHtcb`) never fires
- Manual challenge solve doesn't complete submission — form stays on page, no `formResponse` POST
- **Workarounds needed**: `computer_use` with real browser profile, paid CAPTCHA API, or undetected-chromedriver

### Camoufox Anti-Detection Tested (v0.5.4)
- Same reCAPTCHA handshake failure — `fpHtcb` callback never fires in automation context
- Fingerprint masking works (form loads, fields fill), but token exchange still fails
- Challenge appears in bframe, manual solve doesn't dismiss challenge or trigger confirmation
- Camoufox fingerprint rotation + geoip spoofing insufficient for this reCAPTCHA variant

Reference: `references/google-forms-recaptcha-v2-invisible.md` — full reproduction steps and observations.

## Pitfall: Headless Chromium drops MV3 browser extensions
Playwright headless Chromium **silently ignores** `--load-extension`: the launch still succeeds and the page loads, but the extension's content scripts/background never run (no error, no log — just absent behavior). Confirmed empirically: an unpacked MV3 test extension produced zero `console` signals under `headless=True`, while the same extension loaded fine in a headed persistent context (confirmed via CDP `Target.getTargets` showing the `chrome-extension://…` service worker).

**Implications:**
- Any extension-dependent automation (captcha solvers like Buster, ad-blockers, custom content scripts) is **inert in headless Chromium**, however you launch it.
- To actually run a Chromium extension, use a **persistent context with `headless=False`** and pass both `--disable-extensions-except=<dir>` and `--load-extension=<dir>`.
- On a headless server, run that headed context under `xvfb-run -a` so it still works without a display. This is a valid, testable path — not a blocker.

See skill `buster-captcha-solver` for the full Buster sizing (Chrome vs Firefox XPI builds).
