# Buster Chrome Install
The Chrome build of Buster is distributed as a zip file in the official dessant/buster GitHub releases.

```bash
cd $(git rev-parse --show-toplevel)/scripts/form-automation
# Download and unpack (performed automatically by ensure_buster_chrome_installed())
# The helper uses:
#   URL: https://github.com/dessant/buster/releases/download/v3.4.0/buster_captcha_solver_for_humans-3.4.0-chrome.zip
#   Destination: tmp/buster_chrome
```
The directory must contain a `manifest.json` (MV3) for Chrome to load the extension.