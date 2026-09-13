
# mkdocs-raw-markdown

A tiny MkDocs plugin that makes the original Markdown source available at a URL ending with ``.md``.

## Installation
```bash
pip install mkdocs-raw-markdown
```

## Usage
Add to your ``mkdocs.yml``:
```yaml
plugins:
  - search
  - mkdocs-raw-markdown:
      suffix: .md   # optional, default ".md"
```

Now ``https://example.com/path/to/page.md`` returns the raw Markdown with ``Content-Type: text/markdown``.
