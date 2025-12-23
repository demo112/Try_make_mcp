import pytest
from src.testing.client import McpTestClient

def test_tool_list(mcp_client: McpTestClient):
    """测试工具列表是否包含预期工具"""
    tools = mcp_client.list_tools()
    names = [t["name"] for t in tools]
    assert "generate_test_dataset" in names
    assert "run_qa_test" in names
    assert "evaluate_answers" in names
