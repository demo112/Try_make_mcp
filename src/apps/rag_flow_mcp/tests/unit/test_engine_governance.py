import pytest
import os
from unittest.mock import MagicMock
from src.apps.rag_flow_mcp.engines.governance import GovernanceEngine

class TestGovernanceEngine:
    @pytest.fixture
    def engine(self):
        engine = GovernanceEngine(config={})
        engine.logger = MagicMock()
        return engine

    def test_check_metadata_compliance_pass(self, engine, tmp_path):
        """测试元数据合规性检查通过"""
        doc = tmp_path / "valid.md"
        doc.write_text("""---
product: TestProd
module: TestMod
version: 1.0
---
# Content
""", encoding="utf-8")
        
        result = engine.check_metadata_compliance(str(doc))
        assert result["status"] == "passed"
        assert result["metadata"]["product"] == "TestProd"

    def test_check_metadata_compliance_missing_fields(self, engine, tmp_path):
        """测试缺失字段"""
        doc = tmp_path / "invalid.md"
        doc.write_text("""---
product: TestProd
---
# Content
""", encoding="utf-8")
        
        result = engine.check_metadata_compliance(str(doc))
        assert result["status"] == "failed"
        assert "module" in result["reason"]
        assert "version" in result["reason"]

    def test_check_metadata_compliance_no_yaml(self, engine, tmp_path):
        """测试没有 YAML 头"""
        doc = tmp_path / "no_yaml.md"
        doc.write_text("# Just Content", encoding="utf-8")
        
        result = engine.check_metadata_compliance(str(doc))
        assert result["status"] == "failed"
        # Logic might differ slightly depending on implementation details, 
        # but expected result is failed due to missing all fields.
        assert "product" in result["reason"]

    def test_check_metadata_compliance_file_not_found(self, engine):
        """测试文件不存在"""
        result = engine.check_metadata_compliance("non_existent.md")
        assert result["status"] == "error"

    def test_validate_knowledge_conflict_pass(self, engine):
        """测试冲突检测 (模拟)"""
        data = {"question": "Q", "answer": "A", "metadata": {}}
        result = engine.validate_knowledge_conflict(data)
        assert result["status"] == "passed"
