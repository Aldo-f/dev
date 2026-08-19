# Verify Buster Chrome extension is loaded in Playwright
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir="/tmp/verify_buster_profile",
        headless=False,
        args=["--disable-extensions-except=/home/aldo/scripts/form-automation/tmp/buster_chrome",
              "--load-extension=/home/aldo/scripts/form-automation/tmp/buster_chrome"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    cdp = ctx.new_cdp_session(page)
    targets = cdp.send("Target.getTargets")
    ext_targets = [t for t in targets.get("targetInfos", []) if t.get("type") == "service_worker" and "chrome-extension" in (t.get("url") or "")]
    print("Buster service workers found:", len(ext_targets))
    for t in ext_targets:
        print(t.get("url"))
    ctx.close()