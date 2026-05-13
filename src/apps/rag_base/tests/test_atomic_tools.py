import os
import json
import shutil
import unittest
from unittest.mock import MagicMock
from src.apps.rag_base.server import create_shadow_file, extract_questions_from_doc, retrieve_rag_suggestion, apply_suggestions_to_doc, fill_clarification_suggestions, scenario_processor

class TestDecoupledToolsUnit(unittest.TestCase):
    def setUp(self):
        self.test_dir = "temp_test_atomic_tools"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        self.doc_path = os.path.join(self.test_dir, "test_doc.md")
        with open(self.doc_path, "w", encoding="utf-8") as f:
            f.write("# Question: What is RAG?\n\nContent here.")

        self.original_rag = scenario_processor.rag_client
        self.mock_rag = MagicMock()
        scenario_processor.rag_client = self.mock_rag

    def tearDown(self):
        scenario_processor.rag_client = self.original_rag
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_field_extraction(self):
        """Test the new field-based extraction logic."""
        doc_path = os.path.join(self.test_dir, "test_field.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("## Feature A\n- 描述: How to handle auth failure?\n\n## Normal Header\nJust text.")
        
        shadow_path = create_shadow_file(doc_path)
        res_json = extract_questions_from_doc(shadow_path)
        questions = json.loads(res_json)
        
        self.assertEqual(len(questions), 1)
        # Check if context is merged
        self.assertIn("Feature A", questions[0]['text'])
        self.assertIn("How to handle auth failure", questions[0]['text'])
        
        # Verify line index points to the Header
        self.assertEqual(questions[0]['line_index'], 0)

    def test_retrieve_rag_suggestion_with_llm(self):
        """Test the new MCP-side LLM orchestration flow."""
        # Mock LLM calls
        self.mock_rag.call_llm.side_effect = [
            "refined query",   # Preprocessing
            "Final Answer from LLM" # Synthesis
        ]
        # Mock Chunk Retrieval
        self.mock_rag.retrieve_chunks.return_value = {
            "status": "success",
            "data": [{"content": "Chunk 1", "similarity": 0.9}]
        }
        
        # Call with dataset_id
        res_json = retrieve_rag_suggestion("Raw Query", "test_dataset_id")
        result = json.loads(res_json)
        
        # Verify
        self.assertIn("Final Answer from LLM", result['suggestion'])
        self.assertFalse(result['skipped'])
        
        # Check calls
        self.assertEqual(self.mock_rag.call_llm.call_count, 2)
        self.mock_rag.retrieve_chunks.assert_called_with("test_dataset_id", "refined query")

    def test_tools(self):
        # 1. Create Shadow
        shadow_path = create_shadow_file(self.doc_path)
        self.assertTrue(os.path.exists(shadow_path))
        self.assertIn("_ai_revision", shadow_path)

        # 2. Extract
        res_json = extract_questions_from_doc(shadow_path)
        questions = json.loads(res_json)
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]['text'], "Question: What is RAG?")

        # 3. Retrieve
        self.mock_rag.retrieve_and_answer.return_value = {
            "answer": "RAG is cool.",
            "confidence": 0.9,
            "references": []
        }
        res_json = retrieve_rag_suggestion("What is RAG?")
        sugg = json.loads(res_json)
        self.assertIn("RAG is cool", sugg['suggestion'])

        # 4. Apply
        s_map = {str(questions[0]['line_index']): sugg['suggestion']}
        res_json = apply_suggestions_to_doc(shadow_path, json.dumps(s_map))
        res = json.loads(res_json)
        self.assertEqual(res['status'], 'success')
        
        with open(shadow_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("RAG is cool", content)

    def test_controller(self):
        self.mock_rag.retrieve_and_answer.return_value = {
            "answer": "Auto answer.",
            "confidence": 0.8
        }
        res_json = fill_clarification_suggestions(self.doc_path)
        res = json.loads(res_json)
        self.assertEqual(res['status'], 'success')

if __name__ == "__main__":
    unittest.main()
