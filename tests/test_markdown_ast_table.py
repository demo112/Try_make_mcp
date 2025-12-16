import pytest
from src.apps.rag_flow_mcp.core.markdown_ast import MarkdownASTManager

class TestMarkdownASTTable:
    def setup_method(self):
        self.manager = MarkdownASTManager()

    def test_update_table_cell_basic(self):
        content = """# Section A

| Header 1 | Header 2 |
| --- | --- |
| Row1Col1 | Row1Col2 |
| Row2Col1 | Row2Col2 |

# Section B
"""
        # Update Row 1 (0-based), Col 2 (1-based) -> "NewValue"
        # Row 1 is "Row2Col1", "Row2Col2"
        # So we update Row2Col2 to NewValue
        
        new_content = self.manager.update_table_cell(content, "Section A", 1, 1, "NewValue")
        
        # Check if NewValue is present
        assert "NewValue" in new_content
        # Check if structure is maintained (roughly)
        assert "| Header 1" in new_content
        # Check that Row2Col1 is still there (it was in the same row)
        assert "Row2Col1" in new_content
        assert "# Section B" in new_content

    def test_update_table_cell_out_of_bounds(self):
        content = """# Section A
| A | B |
|---|---|
| 1 | 2 |
"""
        # Row 5 doesn't exist
        new_content = self.manager.update_table_cell(content, "Section A", 5, 0, "X")
        assert new_content == content

    def test_update_table_cell_no_table(self):
        content = """# Section A
No table here.
"""
        new_content = self.manager.update_table_cell(content, "Section A", 0, 0, "X")
        assert new_content == content
