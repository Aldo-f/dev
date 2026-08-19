# Buster Firefox Install
The Firefox version of Buster is an XPI file.

```bash
cd $(git rev-parse --show-toplevel)/scripts/form-automation
# The helper `ensure_buster_installed()` pulls the XPI from:
#   https://addons.mozilla.org/firefox/downloads/latest/buster-captcha-solver/addon-<id>.xpi
#   Destination: tmp/buster_firefox (unzipped folder with manifest.json)
```
Camoufox loads this folder via its `addons` argument.