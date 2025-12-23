
import pytest
from unittest.mock import MagicMock, patch
from src.apps.rag_base.core.rag_client import RAGClient

class TestRAGClient:
    def setup_method(self):
        self.config = {
            "RAGFLOW_API_KEY": "test_key",
            "RAGFLOW_HOST": "http://test_host",
            "RAGFLOW_CHAT_ID": "test_chat_id"
        }
        self.client = RAGClient(self.config)

    @patch("src.apps.rag_base.core.rag_client.requests.get")
    def test_list_datasets(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 0, "data": [{"id": "1", "name": "test"}]}
        mock_get.return_value = mock_response

        result = self.client.list_datasets()
        
        assert result["status"] == "success"
        assert result["data"][0]["name"] == "test"
        mock_get.assert_called_with(
            "http://test_host/api/v1/datasets?page=1&page_size=30",
            headers={"Authorization": "Bearer test_key"}
        )

    @patch("src.apps.rag_base.core.rag_client.requests.post")
    def test_create_dataset(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 0, "data": {"id": "new_id"}}
        mock_post.return_value = mock_response

        result = self.client.create_dataset("new_dataset")
        
        assert result["status"] == "success"
        assert result["data"]["id"] == "new_id"

    @patch("src.apps.rag_base.core.rag_client.requests.post")
    def test_retrieve_and_answer_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Mock RAGFlow chat response structure
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "answer": "This is the answer.",
                "reference": {"total_similarity": 0.9}
            }
        }
        mock_post.return_value = mock_response

        result = self.client.retrieve_and_answer("question")
        
        assert result["answer"] == "This is the answer."
        assert result["confidence"] == 0.9

    def test_retrieve_and_answer_no_chat_id(self):
        client_no_chat = RAGClient({"RAGFLOW_API_KEY": "key"})
        result = client_no_chat.retrieve_and_answer("question")
        assert "not configured" in result["answer"]
        assert result["confidence"] == 0.0
