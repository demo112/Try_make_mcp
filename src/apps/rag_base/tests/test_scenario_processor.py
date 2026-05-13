
import pytest
from unittest.mock import MagicMock, patch
from src.apps.rag_base.core.scenario_processor import ScenarioProcessor

class TestScenarioProcessor:
    def setup_method(self):
        self.mock_rag_client = MagicMock()
        self.processor = ScenarioProcessor(self.mock_rag_client)

    @patch("src.apps.rag_base.core.shadow_file_manager.ShadowFileManager.create_shadow_copy")
    @patch("src.apps.rag_base.core.shadow_file_manager.ShadowFileManager.read_file")
    @patch("src.apps.rag_base.core.shadow_file_manager.ShadowFileManager.write_file")
    def test_process_suggestions(self, mock_write, mock_read, mock_create):
        # Setup
        mock_create.return_value = "shadow_path.md"
        mock_read.return_value = """# Title
## What is 6A?
Some content.
"""
        # Mock RAG response
        self.mock_rag_client.retrieve_and_answer.return_value = {
            "answer": "6A is a workflow.",
            "confidence": 0.9,
            "references": []
        }

        # Execute
        result = self.processor.process_clarification_suggestions("doc.md", "kb_id")

        # Verify
        assert result["status"] == "success"
        
        # Verify write content
        args, _ = mock_write.call_args
        written_content = args[1]
        
        assert "> 💡 **AI Suggestion**" in written_content
        assert "6A is a workflow." in written_content
        assert "(Confidence: 0.90)" in written_content

    @patch("src.apps.rag_base.core.shadow_file_manager.ShadowFileManager.create_shadow_copy")
    @patch("src.apps.rag_base.core.shadow_file_manager.ShadowFileManager.read_file")
    @patch("src.apps.rag_base.core.shadow_file_manager.ShadowFileManager.write_file")
    def test_process_low_confidence_skipped(self, mock_write, mock_read, mock_create):
        mock_create.return_value = "shadow.md"
        mock_read.return_value = "## Low Conf Question?"
        
        self.mock_rag_client.retrieve_and_answer.return_value = {
            "answer": "Dunno.",
            "confidence": 0.1,
            "references": []
        }

        self.processor.process_clarification_suggestions("doc.md", "")
        
        args, _ = mock_write.call_args
        written_content = args[1]
        # Should NOT contain suggestion
        assert "AI Suggestion" not in written_content

    @patch("src.apps.rag_base.core.shadow_file_manager.ShadowFileManager.create_shadow_copy")
    @patch("src.apps.rag_base.core.shadow_file_manager.ShadowFileManager.read_file")
    @patch("src.apps.rag_base.core.shadow_file_manager.ShadowFileManager.write_file")
    def test_process_with_references_and_codeblocks(self, mock_write, mock_read, mock_create):
        mock_create.return_value = "shadow_path.md"
        mock_read.return_value = """# Title
## What is 6A?
```python
# Is this a question?
print("hello")
```
## Another Question?
"""
        # Mock RAG response side_effect for different inputs
        def side_effect(query):
            if "What is 6A?" in query:
                return {
                    "answer": "6A is cool.",
                    "confidence": 0.9,
                    "references": [{"doc_name": "doc1.pdf"}, {"doc_name": "doc2.txt"}]
                }
            elif "Another Question?" in query:
                return {
                    "answer": "Yes.",
                    "confidence": 0.8,
                    "references": []
                }
            return {"answer": "Unknown", "confidence": 0.0, "references": []}

        self.mock_rag_client.retrieve_and_answer.side_effect = side_effect

        # Execute
        result = self.processor.process_clarification_suggestions("doc.md", "kb_id")

        # Verify
        assert result["status"] == "success"
        
        args, _ = mock_write.call_args
        written_content = args[1]
        
        # Check Reference
        assert "*Sources: doc1.pdf, doc2.txt*" in written_content
        
        # Check Question 1 Answered
        assert "6A is cool." in written_content
        
        # Check Question 2 Answered
        assert "Yes." in written_content
        
        # Check Code Block Ignored (should not have called RAG for it)
        calls = self.mock_rag_client.retrieve_and_answer.call_args_list
        queries = [c[0][0] for c in calls]
        
        assert "What is 6A?" in queries
        assert "Another Question?" in queries
        
        # Strict check: "Is this a question?" should NOT be in queries
        # But regex matches lines starting with #. Inside code block it is "# Is this..."
        # So our logic MUST ignore it.
        assert "# Is this a question?" not in queries
        assert "Is this a question?" not in queries
