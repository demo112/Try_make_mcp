import json
import pytest
from unittest.mock import patch, MagicMock
from src.apps.rag_flow_mcp.server import dataset_manage, document_manage, file_manage

# ==========================
# Dataset Manage Tests
# ==========================

@patch('src.apps.rag_flow_mcp.tools.base_tools.create_dataset')
def test_dataset_manage_create(mock_create):
    mock_create.return_value = '{"id": "123"}'
    result = dataset_manage(action='create', name='test_ds', description='desc', avatar='img.png')
    mock_create.assert_called_with('test_ds', 'img.png', 'desc')
    assert result == '{"id": "123"}'

def test_dataset_manage_create_missing_name():
    result = dataset_manage(action='create')
    assert "name is required" in result

@patch('src.apps.rag_flow_mcp.tools.base_tools.delete_dataset')
def test_dataset_manage_delete(mock_delete):
    mock_delete.return_value = 'success'
    result = dataset_manage(action='delete', id='123')
    mock_delete.assert_called_with('123')
    assert result == 'success'

def test_dataset_manage_delete_missing_id():
    result = dataset_manage(action='delete')
    assert "id is required" in result

@patch('src.apps.rag_flow_mcp.tools.base_tools.update_dataset')
def test_dataset_manage_update(mock_update):
    mock_update.return_value = 'success'
    result = dataset_manage(action='update', id='123', name='new_name', description='new_desc')
    mock_update.assert_called_with('123', 'new_name', 'new_desc')
    assert result == 'success'

def test_dataset_manage_update_missing_id():
    result = dataset_manage(action='update')
    assert "id is required" in result

@patch('src.apps.rag_flow_mcp.tools.base_tools.list_datasets')
def test_dataset_manage_list(mock_list):
    mock_list.return_value = '[]'
    result = dataset_manage(action='list', page=2, page_size=10)
    mock_list.assert_called_with(2, 10)
    assert result == '[]'

def test_dataset_manage_unknown_action():
    result = dataset_manage(action='unknown')
    assert "Unknown action" in result

# ==========================
# Document Manage Tests
# ==========================

@patch('src.apps.rag_flow_mcp.tools.base_tools.upload_document')
def test_document_manage_upload(mock_upload):
    mock_upload.return_value = 'success'
    result = document_manage(action='upload', dataset_id='ds1', file_path='/tmp/file.txt')
    mock_upload.assert_called_with('ds1', '/tmp/file.txt')
    assert result == 'success'

def test_document_manage_upload_missing_path():
    result = document_manage(action='upload', dataset_id='ds1')
    assert "file_path is required" in result

@patch('src.apps.rag_flow_mcp.tools.base_tools.delete_document')
def test_document_manage_delete(mock_delete):
    mock_delete.return_value = 'success'
    result = document_manage(action='delete', dataset_id='ds1', document_id='doc1')
    mock_delete.assert_called_with('ds1', 'doc1')
    assert result == 'success'

def test_document_manage_delete_missing_id():
    result = document_manage(action='delete', dataset_id='ds1')
    assert "document_id is required" in result

@patch('src.apps.rag_flow_mcp.tools.base_tools.update_document')
def test_document_manage_update(mock_update):
    mock_update.return_value = 'success'
    result = document_manage(action='update', dataset_id='ds1', document_id='doc1', name='new', enabled=True)
    mock_update.assert_called_with('ds1', 'doc1', 'new', True)
    assert result == 'success'

@patch('src.apps.rag_flow_mcp.tools.base_tools.list_documents')
def test_document_manage_list(mock_list):
    mock_list.return_value = '[]'
    result = document_manage(action='list', dataset_id='ds1', page=1, page_size=20, keywords='key')
    mock_list.assert_called_with('ds1', 1, 20, 'key')
    assert result == '[]'

@patch('src.apps.rag_flow_mcp.tools.base_tools.get_document_content')
def test_document_manage_get_content(mock_get):
    mock_get.return_value = 'content'
    result = document_manage(action='get_content', dataset_id='ds1', document_id='doc1')
    mock_get.assert_called_with('ds1', 'doc1')
    assert result == 'content'

# ==========================
# File Manage Tests
# ==========================

@patch('src.apps.rag_flow_mcp.tools.base_tools.read_file')
def test_file_manage_read(mock_read):
    mock_read.return_value = 'content'
    result = file_manage(action='read', path='/path/to/file')
    mock_read.assert_called_with('/path/to/file')
    assert result == 'content'

@patch('src.apps.rag_flow_mcp.tools.base_tools.list_files')
def test_file_manage_list(mock_list):
    mock_list.return_value = '[]'
    result = file_manage(action='list', path='/dir', pattern='*.txt')
    mock_list.assert_called_with('/dir', '*.txt')
    assert result == '[]'
