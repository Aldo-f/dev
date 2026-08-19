# Buster Mozilla XPI Installation Guide

## Overview
This guide documents the recommended method for installing the Buster captcha solver extension on Firefox using the official Mozilla Add-ons package. This process resolves the `InvalidAddonPath` error encountered when attempting to use a source-built npm package on ARM architectures.

## Prerequisites
- Python 3.8+
- wget or curl
- unzip utility
- Access to the `tmp` directory in the form-automation project

## Installation Steps
1. **Clean existing installation artifacts**:
   ```bash
   rm -rf ~/scripts/form-automation/tmp/buster_firefox
   ```

2. **Download the official XPI package**:
   ```bash
   cd ~/scripts/form-automation/tmp
   wget -O buster.xpi "https://addons.mozilla.org/firefox/downloads/latest/buster-captcha-solver/latest.xpi"
   ```

3. **Extract the XPI contents**:
   ```bash
   unzip -o buster.xpi -d buster_firefox
   ```

4. **Verify the installation**:
   ```bash
   ls -l buster_firefox/manifest.json
   # Expected output: -rw-r--r-- 1 user user 1234 Jun 1 12:34 buster_firefox/manifest.json
   ```

## Integration with Camoufox
When starting the browser automation instance, specify the extracted directory:

```python
self.camoufox = Camoufox(
    headless=self.headless,
    addons=[str(BASE_DIR / 'tmp' / 'buster_firefox')]
)
```

## Troubleshooting
- **InvalidAddonPath**: Ensure `manifest.json` exists and is valid
- **Path resolution**: Use absolute paths or `BASE_DIR` reference
- **Version compatibility**: Use latest Buster version from Mozilla Add-ons
- **Architecture issues**: Direct XPI download resolves arm64 compatibility problems

## Verification
After installation, run:
```bash
python auto_form_camoufox.py --test-buster
```
The script should detect the Buster UI on the reCAPTCHA demo page.