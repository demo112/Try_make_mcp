import pytest
import json
import requests_mock
from src.apps.rag_flow_mcp.core.rag_client import RAGClient
from src.apps.rag_flow_mcp.tools import base_tools

@pytest.fixture
def mock_config(monkeypatch):
    monkeypatch.setenv("RAGFLOW_API_KEY", "test_key")
    monkeypatch.setenv("RAGFLOW_HOST", "http://mock-ragflow")
    monkeypatch.setenv("RAGFLOW_CHAT_ID", "test_chat")
    monkeypatch.setenv("RAGFLOW_TIMEOUT", "10")

@pytest.fixture
def rag_client_instance(mock_config):
    # Re-import to pick up env vars or re-init
    # Since base_tools initializes it globally, we might need to patch it there
    client = RAGClient("test_key", "http://mock-ragflow")
    return client

def test_create_dataset_integration(requests_mock):
    requests_mock.post("http://mock-ragflow/api/v1/datasets", 
                       json={"code": 0, "data": {"id": "ds_123", "name": "test"}})
    
    # We need to patch the global rag_client in base_tools
    with pytest.MonkeyPatch().context() as m:
        client = RAGClient("test_key", "http://mock-ragflow")
        m.setattr(base_tools, 'rag_client', client)
        
        result = base_tools.create_dataset("test")
        assert "ds_123" in result

def test_upload_document_integration(requests_mock, tmp_path):
    # Create dummy file
    f = tmp_path / "test.txt"
    f.write_text("content")
    
    requests_mock.post("http://mock-ragflow/api/v1/datasets/ds_123/documents",
                       json={"code": 0, "data": {"id": "doc_456"}})
    
    with pytest.MonkeyPatch().context() as m:
        client = RAGClient("test_key", "http://mock-ragflow")
        m.setattr(base_tools, 'rag_client', client)
        
        result = base_tools.upload_document("ds_123", str(f))
        assert "doc_456" in result

def test_list_datasets_integration(requests_mock):
    requests_mock.get("http://mock-ragflow/api/v1/datasets?page=1&page_size=30",
                      json={"code": 0, "data": [{"id": "ds_1"}]})
    
    with pytest.MonkeyPatch().context() as m:
        client = RAGClient("test_key", "http://mock-ragflow")
        m.setattr(base_tools, 'rag_client', client)
        
        result = base_tools.list_datasets()
        assert "ds_1" in result

def test_retrieve_chunks_integration(requests_mock):
    requests_mock.post("http://mock-ragflow/api/v1/retrieval",
                       json={"code": 0, "data": [{"content_with_weight": "chunk1"}]})
    
    with pytest.MonkeyPatch().context() as m:
        client = RAGClient("test_key", "http://mock-ragflow")
        m.setattr(base_tools, 'rag_client', client)
        
        result = base_tools.retrieve_chunks("ds_1", "query")
        assert "chunk1" in result
