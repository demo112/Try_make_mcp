import pytest
import os
import time
from src.apps.rag_flow_mcp.core.shadow_file_manager import ShadowFileManager

class TestShadowFileManager:
    def setup_method(self):
        self.manager = ShadowFileManager()

    def test_generate_shadow_copy_success(self, tmp_path):
        # 1. Prepare original file
        d = tmp_path / "docs"
        d.mkdir()
        p = d / "test_doc.md"
        original_content = "# Title\nOriginal Content"
        p.write_text(original_content, encoding="utf-8")
        
        # 2. Prepare new content
        new_content = "# Title\nNew Content"
        
        # 3. Call generate_shadow_copy
        shadow_path, diff_path = self.manager.generate_shadow_copy(str(p), new_content)
        
        # 4. Verify shadow file exists and content matches
        assert os.path.exists(shadow_path)
        assert "_ai_revision_" in shadow_path
        with open(shadow_path, 'r', encoding='utf-8') as f:
            assert f.read() == new_content
            
        # 5. Verify original file is UNTOUCHED
        with open(p, 'r', encoding='utf-8') as f:
            assert f.read() == original_content

        # 6. Verify diff report exists
        assert os.path.exists(diff_path)
        assert "_diff_" in diff_path
        with open(diff_path, 'r', encoding='utf-8') as f:
            diff_content = f.read()
            assert "Diff Report" in diff_content
            assert "-Original Content" in diff_content
            assert "+New Content" in diff_content

    def test_generate_shadow_copy_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            self.manager.generate_shadow_copy("non_existent_file.md", "content")

    def test_generate_diff_report_format(self):
        old = "Line 1\nLine 2"
        new = "Line 1\nLine 2 Modified"
        report = self.manager._generate_diff_report(old, new, "old.md", "new.md")
        
        assert "# Diff Report: old.md" in report
        assert "**Source**: `old.md`" in report
        assert "**Revision**: `new.md`" in report
        assert "```diff" in report
        assert "-Line 2" in report
        assert "+Line 2 Modified" in report
