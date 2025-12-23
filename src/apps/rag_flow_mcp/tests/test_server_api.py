import json
import pytest
from unittest.mock import MagicMock, patch
from src.apps.rag_flow_mcp.server import (
    fill_clarification_suggestions,
    evolve_scheme_document,
    harvest_knowledge_candidates,
    promote_knowledge,
    validate_knowledge_conflict
)

# Mock engines to isolate API layer testing
@pytest.fixture
def mock_engines():
    with patch('src.apps.rag_flow_mcp.server.inference_engine') as mock_inf, \
         patch('src.apps.rag_flow_mcp.server.evolution_engine') as mock_evo, \
         patch('src.apps.rag_flow_mcp.server.lifecycle_engine') as mock_life, \
         patch('src.apps.rag_flow_mcp.server.governance_engine') as mock_gov:
        yield {
            'inference': mock_inf,
            'evolution': mock_evo,
            'lifecycle': mock_life,
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

def test_promote_knowledge_valid_json(mock_engines):
    # Setup mock
    mock_engines['lifecycle'].promote_knowledge.return_value = {"status": "success"}
    
    # Valid JSON input
    candidate = {"id": "123", "question": "q", "answer": "a"}
    candidate_json = json.dumps(candidate)
    
    # Call function
    result_json = promote_knowledge(candidate_json, "/target/path")
    
    # Verify
    result = json.loads(result_json)
    assert result["status"] == "success"
    mock_engines['lifecycle'].promote_knowledge.assert_called_once_with(candidate, "/target/path")

def test_promote_knowledge_invalid_json(mock_engines):
    # Invalid JSON input
    invalid_json = "{bad_json}"
    
    # Call function
    result_json = promote_knowledge(invalid_json, "/target/path")
    
    # Verify error handling
    result = json.loads(result_json)
    assert result["status"] == "error"
    assert "Invalid JSON format" in result["message"]
    mock_engines['lifecycle'].promote_knowledge.assert_not_called()

def test_validate_knowledge_conflict_invalid_json(mock_engines):
    # Invalid JSON input
    invalid_json = "not a json"
    
    # Call function
    result_json = validate_knowledge_conflict(invalid_json)
    
    # Verify error handling
    result = json.loads(result_json)
    assert result["status"] == "error"
    assert "Invalid JSON format" in result["message"]
    mock_engines['governance'].validate_knowledge_conflict.assert_not_called()
