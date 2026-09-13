"""MkDocs hook: same-page language switching via a slug map (feature 004).

Runs inside BOTH language builds (wired via `hooks:` in mkdocs.*.yml):

1. on_config  — registers the emitted slug-switch.js in extra_javascript so
                it ships with the build.
2. on_post_build — scans docs/<en>/ and docs/<nl>/ blog posts, pairs mirrors
                by filename, slugifies titles with Material's own default
                slugifier (byte-parity with real URLs), writes site/slugmap.json.

The JS intercepts clicks on the language selector: if the current URL is in
the map, navigate to the twin page; otherwise fall back to the link's default
target (the other language's home).
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

from pymdownx.slugs import slugify

SLUGIFY = slugify(case="lower")
SEPARATOR = "-"
REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ("en", "nl")

JS_NAME = "assets/javascripts/slug-switch.js"

_SWITCH_JS = """\
(function () {
  'use strict';
  var map = null;
  fetch('/slugmap.json', { cache: 'no-cache' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (j) { map = j; })
    .catch(function () { map = null; });

  function currentPath() {
    var p = location.pathname;
    p = p.replace(/index\\.html$/, '');
    if (p.length > 1 && !p.endsWith('/')) p += '/';
    return p;
  }

  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a[hreflang]');
    if (!a || !map) return;
    var target = map[currentPath()];
    if (target && target !== currentPath()) {
      ev.preventDefault();
      location.assign(target);
    }
  }, true);
})();
"""


def slugifier():
    """Expose the exact default slugifier for parity tests."""
    return SLUGIFY


def _parse_post(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.DOTALL)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        s = line.strip()
        if ":" in s and not s.startswith("-"):
            k, _, v = s.partition(":")
            meta[k.strip().lower()] = v.strip().strip("'\"")
    return meta


def build_map(root: Path) -> dict[str, str]:
    """Pair mirrored posts by filename; return URL-path -> URL-path map."""
    trees: dict[str, dict[str, dict]] = {}
    for lang in LANGS:
        d = root / "docs" / lang / "blog" / "posts"
        items: dict[str, dict] = {}
        for p in sorted(d.glob("*.md")) if d.is_dir() else []:
            meta = _parse_post(p)
            if not meta:
                continue
            if meta.get("draft", "").lower() == "true":
                continue
            date = meta.get("date", "")[:10]
            try:
                d = datetime.date.fromisoformat(date)
            except ValueError:
                continue
            slug = SLUGIFY(meta.get("title", ""), SEPARATOR)
            items[p.stem] = {
                "url": f"/{lang == 'nl' and 'nl/' or ''}blog/{d.year:04d}/{d.month:02d}/{d.day:02d}/{slug}/"
            }
        trees[lang] = items

    mapping: dict[str, str] = {}
    for src, dst in (("en", "nl"), ("nl", "en")):
        for stem, card in trees[src].items():
            if stem in trees[dst]:
                mapping[card["url"]] = trees[dst][stem]["url"]
    return mapping


def write_site(root: Path, out_path: Path) -> int:
    mapping = build_map(root)
    # merge over any existing file (second build adds its view; union is
    # identical because both builds scan both trees)
    existing = {}
    if out_path.is_file():
        try:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
    merged = {**existing, **mapping}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(merged, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return len(merged)


# --------------------------------------------------------------------------
# MkDocs hooks API
# --------------------------------------------------------------------------


def on_config(config, **_kwargs):
    extra = list(config.get("extra_javascript") or [])
    if JS_NAME not in extra:
        extra.append(JS_NAME)
    config["extra_javascript"] = extra
    return config


def on_post_build(config, **_kwargs):
    # repo root holds docs/en + docs/nl; site dir receives slugmap.json
    n = write_site(REPO_ROOT, Path(config.site_dir) / "slugmap.json")
    js_path = Path(config.site_dir) / JS_NAME
    js_path.parent.mkdir(parents=True, exist_ok=True)
    js_path.write_text(_SWITCH_JS, encoding="utf-8")

    # Material renders its own generic 404.html; our custom 404.md pages are
    # built as regular pages (404/index.html). Promote the language-appropriate
    # one to the root 404.html so dead links get a styled, localized page.
    site = Path(config.site_dir)
    lang = "nl" if str(site).endswith("/nl") else "en"
    custom = site / "404" / "index.html"
    if custom.exists():
        (site / "404.html").write_text(
            custom.read_text(encoding="utf-8"), encoding="utf-8"
        )
        print(f"404: promoted {lang} custom page to 404.html")

    print(f"slugmap: wrote {n} mirror entries + {JS_NAME}")
