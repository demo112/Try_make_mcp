import pytest
from src.testing.client import McpTestClient

def test_tool_list(mcp_client: McpTestClient):
    """测试工具列表是否包含 hello_world"""
    tools = mcp_client.list_tools()
    names = [t["name"] for t in tools]
    assert "hello_world" in names

def test_hello_world(mcp_client: McpTestClient):
    """测试 hello_world 工具调用"""
    result = mcp_client.call_tool("hello_world")
    assert len(result) > 0
    text_content = result[0]["text"]
    assert "Hello" in text_content
    assert "RAG评估工作流" in text_content
