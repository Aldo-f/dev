"""Tests for mkdocs-pivot-table plugin."""

import pytest
from mkdocs_pivot_table import (
    __version__,
    _parse_pivot_table,
    _build_table_html,
    _generate_table_id,
)


class TestVersion:
    def test_version_exists(self):
        assert isinstance(__version__, str)
        assert len(__version__) > 0


class TestParsePivotTable:
    def test_parse_basic_table(self):
        md = """| A | B |
|---|---|
| 1 | 2 |"""
        headers, rows = _parse_pivot_table(md)
        assert headers == ["A", "B"]
        assert rows == [["1", "2"]]

    def test_parse_single_row(self):
        md = """| Name | Value |
|------|-------|
| foo  | bar   |"""
        headers, rows = _parse_pivot_table(md)
        assert headers == ["Name", "Value"]
        assert rows == [["foo", "bar"]]

    def test_parse_no_data(self):
        # Parser requires at least header + separator lines
        md = """| A | B |
|---|---|"""
        headers, rows = _parse_pivot_table(md)
        assert headers == ["A", "B"]
        assert rows == []

    def test_parse_empty(self):
        headers, rows = _parse_pivot_table("")
        assert headers == []
        assert rows == []

    def test_parse_with_whitespace(self):
        md = """\n  | X | Y |\n  |---|---|\n  | a | b |\n"""
        headers, rows = _parse_pivot_table(md)
        assert headers == ["X", "Y"]
        assert rows == [["a", "b"]]


class TestBuildTableHtml:
    def test_basic_table(self):
        html = _build_table_html(["A", "B"], [["1", "2"]], "test-001")
        assert 'id="test-001"' in html
        assert ">A<" in html  # Check for A in th tag
        assert ">B<" in html
        assert ">1<" in html
        assert ">2<" in html

    def test_escapes_html(self):
        html = _build_table_html(["A<B", "C>D"], [["&e"]], "test-002")
        assert "&lt;B" in html
        assert "C&gt;" in html

    def test_multiple_rows(self):
        html = _build_table_html(["X", "Y"], [["1", "2"], ["3", "4"]], "test-003")
        # Each value appears once in the table body
        assert html.count(">1<") == 1
        assert html.count(">2<") == 1
        assert html.count(">3<") == 1
        assert html.count(">4<") == 1

    def test_includes_toolbar(self):
        html = _build_table_html(["Name", "Value"], [["a", "1"]], "test-004")
        assert "pivot-toolbar" in html
        # Toolbar div is present (buttons are rendered by JS)
        assert 'data-for="test-004"' in html


class TestGenerateTableId:
    def test_basic_id(self):
        assert _generate_table_id(1, "test-page") == "pivot-test-page-001"

    def test_nested_page(self):
        assert _generate_table_id(1, "blog/posts/2026/09/test") == "pivot-blog-posts-2026-09-test-001"

    def test_global_default(self):
        assert _generate_table_id(1, "global") == "pivot-global-001"
        assert _generate_table_id(5, "global") == "pivot-global-005"


class TestPluginIntegration:
    def test_plugin_class_exists(self):
        from mkdocs_pivot_table.plugin import PivotTablePlugin
        assert PivotTablePlugin is not None

    def test_on_config_returns_config(self):
        from mkdocs_pivot_table.plugin import PivotTablePlugin
        plugin = PivotTablePlugin()
        # Should not raise
        result = plugin.on_config(None)
        assert result is None

    def test_on_page_markdown_passes_through(self):
        from mkdocs_pivot_table.plugin import PivotTablePlugin
        plugin = PivotTablePlugin()
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = plugin.on_page_markdown(md, None, None, None)
        assert result == md  # No block to process

    def test_process_markdown_with_pivot_block(self):
        from mkdocs_pivot_table.plugin import PivotTablePlugin
        plugin = PivotTablePlugin()
        md = """[pivot-table]
| Tool | Eco |
|------|-----|
| npm  | JS  |
[/pivot-table]"""
        result = plugin.on_page_markdown(md, None, None, None)
        # Should contain table HTML, not original markdown
        assert "<table" in result
        assert "pivot-table" in result
        assert "[pivot-table]" not in result  # Block marker replaced


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
