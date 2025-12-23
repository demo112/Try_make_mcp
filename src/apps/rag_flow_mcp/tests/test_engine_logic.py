import pytest
import os
from unittest.mock import MagicMock, patch
from src.apps.rag_flow_mcp.engines.inference import InferenceEngine
from src.apps.rag_flow_mcp.engines.evolution import EvolutionEngine

class TestInferenceEngine:
    @pytest.fixture
    def engine(self):
        # Mock init to avoid real connections during instantiation if any
        with patch('src.apps.rag_flow_mcp.engines.inference.RAGClient'), \
             patch('src.apps.rag_flow_mcp.core.evaluator.QualityEvaluator'), \
             patch('src.apps.rag_flow_mcp.engines.inference.ShadowFileManager'):
            engine = InferenceEngine(config={})
            # Manually mock components
            engine.rag_client = MagicMock()
            engine.evaluator = MagicMock()
            engine.shadow_manager = MagicMock()
            engine.logger = MagicMock()
            return engine

    def test_fill_suggestions_no_file(self, engine):
        result = engine.fill_clarification_suggestions("non_existent.md")
        assert result["status"] == "error"
        assert "文件未找到" in result["message"]

    def test_fill_suggestions_no_questions(self, engine, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text("# Title\nNo questions here.", encoding="utf-8")
        
        result = engine.fill_clarification_suggestions(str(doc))
        assert result["status"] == "success"
        assert result["processed_count"] == 0

    def test_fill_suggestions_success(self, engine, tmp_path):
        doc = tmp_path / "questions.md"
        content = """---
product: P
module: M
---
# 待确认问题

## 1. Q1
**背景**: Context
**问题描述**: What is X?
**回答**: 
"""
        doc.write_text(content, encoding="utf-8")
        
        # Mock RAG response - InferenceEngine uses agentic_search
        engine.rag_client.agentic_search.return_value = {"answer": "It is X.", "score": 0.9}
        # Mock Evaluator
        engine.evaluator.evaluate.return_value = {"is_valid": True, "reason": "Pass"}
        
        # Mock Shadow Manager
        engine.shadow_manager.generate_shadow_copy.return_value = ("shadow.md", "diff.html")

        # We need to mock _read_file and _write_file if they are methods of BaseEngine, 
        # or rely on them reading/writing the real tmp file if they use standard open().
        # BaseEngine usually uses standard open().
        
        result = engine.fill_clarification_suggestions(str(doc))
        
        if result["status"] == "error":
             print(f"Error Message: {result.get('message')}")

        assert result["status"] == "success"
        assert result["processed_count"] == 1
        
        # Verify file content updated
        new_content = doc.read_text(encoding="utf-8")
        # Since we use ShadowFileManager, original file might NOT be updated directly 
        # depending on implementation. 
        # InferenceEngine.py: 
        # shadow_path, diff_path = self.shadow_manager.generate_shadow_copy(doc_path, new_content)
        # It returns shadow_path. It DOES NOT overwrite original doc?
        # Let's check InferenceEngine.py again.
        # Line 120: shadow_path, ... = ...
        # It does NOT write back to doc_path.
        # So we should check if result contains shadow_path
        
        assert "shadow_path" in result

class TestEvolutionEngine:
    @pytest.fixture
    def engine(self):
        with patch('src.apps.rag_flow_mcp.engines.evolution.MarkdownASTManager'), \
             patch('src.apps.rag_flow_mcp.engines.evolution.ShadowFileManager'), \
             patch('src.apps.rag_flow_mcp.engines.evolution.RAGClient'):
            engine = EvolutionEngine(config={})
            engine.ast_manager = MagicMock()
            engine.shadow_manager = MagicMock()
            engine.rag_client = MagicMock()
            engine.logger = MagicMock()
            return engine

    def test_evolve_scheme_doc_not_found(self, engine):
        result = engine.evolve_scheme_document("no_scheme.md", "clarification.md")
        assert result["status"] == "error"
        assert "文件未找到" in result["message"]

    def test_evolve_clarification_doc_not_found(self, engine, tmp_path):
        scheme = tmp_path / "scheme.md"
        scheme.touch()
        result = engine.evolve_scheme_document(str(scheme), "no_clarification.md")
        assert result["status"] == "error"
        assert "文件未找到" in result["message"]

    def test_evolve_success(self, engine, tmp_path):
        scheme_doc = tmp_path / "scheme.md"
        scheme_doc.write_text("""# Scheme
## Section 1
Old Content
""", encoding="utf-8")
        
        clarif_doc = tmp_path / "clarif.md"
        clarif_doc.write_text("""
## 1. Q1
**问题描述**: Change scheme?
**回答**: Yes, update Section 1.
""", encoding="utf-8")

        # Use Real AST Manager for logic test
        from src.apps.rag_flow_mcp.core.markdown_ast import MarkdownASTManager
        engine.ast_manager = MarkdownASTManager()
        
        # Mock RAG response
        engine.rag_client.agentic_search.return_value = {
            "answer": """
```json
{
  "target_header": "Section 1",
  "new_content": "New Content"
}
```
"""
        }
        
        # Mock Shadow Manager
        engine.shadow_manager.generate_shadow_copy.return_value = ("shadow.md", "diff.html")

        result = engine.evolve_scheme_document(str(scheme_doc), str(clarif_doc))
        
        if result["status"] == "error":
             print(f"Error Message: {result.get('message')}")
        
        assert result["status"] == "success"
        
        # Verify scheme updated
        # Note: Evolution Engine writes to Shadow Copy, not original file directly?
        # Line 121: generate_shadow_copy(scheme_doc_path, current_content)
        # So scheme_doc on disk is NOT updated. We must verify the content passed to shadow_manager.
        
        args, _ = engine.shadow_manager.generate_shadow_copy.call_args
        content_passed = args[1]
        assert "New Content" in content_passed
        assert "Old Content" not in content_passed
