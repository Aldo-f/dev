# mkdocs-pivot-table

A lightweight MkDocs plugin that renders interactive, sortable, and filterable comparison tables directly in your documentation.

## Features

- **Sortable columns** – Click any column header to sort ascending/descending
- **Drag-to-reorder** – Drag column headers to change order
- **State preservation** – View state is saved to the URL (shareable links) and localStorage
- **Hide/show columns** – Toggle individual columns via toolbar buttons
- **Hide/show rows** – Toggle individual rows via toolbar buttons
- **Swap rows/columns** – Transform the table orientation with one click
- **Reset button** – Restore the original view
- **Zero config** – Works out of the box with minimal setup

## Installation

Add to your `requirements.txt`:

```txt
-e git+https://github.com/Aldo-f/mkdocs-pivot-table.git#egg=mkdocs-pivot-table
```

Or install from PyPI (when published):

```bash
pip install mkdocs-pivot-table
```

Then enable the plugin in your `mkdocs.yml`:

```yaml
plugins:
  - mkdocs_pivot_table
```

## Usage

Place a table in your markdown using the `[pivot-table]` wrapper:

```markdown
[pivot-table]
| Feature | npm | pnpm | Bun | pip | uv |
|---------|-----|------|------|-----|----|
| Speed   | Slow | Fast | Fastest | Slow | Fast |
| Dedup   | No  | Yes  | Yes   | No  | Yes  |
| Runtime | No  | Yes  | Yes   | No  | Yes  |
| Maturity| High| High | Medium| High| Medium|
[/pivot-table]
```

The table will render as an interactive `<table>` with:

- **Sorting**: Click column headers to sort
- **Reordering**: Drag column headers to reorder
- **Filtering**: Use toolbar buttons to hide/show columns or rows
- **Swapping**: Click "Swap R/Col" to transpose the table
- **Sharing**: The current view is reflected in the URL

## Configuration

Optional configuration in `mkdocs.yml`:

```yaml
plugins:
  - mkdocs_pivot_table:
      asset_url: "https://cdn.jsdelivr.net/npm/pivot-table-kit@0.1.0/dist/pivot-table.js"
      asset_inline: false
```

| Option | Default | Description |
|--------|---------|-------------|
| `asset_url` | CDN URL | External JavaScript asset URL |
| `asset_inline` | `false` | Whether to inline the JS instead of loading from URL |

## Requirements

- MkDocs ≥ 1.5.0
- Python ≥ 3.9

## License

MIT
