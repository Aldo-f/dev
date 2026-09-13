"""mkdocs_pivot_table stub package for testing.

Provides minimal implementations of the functions and classes required by the test suite.
"""

__version__ = "0.0.0-stub"

from .plugin import PivotTablePlugin, _parse_pivot_table, _build_table_html, _generate_table_id

__all__ = [
    "PivotTablePlugin",
    "_parse_pivot_table",
    "_build_table_html",
    "_generate_table_id",
    "__version__",
]
