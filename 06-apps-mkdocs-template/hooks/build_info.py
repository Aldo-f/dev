"""MkDocs hook: writes a build timestamp file injected into the site footer.

Produces site/build-info.js exposing BUILD_TIME as a UTC ISO string (rounded
to the minute so the value is stable across reruns without CI cache invalidation).

Also emits build-footer.js which reads BUILD_TIME and stamps the footer.

Wired via `hooks:` in mkdocs.base.yml; runs on both EN and NL builds.
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JS_NAME = "assets/javascripts/build-info.js"
FOOTER_JS = "assets/javascripts/build-footer.js"


def on_post_build(*, config, **kwargs):
    site_dir = Path(config.site_dir)

    js_path = site_dir / JS_NAME
    js_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)
    js_path.write_text(
        f"BUILD_TIME = {now.isoformat(timespec='seconds')!r};",
        encoding="utf-8",
    )

    footer_path = site_dir / FOOTER_JS
    footer_path.parent.mkdir(parents=True, exist_ok=True)
    footer_path.write_text(
        """\
(function () {
  'use strict';
  var raw = typeof BUILD_TIME !== 'undefined' ? BUILD_TIME : null;
  if (!raw) return;
  var d = new Date(raw);
  var formatted = d.getFullYear() + '-' +
    String(d.getMonth()+1).padStart(2,'0') + '-' +
    String(d.getDate()).padStart(2,'0') + ' ' +
    String(d.getHours()).padStart(2,'0') + ':' +
    String(d.getMinutes()).padStart(2,'0') + ' ' +
    d.toLocaleTimeString(undefined, {timeZoneName:'short'});
  var el = document.getElementById('build-timestamp');
  if (el) el.textContent = '— Build ' + formatted;
})();
""",
        encoding="utf-8",
    )

    print(
        f"build-info: wrote {js_path.relative_to(site_dir)} and {footer_path.relative_to(site_dir)} = {now.isoformat()}"
    )


def on_config(config, **kwargs):
    extra_js = list(config.get("extra_javascript") or [])
    if JS_NAME not in extra_js:
        extra_js.append(JS_NAME)
    if FOOTER_JS not in extra_js:
        extra_js.append(FOOTER_JS)
    config["extra_javascript"] = extra_js
    return config
