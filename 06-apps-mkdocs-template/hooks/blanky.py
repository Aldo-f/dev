"""MkDocs hook: copy js-blanky UMD bundle and inject external-link opener.

Copies the installed npm package `js-blanky` UMD build into the site assets
and wires an init script that opens all external links in a new tab/window.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PKG_JS = REPO_ROOT / "node_modules" / "js-blanky" / "dist" / "blanky.umd.js"
JS_NAME = "assets/javascripts/blanky.umd.js"
INIT_JS = "assets/javascripts/blanky-init.js"


def on_post_build(*, config, **kwargs):
    site_dir = Path(config.site_dir)

    if not PKG_JS.is_file():
        raise FileNotFoundError(
            f"js-blanky not installed at {PKG_JS}. Run `npm install js-blanky`."
        )

    # Copy blanky UMD bundle from node_modules
    js_path = site_dir / JS_NAME
    js_path.parent.mkdir(parents=True, exist_ok=True)
    js_path.write_bytes(PKG_JS.read_bytes())

    # Write init script
    init_path = site_dir / INIT_JS
    init_path.write_text(
        "window.blanky.blanky({ blank: true, noopener: true, nofollow: false });\n",
        encoding="utf-8",
    )
    print(f"blanky: wrote {js_path.name} + {init_path.name}")


def on_config(config, **kwargs):
    extra_js = list(config.get("extra_javascript") or [])
    if JS_NAME not in extra_js:
        extra_js.append(JS_NAME)
    if INIT_JS not in extra_js:
        extra_js.append(INIT_JS)
    config["extra_javascript"] = extra_js
    return config
