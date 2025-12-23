import pytest
from unittest.mock import MagicMock, patch
from src.apps.rag_flow_mcp.core.query_rewriter import QueryRewriter
from src.apps.rag_flow_mcp.core.rag_client import RAGClient

class TestQueryRewriter:
    
    @pytest.fixture
    def mock_rag_client(self):
        client = MagicMock(spec=RAGClient)
        # Default behavior: chat_id is set
        client.chat_id = "test_chat_id"
        return client

    def test_rewrite_success(self, mock_rag_client):
        """Test successful query rewriting."""
        mock_rag_client.call_llm.return_value = "rewritten query"
        rewriter = QueryRewriter(mock_rag_client)
        
        result = rewriter.rewrite("original query", "context")
        
        assert result == "rewritten query"
        mock_rag_client.call_llm.assert_called_once()

    def test_rewrite_no_chat_id(self, mock_rag_client):
        """Test fallback when chat_id is missing."""
        mock_rag_client.chat_id = ""
        rewriter = QueryRewriter(mock_rag_client)
        
        result = rewriter.rewrite("original query", "context")
        
        # Should return original query and NOT call LLM
        assert result == "original query"
        mock_rag_client.call_llm.assert_not_called()

    def test_rewrite_exception(self, mock_rag_client):
        """Test fallback when LLM call fails."""
        mock_rag_client.call_llm.side_effect = Exception("API Error")
        rewriter = QueryRewriter(mock_rag_client)
        
        result = rewriter.rewrite("original query", "context")
        
        # Should return original query on error
        assert result == "original query"
