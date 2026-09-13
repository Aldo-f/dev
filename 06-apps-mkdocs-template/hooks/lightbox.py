"""MkDocs hook: full-page lightbox for images and mermaid SVGs.

Runs inside BOTH language builds (wired via `hooks:` in mkdocs.base.yml).
Emits assets/javascripts/lightbox.js + assets/css/lightbox.css into the
site dir and registers them via extra_javascript / extra_css.

Behavior:
- Click any content <img> or a rendered .mermaid <svg> -> fullscreen overlay.
- Mermaid SVGs are cloned at natural size with a white background so small
  diagrams become readable; overlay scrolls if the diagram exceeds the screen.
- Esc, overlay-click or close-button dismisses it.
"""

from __future__ import annotations

from pathlib import Path

JS_NAME = "assets/javascripts/lightbox.js"
CSS_NAME = "assets/css/lightbox.css"

_LIGHTBOX_JS = """(function () {
  'use strict';

  var overlay = null;

  function ensureOverlay() {
    if (overlay) return overlay;
    overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';
    overlay.innerHTML =
      '<button class="lightbox-close" aria-label="Close">&#10005;</button>' +
      '<div class="lightbox-content"></div>';
    document.body.appendChild(overlay);
    overlay.addEventListener('click', function (ev) {
      if (ev.target === overlay || ev.target.closest('.lightbox-close')) {
        closeLightbox();
      }
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') closeLightbox();
    });
    return overlay;
  }

  function closeLightbox() {
    if (overlay) {
      overlay.classList.remove('open');
      overlay.querySelector('.lightbox-content').innerHTML = '';
    }
  }

  function openImage(src, alt) {
    var box = ensureOverlay();
    var img = document.createElement('img');
    img.src = src;
    img.alt = alt || '';
    var content = box.querySelector('.lightbox-content');
    content.innerHTML = '';
    content.appendChild(img);
    box.classList.add('open');
  }

  function openSvg(svg) {
    var box = ensureOverlay();
    var clone = svg.cloneNode(true);
    clone.removeAttribute('style'); // drop page-fit sizing constraints
    clone.style.maxWidth = 'none';
    clone.style.width = '';
    clone.style.maxWidth = '';
    var wrap = document.createElement('div');
    wrap.className = 'lightbox-svg';
    wrap.appendChild(clone);
    var content = box.querySelector('.lightbox-content');
    content.innerHTML = '';
    content.appendChild(wrap);
    box.classList.add('open', 'has-svg');
  }

  function findSvg(node) {
    // click target may be the svg itself, a child element, or a wrapper div
    // Also need to check for shadow roots in mermaid elements
    if (!node.closest) return null;

    // Check direct matches first
    var directSvg = node.closest('svg.mermaid');
    if (directSvg) return directSvg;

    var directMermaid = node.closest('.mermaid');
    if (directMermaid) {
      // Check if this mermaid element has a shadow root with SVG inside
      if (directMermaid.shadowRoot) {
        var svgInShadow = directMermaid.shadowRoot.querySelector('svg');
        if (svgInShadow) return svgInShadow;
      }
      // Fallback to the mermaid element itself
      return directMermaid;
    }

    var directSvgAny = node.closest('svg');
    return directSvgAny;
  }

  function isInteractiveElement(el) {
    if (!el || !(el instanceof Element)) return false;
    var tag = el.tagName.toLowerCase();
    // Native interactive elements
    if (['a', 'button', 'input', 'select', 'textarea', 'label', 'summary'].includes(tag)) return true;
    // Elements with explicit interactive roles
    if (el.getAttribute('role') === 'button' || el.getAttribute('role') === 'link') return true;
    // Elements with onclick or tabindex (likely interactive)
    if (el.hasAttribute('onclick') || el.hasAttribute('tabindex')) return true;
    // Material theme nav elements
    if (el.closest('.md-nav, .md-header, .md-tabs, .md-breadcrumbs, .md-footer')) return true;
    // Any element inside a link or button (covers img, svg, span, etc.)
    if (el.closest('a, button, input, select, textarea, label, summary')) return true;
    return false;
  }

  document.addEventListener('click', function (ev) {
    var t = ev.target;
    if (!(t instanceof Element)) return;
    if (t.closest('.lightbox-overlay')) return;
    if (isInteractiveElement(t)) return; // let all interactive elements behave normally

    if (t.tagName === 'IMG' && t.closest('.md-content')) {
      ev.preventDefault();
      openImage(t.currentSrc || t.src, t.alt);
      return;
    }
    var svgHit = findSvg(t);
    if (svgHit) {
      var mermaidRoot = svgHit.closest('.mermaid') || svgHit;
      var inner = mermaidRoot.querySelector('svg') || svgHit;
      // If inner is still not an SVG, try to find SVG in shadow root
      if (!(inner instanceof SVGElement) && mermaidRoot.shadowRoot) {
        var svgInShadow = mermaidRoot.shadowRoot.querySelector('svg');
        if (svgInShadow) {
          inner = svgInShadow;
        } else {
          // Shadow root exists but is empty (rendering not complete yet)
          // We'll try again after a short delay
          setTimeout(function() {
            if (mermaidRoot && mermaidRoot.shadowRoot) {
              var retrySvg = mermaidRoot.shadowRoot.querySelector('svg');
              if (retrySvg && retrySvg instanceof SVGElement) {
                ev.preventDefault();
                openSvg(retrySvg);
              } else {
                // Fallback to using the mermaid div itself if still no SVG after delay
                ev.preventDefault();
                openSvg(inner);
              }
            } else {
              // Fallback to using the mermaid div itself
              ev.preventDefault();
              openSvg(inner);
            }
          }, 100); // 100ms delay
          return; // Important: return early to avoid double-processing
        }
      }
      ev.preventDefault();
      openSvg(inner);
    }
  }, true);

  // Cursor hint on hover
  var style = document.createElement('style');
  style.textContent = '.md-content img, .mermaid svg { cursor: zoom-in; }';
  document.head.appendChild(style);
})();"""

_LIGHTBOX_CSS = """.lightbox-overlay {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.85);
  padding: 2rem;
}
.lightbox-overlay.open {
  display: flex;
  align-items: center;
  justify-content: center;
}
.lightbox-overlay.open.has-svg {
  display: block;
  overflow: auto;
}
.lightbox-content img {
  max-width: 96vw;
  max-height: 92vh;
  box-shadow: 0 0 2rem rgba(0, 0, 0, 0.6);
}
.lightbox-svg {
  display: inline-block;
  min-width: 100%;
  max-width: 100%;
  max-height: 90vh;
  background: #ffffff;
  border-radius: 4px;
  padding: 1rem;
  overflow: auto;
}
.lightbox-svg svg {
  max-width: 100%;
  max-height: 90vh;
  height: auto;
  width: auto;
}
.lightbox-close {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 10000;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 2.4rem;
  height: 2.4rem;
  font-size: 1.1rem;
  cursor: pointer;
}
.lightbox-close:hover {
  background: rgba(255, 255, 255, 0.3);
}
"""


def on_config(config, **_kwargs):
    extra_js = list(config.get("extra_javascript") or [])
    if JS_NAME not in extra_js:
        extra_js.append(JS_NAME)
    config["extra_javascript"] = extra_js

    extra_css = list(config.get("extra_css") or [])
    if CSS_NAME not in extra_css:
        extra_css.append(CSS_NAME)
    config["extra_css"] = extra_css
    return config


def on_post_build(*, config, **kwargs):
    site = Path(config.site_dir)
    js_path = site / JS_NAME
    js_path.parent.mkdir(parents=True, exist_ok=True)
    js_path.write_text(_LIGHTBOX_JS, encoding="utf-8")
    css_path = site / CSS_NAME
    css_path.parent.mkdir(parents=True, exist_ok=True)
    css_path.write_text(_LIGHTBOX_CSS, encoding="utf-8")
    print(f"lightbox: wrote {JS_NAME} + {CSS_NAME}")
