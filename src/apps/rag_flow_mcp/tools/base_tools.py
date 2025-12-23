from typing import Any, Dict, List
import logging
from src.apps.rag_flow_mcp.core.rag_client import RAGClient
from src.apps.rag_flow_mcp.core.file_service import FileService
from src.apps.rag_flow_mcp.core.query_rewriter import QueryRewriter
from src.apps.rag_flow_mcp.config import load_config

logger = logging.getLogger(__name__)

# Initialize Clients
config = load_config()
rag_client = RAGClient(
    api_key=config["RAGFLOW_API_KEY"],
    base_url=config["RAGFLOW_HOST"],
    chat_id=config["RAGFLOW_CHAT_ID"],
    timeout=config["RAGFLOW_TIMEOUT"]
)
file_service = FileService()
query_rewriter = QueryRewriter(rag_client)

# --- File System Operations ---

def read_file(file_path: str) -> str:
    """Read content from a file."""
    try:
        return file_service.read_text(file_path)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return f"Error: {str(e)}"

def write_file(file_path: str, content: str) -> str:
    """Write content to a file (Use with caution)."""
    try:
        file_service.write_text(file_path, content)
        return "Success"
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return f"Error: {str(e)}"

def list_files(dir_path: str, pattern: str = "*") -> str:
    """List files in a directory."""
    try:
        files = file_service.list_files(dir_path, pattern)
        return str(files)
    except Exception as e:
        logger.error(f"Error listing files in {dir_path}: {e}")
        return f"Error: {str(e)}"

# --- RAG Operations ---

def create_dataset(name: str, avatar: str = "", description: str = "") -> str:
    """
    Create a new Knowledge Base (Dataset).
    """
    try:
        result = rag_client.create_dataset(name, avatar, description)
        return str(result)
    except Exception as e:
        logger.error(f"Error creating dataset: {e}")
        return f"Error: {str(e)}"

def delete_dataset(id: str) -> str:
    """
    Delete a Knowledge Base by ID.
    """
    try:
        result = rag_client.delete_dataset(id)
        return str(result)
    except Exception as e:
        logger.error(f"Error deleting dataset: {e}")
        return f"Error: {str(e)}"

def list_datasets(page: int = 1, page_size: int = 30) -> str:
    """
    List all Knowledge Bases.
    """
    try:
        result = rag_client.list_datasets(page, page_size)
        return str(result)
    except Exception as e:
        logger.error(f"Error listing datasets: {e}")
        return f"Error: {str(e)}"

def update_dataset(id: str, name: str = None, description: str = None) -> str:
    """
    Update Knowledge Base metadata.
    """
    try:
        result = rag_client.update_dataset(id, name, description)
        return str(result)
    except Exception as e:
        logger.error(f"Error updating dataset: {e}")
        return f"Error: {str(e)}"

def upload_document(dataset_id: str, file_path: str) -> str:
    """
    Upload a file to a Knowledge Base.
    Args:
        dataset_id: The target Knowledge Base ID.
        file_path: Absolute path to the local file.
    """
    try:
        result = rag_client.upload_document(dataset_id, file_path)
        return str(result)
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return f"Error: {str(e)}"

def delete_document(dataset_id: str, document_id: str) -> str:
    """
    Delete a document from a Knowledge Base.
    """
    try:
        result = rag_client.delete_document(dataset_id, document_id)
        return str(result)
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return f"Error: {str(e)}"

def update_document(dataset_id: str, document_id: str, name: str = None, enabled: bool = None) -> str:
    """
    Update document metadata (rename or enable/disable).
    """
    try:
        result = rag_client.update_document(dataset_id, document_id, name, enabled)
        return str(result)
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        return f"Error: {str(e)}"

def get_document_content(dataset_id: str, document_id: str) -> str:
    """
    Get parsed chunks of a document.
    """
    try:
        result = rag_client.get_document_content(dataset_id, document_id)
        return str(result)
    except Exception as e:
        logger.error(f"Error getting document content: {e}")
        return f"Error: {str(e)}"

def list_documents(dataset_id: str, page: int = 1, page_size: int = 30, keywords: str = "") -> str:
    """
    List documents in a Knowledge Base.
    """
    try:
        result = rag_client.list_documents(dataset_id, page, page_size, keywords)
        return str(result)
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return f"Error: {str(e)}"

def retrieve_chunks(dataset_id: str, query: str, page: int = 1, page_size: int = 30, similarity_threshold: float = 0.2) -> str:
    """
    [Knowledge Retrieval] Directly retrieve chunks from the knowledge base (without LLM generation).
    Suitable for finding relevant content without QA.
    """
    try:
        result = rag_client.retrieve_chunks(dataset_id, query, page, page_size, similarity_threshold)
        return str(result)
    except Exception as e:
        logger.error(f"Error retrieving chunks: {e}")
        return f"Error: {str(e)}"

import json

def rewrite_query(query: str, context: str = "") -> str:
    """
    [Query Rewrite] Optimize user query for better retrieval.
    Args:
        query: The original user query.
        context: Optional context to help with rewriting.
    """
    try:
        result = query_rewriter.rewrite(query, context)
        return str(result)
    except Exception as e:
        logger.error(f"Error rewriting query: {e}")
        return f"Error: {str(e)}"

def inspect_config() -> str:
    """
    [System] Inspect current configuration (sensitive data masked).
    """
    try:
        safe_config = config.copy()
        if "RAGFLOW_API_KEY" in safe_config:
            key = safe_config["RAGFLOW_API_KEY"]
            safe_config["RAGFLOW_API_KEY"] = f"{key[:4]}***{key[-4:]}" if len(key) > 8 else "***"
        return json.dumps(safe_config, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error inspecting config: {e}")
        return f"Error: {str(e)}"
