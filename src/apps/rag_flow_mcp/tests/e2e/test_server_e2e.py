import pytest
import asyncio
from src.apps.rag_flow_mcp.server import mcp

@pytest.mark.asyncio
async def test_e2e_tools_registration():
    """
    Verify that all expected tools are registered in the MCP server instance.
    """
    expected_tools = [
        "mcp_rag_base_dataset_manage",
        "mcp_rag_base_document_manage",
        "mcp_rag_base_file_manage",
        "mcp_rag_base_retrieve_chunks",
        "mcp_rag_base_rewrite_query",
        "mcp_rag_base_inspect_config",
        "mcp_rag_flow_fill_clarification_suggestions",
        "mcp_rag_flow_evolve_scheme_document",
        "mcp_rag_flow_check_metadata_compliance",
        "mcp_rag_flow_validate_knowledge_conflict",
        "mcp_rag_flow_harvest_knowledge_candidates",
        "mcp_rag_flow_promote_knowledge",
        "mcp_rag_flow_view_diff",
        "mcp_rag_flow_add_test_case"
    ]
    
    # FastMCP stores tools in _tool_manager usually, but let's check _tools directly first
    # Based on common FastMCP usage:
    registered_tools = []
    
    if hasattr(mcp, '_tools'):
        registered_tools = list(mcp._tools.keys())
    elif hasattr(mcp, 'list_tools'):
         # list_tools might be async and return objects
         tools = await mcp.list_tools()
         registered_tools = [t.name for t in tools]
    
    print(f"Registered tools: {registered_tools}")
    
    for tool in expected_tools:
        assert tool in registered_tools, f"Tool {tool} not found in registered tools"

def test_e2e_server_startup():
    """
    Smoke test to ensure server module imports without error.
    """
    from src.apps.rag_flow_mcp import server
    assert server.mcp is not None
