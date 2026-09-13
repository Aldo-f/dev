"""
mkdocs-pivot-table — Interactive sortable/filterable comparison tables for MkDocs.

Usage:
    [pivot-table]
    | col1 | col2 | col3 |
    |------|------|------|
    | a    | b    | c    |
    | d    | e    | f    |
    [/pivot-table]
"""

__version__ = "0.3.0"

import os
import re
from pathlib import Path
from mkdocs.plugins import BasePlugin
from mkdocs.config.config_options import Type as PluginType


PIVOT_PATTERN = re.compile(r"\[pivot-table\]\s*\n(.*?)\n\s*\[/pivot-table\]", re.DOTALL)

PLUGIN_DIR = Path(__file__).parent
ASSETS_DIR = PLUGIN_DIR / "assets"


def _parse_pivot_table(md_text):
    """Parse markdown pipe-table into (headers, rows)."""
    lines = [l.strip() for l in md_text.strip().split("\n") if l.strip()]
    if len(lines) < 2:
        return [], []
    headers = [c.strip() for c in lines[0].split("|") if c.strip()]
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if cells:
            rows.append(cells)
    return headers, rows


def _generate_table_id(idx, page_key="global"):
    """Generate a unique table ID based on page and index."""
    safe_page = page_key.replace("/", "-").replace(".", "-")
    return f"pivot-{safe_page}-{idx:03d}"


def _escape_attr(s):
    """Escape HTML attributes safely."""
    return (
        s.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _load_asset(filename):
    """Load an asset file from the assets directory."""
    asset_path = ASSETS_DIR / filename
    if asset_path.exists():
        return asset_path.read_text(encoding="utf-8")
    return ""


def _build_table_html(headers, rows, table_id):
    """Generate the static HTML skeleton for an interactive table."""
    h = [f'<div class="pivot-table-wrap" data-pivot="{table_id}">']
    # Toolbar is injected by JavaScript on init
    h.append(f'<div class="pivot-toolbar" data-for="{table_id}"></div>')

    # Build table
    h.append(
        f'<table id="{table_id}" class="pivot-table" '
        'border="1" cellpadding="5" cellspacing="0" '
        'style="border-collapse:collapse;font-size:0.85rem;width:100%">')
    h.append("<thead><tr>")
    for i, col in enumerate(headers):
        h.append(f'<th draggable="true" data-col="{i}">{_escape_attr(col)}</th>')
    h.append("</tr></thead><tbody>")

    for ri, row in enumerate(rows):
        h.append("<tr>")
        for ci, cell in enumerate(row):
            h.append(f'<td data-col="{ci}">{_escape_attr(cell)}</td>')
        h.append("</tr>")

    h.append("</tbody></table></div>")
    return "\n".join(h)


class PivotTablePlugin(BasePlugin):
    """MkDocs plugin for interactive comparison tables.

    Configure in mkdocs.yml:
        plugins:
          - mkdocs_pivot_table
    """

    config_scheme = (
        (
            "asset_url",
            PluginType(
                str,
                default="https://cdn.jsdelivr.net/npm/pivot-table-kit@0.1.0/dist/pivot-table.js",
            ),
        ),
        ("asset_inline", PluginType(bool, default=False)),
    )

    def on_config(self, config):
        self._has_table = False
        return config

    def _process_markdown(self, source, page):
        """Replace [pivot-table] blocks in raw markdown with HTML."""
        matches = list(PIVOT_PATTERN.finditer(source))
        if not matches:
            return source, []

        out_parts = []
        last = 0
        for idx, m in enumerate(matches, start=1):
            out_parts.append(source[last : m.start()])
            md_text = m.group(1)
            headers, rows = _parse_pivot_table(md_text)
            page_key = (
                page.file.src_path if page and hasattr(page, "file") else "global"
            )
            table_id = _generate_table_id(idx, page_key)
            if headers and rows:
                out_parts.append(_build_table_html(headers, rows, table_id))
                self._has_table = True
            else:
                out_parts.append(m.group(0))
            last = m.end()
        out_parts.append(source[last:])
        return "".join(out_parts), []

    def on_page_markdown(self, markdown, page, config, files):
        """Process raw markdown to substitute pivot blocks before HTML conversion."""
        return self._process_markdown(markdown, page)[0]

    def on_post_page(self, output_content, config, page, **kwargs):
        return output_content

    def on_post_build(self, config):
        """Inject the pivot JS/CSS into every HTML page that has a pivot table."""
        if not self._has_table:
            return

        site_dir = config["site_dir"]
        css_content = _load_asset("pivot.css")
        js_content = _load_asset("pivot.js")

        for root, _dirs, files in os.walk(site_dir):
            for fname in files:
                if not fname.endswith(".html"):
                    continue
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8") as fh:
                    html = fh.read()
                if 'class="pivot-table"' not in html:
                    continue
                if "pivot-table-style" not in html and css_content:
                    html = html.replace(
                        "</head>",
                        f'<style class="pivot-table-style">\n{css_content}\n</style>\n</head>',
                        1,
                    )
                if "pivot-table-script" not in html and js_content:
                    scripts = [
                        f'<script class="pivot-table-script">\n{js_content}\n</script>'
                    ]
                    if self.config["asset_url"] and not self.config["asset_inline"]:
                        scripts.append(
                            f'<script class="pivot-table-script" '
                            f'src="{self.config["asset_url"]}"></script>'
                        )
                    html = html.replace("</body>", "\n".join(scripts) + "\n</body>", 1)
                with open(fpath, "w", encoding="utf-8") as fh:
                    fh.write(html)


# Expose plugin class and helpers for tests and import
__all__ = [
    "PivotTablePlugin",
    "PIVOT_PATTERN",
    "_parse_pivot_table",
    "_build_table_html",
    "_generate_table_id",
    "__version__",
]
