import os
import sys
import json
import functools
import traceback

# Ensure core modules can be imported
if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)
    # Add project root
    project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from mcp.server.fastmcp import FastMCP
from src.common.logger import get_app_logger
try:
    from src.apps.rag_base.config import load_config
except ImportError:
    from config import load_config

from src.apps.rag_base.core.rag_client import RAGClient
from src.apps.rag_base.core.scenario_processor import ScenarioProcessor

# 1. Initialize Config & Logger
config = load_config()
logger = get_app_logger("rag_base")
logger.info("Initializing RAG Base Server...")

# 2. Initialize Core Components
rag_client = RAGClient(config)
scenario_processor = ScenarioProcessor(rag_client)

# 3. Initialize MCP
mcp = FastMCP("rag_base")

# Decorator for consistent logging
def log_tool_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tool_name = func.__name__
        try:
            logger.info(f"🔧 Calling Tool [{tool_name}] args={args} kwargs={kwargs}")
            result = func(*args, **kwargs)
            logger.info(f"✅ Tool [{tool_name}] Success")
            return result
        except Exception as e:
            logger.error(f"❌ Tool [{tool_name}] Failed: {e}")
            logger.error(traceback.format_exc())
            return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
    return wrapper

# --- Dataset Tools ---

@mcp.tool()
@log_tool_call
def create_dataset(name: str, avatar: str = "", description: str = "") -> str:
    """
    Create a new Knowledge Base (Dataset).
    """
    result = rag_client.create_dataset(name, avatar, description)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def delete_dataset(id: str) -> str:
    """
    Delete a Knowledge Base by ID.
    """
    result = rag_client.delete_dataset(id)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def list_datasets(page: int = 1, page_size: int = 30) -> str:
    """
    List all Knowledge Bases.
    """
    result = rag_client.list_datasets(page, page_size)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def update_dataset(id: str, name: str = None, description: str = None) -> str:
    """
    Update Knowledge Base metadata.
    """
    result = rag_client.update_dataset(id, name, description)
    return json.dumps(result, ensure_ascii=False, indent=2)

# --- Document Tools ---

@mcp.tool()
@log_tool_call
def upload_document(dataset_id: str, file_path: str) -> str:
    """
    Upload a file to a Knowledge Base.
    Args:
        dataset_id: The target Knowledge Base ID.
        file_path: Absolute path to the local file.
    """
    result = rag_client.upload_document(dataset_id, file_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def delete_document(dataset_id: str, document_id: str) -> str:
    """
    Delete a document from a Knowledge Base.
    """
    result = rag_client.delete_document(dataset_id, document_id)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def update_document(dataset_id: str, document_id: str, name: str = None, enabled: bool = None) -> str:
    """
    Update document metadata (rename or enable/disable).
    """
    result = rag_client.update_document(dataset_id, document_id, name, enabled)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def get_document_content(dataset_id: str, document_id: str) -> str:
    """
    Get parsed chunks of a document.
    """
    result = rag_client.get_document_content(dataset_id, document_id)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def list_documents(dataset_id: str, page: int = 1, page_size: int = 30, keywords: str = "") -> str:
    """
    List documents in a Knowledge Base.
    """
    result = rag_client.list_documents(dataset_id, page, page_size, keywords)
    return json.dumps(result, ensure_ascii=False, indent=2)

# --- Scenario 1 Tools ---

@mcp.tool()
@log_tool_call
def fill_clarification_suggestions(doc_path: str, dataset_id: str = "") -> str:
    """
    Scenario 1 Controller: Smart Clarification Suggestion Filling.
    Reads a Markdown file, identifies questions (Headers), retrieves answers from RAG,
    and fills them into a shadow copy of the file.
    
    Args:
        doc_path: Absolute path to the Markdown file.
        dataset_id: (Optional) ID of the Knowledge Base to search in. 
                    Currently uses the configured Chat Assistant's defaults.
    """
    result = scenario_processor.process_clarification_suggestions(doc_path, dataset_id)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def create_shadow_file(file_path: str) -> str:
    """
    Atomic Tool: Create a shadow copy of the document (_ai_revision).
    Returns the path of the created shadow file.
    """
    result = scenario_processor.create_shadow_file(file_path)
    return result

@mcp.tool()
@log_tool_call
def extract_questions_from_doc(file_path: str) -> str:
    """
    Atomic Tool: Extract questions from a Markdown document (headers).
    Returns a list of identified questions with line numbers.
    """
    result = scenario_processor.extract_questions(file_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def retrieve_rag_suggestion(query: str, dataset_id: str = "") -> str:
    """
    Atomic Tool: Retrieve a single suggestion from RAG.
    
    IMPORTANT: This tool expects a clean, well-formulated query.
    The Client/Agent should perform query rewriting (using its conversational LLM) 
    BEFORE calling this tool if the original input is messy or ambiguous.
    
    Args:
        query: The user query (optimized).
        dataset_id: Optional dataset ID.
    Returns the suggestion content, confidence, and references.
    """
    result = scenario_processor.retrieve_rag_suggestion(query, dataset_id)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def apply_suggestions_to_doc(file_path: str, suggestions_map: str) -> str:
    """
    Atomic Tool: Apply suggestions to the document.
    Args:
        file_path: Path to the shadow file.
        suggestions_map: JSON string mapping line index (int) to content (str).
    """
    try:
        data = json.loads(suggestions_map)
        result = scenario_processor.apply_suggestions(file_path, data)
        return json.dumps({"status": "success", "file": result}, ensure_ascii=False)
    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "Invalid JSON in suggestions_map"}, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()
