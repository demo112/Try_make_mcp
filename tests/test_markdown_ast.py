import pytest
from src.apps.rag_flow_mcp.core.markdown_ast import MarkdownASTManager

class TestMarkdownASTManager:
    def setup_method(self):
        self.manager = MarkdownASTManager()

    def test_find_section_range_basic(self):
        content = """# Header 1
Content 1

# Header 2
Content 2
"""
        tokens = self.manager.parse(content)
        start, end = self.manager.find_section_range(tokens, "Header 1")
        # Header 1 (line 0) to start of Header 2 (line 3)
        assert start == 0
        assert end == 3

    def test_find_section_range_nested(self):
        content = """# Root
## Child 1
Content 1
## Child 2
Content 2
# Next Root
"""
        tokens = self.manager.parse(content)
        # Search for "Child 1"
        # Should start at "## Child 1" and end at "## Child 2"
        start, end = self.manager.find_section_range(tokens, "Child 1")
        # Line numbers (0-based):
        # 0: # Root
        # 1: ## Child 1
        # 2: Content 1
        # 3: ## Child 2
        assert start == 1
        assert end == 3

    def test_replace_section_basic(self):
        content = """# Section A
Old Content A

# Section B
Content B
"""
        new_content = "New Content A"
        # Expect header to be preserved
        # Note: The blank line between sections is part of Section A's range, so it gets replaced.
        expected = """# Section A
New Content A
# Section B
Content B
"""
        result = self.manager.replace_section(content, "Section A", new_content)
        assert result == expected

    def test_replace_section_not_found(self):
        content = "# Section A\nContent"
        result = self.manager.replace_section(content, "Section Z", "New")
        assert result == content

    def test_replace_section_last_section(self):
        content = """# Section A
Content A
"""
        new_content = "New Content A"
        expected = """# Section A
New Content A
"""
        result = self.manager.replace_section(content, "Section A", new_content)
        assert result == expected

    def test_replace_section_with_newlines(self):
        # Test handling of newlines in new_content
        content = """# Section A
Old
# Section B
"""
        # new_content without trailing newline
        new_content = "New"
        expected = """# Section A
New
# Section B
"""
        result = self.manager.replace_section(content, "Section A", new_content)
        assert result == expected

    def test_replace_section_preserves_header_level(self):
        content = """### Deep Header
Old Content
"""
        new_content = "New Content"
        expected = """### Deep Header
New Content
"""
        result = self.manager.replace_section(content, "Deep Header", new_content)
        assert result == expected
