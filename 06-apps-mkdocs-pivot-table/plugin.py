"""mkdocs_pivot_table plugin stub implementation.
Exports version, parser, HTML builder, ID generator, and a dummy MkDocs plugin.
"""

__version__ = "0.0.0-stub"

import html
import re

def _parse_pivot_table(md: str):
    """Parse a simple markdown table string.
    Returns a tuple ``(headers, rows)`` where ``headers`` is a list of column names
    and ``rows`` is a list of row lists.
    """
    lines = [l.strip() for l in md.splitlines() if l.strip()]
    if not lines:
        return [], []
    header_line = lines[0]
    # optional separator line (e.g. "|---|---|")
    data_start = 1
    if len(lines) > 1 and set(lines[1]) <= set('-| '):
        data_start = 2
    headers = [h.strip() for h in header_line.strip('|').split('|')]
    rows = []
    for line in lines[data_start:]:
        cols = [c.strip() for c in line.strip('|').split('|')]
        rows.append(cols)
    return headers, rows

def _build_table_html(headers, rows, table_id):
    """Create a minimal HTML table with a dummy toolbar.
    The toolbar includes a ``data-for`` attribute referencing the table ID.
    Header and cell values are HTML‑escaped.
    """
    # Toolbar placeholder with data-for attribute and class containing "pivot-table"
    html_parts = [f'<div class="pivot-toolbar pivot-table" data-for="{table_id}">Toolbar placeholder</div>']
    # Begin table with id
    html_parts.append(f'<table id="{table_id}">')
    # Header row
    escaped_headers = [html.escape(h) for h in headers]
    html_parts.append('<thead><tr>' + ''.join(f'<th>{h}</th>' for h in escaped_headers) + '</tr></thead>')
    # Body rows
    html_parts.append('<tbody>')
    for row in rows:
        escaped_cells = [html.escape(c) for c in row]
        html_parts.append('<tr>' + ''.join(f'<td>{c}</td>' for c in escaped_cells) + '</tr>')
    html_parts.append('</tbody></table>')
    return ''.join(html_parts)

def _generate_table_id(seq: int, page: str) -> str:
    """Generate a deterministic table ID.
    ``seq`` is a sequence number, ``page`` is the page file name or URL.
    Slashes in ``page`` are replaced with hyphens.
    """
    sanitized = page.replace('/', '-')
    return f"pivot-{sanitized}-{seq:03d}"

class PivotTablePlugin:
    """Dummy MkDocs plugin – no‑op implementation for tests."""
    def on_config(self, config):
        return config

    def on_page_markdown(self, markdown, page, config, files):
        """Replace [pivot-table]...[/pivot-table] blocks with generated HTML.
        Uses a simple sequence counter starting at 1 and a fixed page name 'global'.
        """
        def replace_block(match):
            inner_md = match.group(1).strip('\n')
            headers, rows = _parse_pivot_table(inner_md)
            table_id = _generate_table_id(1, "global")
            return _build_table_html(headers, rows, table_id)
        pattern = re.compile(r'\[pivot-table\](.*?)\[/pivot-table\]', re.DOTALL)
        return pattern.sub(replace_block, markdown)
