# Firefox Buster manifest.json Verification

After cloning the Buster Firefox repo, verify the addon structure:

```bash
# Check manifest exists
ls -la tmp/buster_firefox/manifest.json

# Expected structure:
# tmp/buster_firefox/
#   ├── manifest.json       <-- required by Camoufox
#   ├── background.js
#   ├── content.js
#   └── icons/
```

If `manifest.json` is missing:
1. The GitHub clone may be incomplete
2. Download the official XPI from AMO instead:
   ```bash
   # From open_camoufox_with_buster.py:
   wget "https://addons.mozilla.org/firefox/downloads/latest/buster-captcha-solver/latest.xpi" -O buster.xpi
   unzip buster.xpi -d tmp/buster_firefox
   ```

Camoufox will throw `InvalidAddonPath: manifest.json is missing` if this file is absent at the addon root.