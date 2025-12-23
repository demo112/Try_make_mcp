
import pytest
import json
from src.testing.client import McpTestClient

def test_rag_base_tools_list(mcp_client: McpTestClient):
    """Verify all RAG tools are registered"""
    tools = mcp_client.list_tools()
    tool_names = [t["name"] for t in tools]
    
    expected_tools = [
        "create_dataset", "list_datasets", "delete_dataset", "update_dataset",
        "upload_document", "list_documents", "delete_document", 
        "get_document_content", "update_document",
        "fill_clarification_suggestions"
    ]
    
    for tool in expected_tools:
        assert tool in tool_names

def test_list_datasets_call(mcp_client: McpTestClient):
    """
    Test calling list_datasets.
    Note: This will try to hit the real API if env is set, or fail gracefully.
    We just check if the call returns a valid JSON structure (even if it's an error).
    """
    result = mcp_client.call_tool("list_datasets", {"page": 1, "page_size": 10})
    # Result is a stringified JSON
    assert len(result) > 0
    
    # Parse the result string
    try:
        data = json.loads(result[0]["text"])
        # Should have status or message
        assert "status" in data or "code" in data
    except json.JSONDecodeError:
        pytest.fail(f"Tool output is not valid JSON: {result[0]['text']}")
