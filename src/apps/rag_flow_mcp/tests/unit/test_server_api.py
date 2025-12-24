import json
import pytest
from unittest.mock import MagicMock, patch
from src.apps.rag_flow_mcp.server import (
    fill_clarification_suggestions,
    evolve_scheme_document
)

# Mock engines to isolate API layer testing
@pytest.fixture
def mock_engines():
    with patch('src.apps.rag_flow_mcp.server.inference_engine') as mock_inf, \
         patch('src.apps.rag_flow_mcp.server.evolution_engine') as mock_evo, \
         patch('src.apps.rag_flow_mcp.server.governance_engine') as mock_gov, \
         patch('src.apps.rag_flow_mcp.server.legacy_processor', None):
        yield {
            'inference': mock_inf,
            'evolution': mock_evo,
            'governance': mock_gov
        }

def test_fill_clarification_suggestions_success(mock_engines):
    # Setup mock return
    expected_result = {"status": "success", "suggestions": []}
    mock_engines['inference'].fill_clarification_suggestions.return_value = expected_result
    
    # Call function
    result_json = fill_clarification_suggestions("/path/to/doc.md")
    
    # Verify
    result = json.loads(result_json)
    assert result == expected_result
    mock_engines['inference'].fill_clarification_suggestions.assert_called_once_with("/path/to/doc.md")

