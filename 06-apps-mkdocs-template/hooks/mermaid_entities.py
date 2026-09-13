"""MkDocs hook: decode HTML entities in mermaid code blocks."""

from __future__ import annotations

import re
import html as html_module

# Minimal init script - mermaid is already loaded via extra_javascript in mkdocs.base.yml
MERMAID_INIT_JS = """
<script>
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose'
});
</script>
"""


def on_page_content(html, page, config, files):
    """Decode HTML entities in mermaid code blocks."""
    if "mermaid" not in html.lower():
        return html

    # Decode HTML entities in mermaid code blocks
    def decode_entities(match):
        code = match.group(1)
        decoded = html_module.unescape(code)
        # Convert self-closing br to non-self-closing for mermaid compatibility
        decoded = decoded.replace("<br/>", "<br>")
        return f'<pre class="mermaid">{decoded}</pre>'

    # Handle multiple formats
    html = re.sub(
        r'<pre class="mermaid"><code>(.*?)</code></pre>',
        decode_entities,
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        decode_entities,
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'<pre class="mermaid">\s*(.*?)\s*</pre>',
        lambda m: f'<pre class="mermaid">{html_module.unescape(m.group(1))}</pre>',
        html,
        flags=re.DOTALL,
    )

    return html


def on_post_page(output, page, config, files=None):
    """Add mermaid init script after template rendering."""
    if "mermaid" not in output.lower():
        return output

    # Decode any remaining HTML entities in mermaid blocks
    def decode_entities(match):
        code = match.group(1)
        decoded = html_module.unescape(code)
        decoded = decoded.replace("<br/>", "<br>")
        return f'<pre class="mermaid">{decoded}</pre>'

    output = re.sub(
        r'<pre class="mermaid">(.*?)</pre>', decode_entities, output, flags=re.DOTALL
    )

    # Add mermaid init script if not present
    if "mermaid.initialize" not in output:
        output = output.replace("</body>", f"{MERMAID_INIT_JS}\n  </body>")

    return output


def on_post_build(config):
    """Log completion."""
    print("mermaid hook: complete")
