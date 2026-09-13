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

from .plugin import (
    PivotTablePlugin,
    PIVOT_PATTERN,
    _parse_pivot_table,
    _build_table_html,
    _generate_table_id,
)

__all__ = [
    "PivotTablePlugin",
    "PIVOT_PATTERN",
    "_parse_pivot_table",
    "_build_table_html",
    "_generate_table_id",
    "__version__",
]
