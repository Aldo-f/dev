# PROJECT KNOWLEDGE BASE – plugins

**Generated:** {{timestamp}}
**Commit:** {{short_sha}}
**Branch:** {{branch}}

## OVERVIEW
Custom MkDocs plugins extending the documentation pipeline (e.g., raw‑markdown parser, slugmap generator).

## STRUCTURE
```
06-apps-aldo-f-github-io/
└── plugins/
    ├── mkdocs_raw_markdown/
    │   ├── __init__.py    # Plugin entry point
    │   └── raw_parser.py  # Parses raw markdown blocks
    └── other_plugin/       # Placeholder for future plugins
```

## WHERE TO LOOK
| File/Dir | Purpose |
|----------|--------|
| `mkdocs_raw_markdown/__init__.py` | Registers the plugin with MkDocs |
| `mkdocs_raw_markdown/raw_parser.py` | Implements the raw‑markdown parsing logic |
| `other_plugin/` | Space for additional plugins |

## CONVENTIONS
- Plugins expose a `on_page_markdown` hook to inject custom processing.
- Configuration lives in `mkdocs.base.yml` under the `plugins` key.

## ANTI‑PATTERNS (THIS PROJECT)
- Do not import heavy third‑party libraries inside plugins unless required – keep them lightweight.

## COMMANDS
```bash
# Run MkDocs with plugins (handled automatically by mkdocs build)
mkdocs serve -f mkdocs.en.yml
```
