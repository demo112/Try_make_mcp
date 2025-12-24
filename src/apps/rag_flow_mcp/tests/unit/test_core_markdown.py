import pytest
from src.apps.rag_flow_mcp.core.markdown_ast import MarkdownASTManager

class TestMarkdownAST:
    @pytest.fixture
    def manager(self):
        return MarkdownASTManager()

    @pytest.fixture
    def sample_md(self):
        return """# Title
Intro text.

## Section 1
Content 1.
### Subsection 1.1
Content 1.1.

## Section 2
Content 2.

# Conclusion
Final text.
"""

    def test_find_section_range_h2(self, manager, sample_md):
        """测试查找 H2 章节范围 (到下一个 H2 结束)"""
        tokens = manager.parse(sample_md)
        start, end = manager.find_section_range(tokens, "Section 1")
        
        # Section 1 starts at line 3 (0-indexed)
        # Ends before Section 2 (line 8)
        assert start == 3
        assert end == 8

    def test_find_section_range_h2_end_of_h1(self, manager, sample_md):
        """测试查找 H2 章节范围 (到下一个 H1 结束)"""
        tokens = manager.parse(sample_md)
        start, end = manager.find_section_range(tokens, "Section 2")
        
        # Section 2 starts at line 8
        # Ends before Conclusion (line 11)
        assert start == 8
        assert end == 11

    def test_find_section_range_nested(self, manager, sample_md):
        """测试查找包含子章节的范围"""
        # Section 1 应该包含 Subsection 1.1
        tokens = manager.parse(sample_md)
        start, end = manager.find_section_range(tokens, "Section 1")
        
        lines = sample_md.splitlines()
        section_content = "\n".join(lines[start:end])
        assert "Subsection 1.1" in section_content

    def test_find_section_range_not_found(self, manager, sample_md):
        """测试查找不存在的章节"""
        tokens = manager.parse(sample_md)
        result = manager.find_section_range(tokens, "NonExistent")
        assert result is None

    def test_replace_section(self, manager, sample_md):
        """测试替换章节内容"""
        new_content = "## Section 1\nNew Content.\n"
        result = manager.replace_section(sample_md, "Section 1", new_content)
        
        assert "Content 1" not in result
        assert "New Content" in result
        assert "## Section 2" in result # Ensure subsequent sections remain
        assert "# Conclusion" in result

    def test_replace_last_section(self, manager, sample_md):
        """测试替换最后一个章节"""
        new_content = "# Conclusion\nNew Conclusion.\n"
        result = manager.replace_section(sample_md, "Conclusion", new_content)
        
        assert "Final text" not in result
        assert "New Conclusion" in result

    def test_replace_section_not_found(self, manager, sample_md):
        """测试替换不存在的章节 (应保持原样)"""
        result = manager.replace_section(sample_md, "Ghost", "Boo")
        assert result == sample_md
