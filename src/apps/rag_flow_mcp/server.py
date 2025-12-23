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
    project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from mcp.server.fastmcp import FastMCP
from src.common import get_app_logger
from dotenv import load_dotenv

# Load .env
load_dotenv()

try:
    from config import load_config
except ImportError:
    from src.apps.rag_flow_mcp.config import load_config

from engines import (
    InferenceEngine,
    EvolutionEngine,
    GovernanceEngine,
    LifecycleEngine
)

# Import Implementation Tools
from src.apps.rag_flow_mcp.tools import base_tools

# Initialize Configuration and Logger
config = load_config()
logger = get_app_logger("rag_flow_mcp")

# Log loaded configuration (masking sensitive info)
safe_config = config.copy()
if "RAGFLOW_API_KEY" in safe_config:
    safe_config["RAGFLOW_API_KEY"] = "***" + safe_config["RAGFLOW_API_KEY"][-4:] if len(safe_config["RAGFLOW_API_KEY"]) > 4 else "***"
logger.info(f"Loaded Configuration: {json.dumps(safe_config, ensure_ascii=False)}")

mcp = FastMCP("rag_flow_mcp")

# Logging Decorator
def log_tool_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tool_name = func.__name__
        try:
            logger.info(f"🔧 Calling Tool [{tool_name}]")
            if args:
                logger.info(f"  Args: {args}")
            if kwargs:
                logger.info(f"  Kwargs: {json.dumps(kwargs, ensure_ascii=False)}")
            
            result = func(*args, **kwargs)
            
            res_str = str(result)
            if len(res_str) > 500:
                res_str = res_str[:500] + "... (truncated)"
            logger.info(f"✅ Tool [{tool_name}] Success: {res_str}")
            
            return result
        except Exception as e:
            logger.error(f"❌ Tool [{tool_name}] Failed: {e}")
            logger.error(traceback.format_exc())
            return json.dumps({
                "status": "error", 
                "message": f"Tool execution failed: {str(e)}",
                "details": traceback.format_exc()
            }, ensure_ascii=False)
    return wrapper

# Initialize Engines
inference_engine = InferenceEngine(config)
evolution_engine = EvolutionEngine(config)
governance_engine = GovernanceEngine(config)
# lifecycle_engine = LifecycleEngine(config)

inference_engine.initialize()
evolution_engine.initialize()
governance_engine.initialize()
# lifecycle_engine.initialize()

try:
    from src.apps.rag_flow_mcp.legacy_core.scenario_processor import ScenarioProcessor as LegacyScenarioProcessor
    legacy_processor = LegacyScenarioProcessor(inference_engine.rag_client) if hasattr(inference_engine, 'rag_client') else None
except ImportError:
    legacy_processor = None

# ==========================================
# Logic Tools (mcp_rag_flow_*)
# ==========================================

@mcp.tool(name="mcp_rag_flow_fill_clarification_suggestions")
@log_tool_call
def fill_clarification_suggestions(doc_path: str, dataset_id: str = "") -> str:
    """
    [主线任务] 填充澄清建议 (Hybrid: Prefer Legacy Logic).
    读取评审问题记录文档，调用 RAG 检索知识库，并将带有置信度的建议填入文档。
    
    Args:
        doc_path: '04_评审问题记录.md' 的绝对路径。
        dataset_id: (Optional) ID of the Knowledge Base to search in.
    """
    if legacy_processor:
        result = legacy_processor.process_clarification_suggestions(doc_path, dataset_id)
    else:
        result = inference_engine.fill_clarification_suggestions(doc_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool(name="mcp_rag_flow_evolve_scheme_document")
@log_tool_call
def evolve_scheme_document(scheme_doc_path: str, clarification_doc_path: str) -> str:
    """
    [主线任务] 基于澄清决策进化方案文档。
    将已确认的澄清点应用到原方案文档中，生成 v1.1 版本。
    
    Args:
        scheme_doc_path: 原方案文档 (v1.0) 的路径。
        clarification_doc_path: 已澄清的问题记录文档路径。
    """
    result = evolution_engine.evolve_scheme_document(scheme_doc_path, clarification_doc_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool(name="mcp_rag_flow_check_metadata_compliance")
@log_tool_call
def check_metadata_compliance(doc_path: str) -> str:
    """
    [治理管控] 检查文档是否包含必要的元数据 (如 product, module 等)。
    """
    return json.dumps({"status": "disabled", "message": "Governance Engine is temporarily disabled."}, ensure_ascii=False)
    # result = governance_engine.check_metadata_compliance(doc_path)
    # return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool(name="mcp_rag_flow_validate_knowledge_conflict")
@log_tool_call
def validate_knowledge_conflict(candidate_json: str) -> str:
    """
    [治理管控] 验证知识候选是否与现有知识库冲突。
    
    Args:
        candidate_json: 候选知识的 JSON 字符串。
    """
    return json.dumps({"status": "disabled", "message": "Governance Engine is temporarily disabled."}, ensure_ascii=False)
    # try:
    #     candidate_data = json.loads(candidate_json)
    #     result = governance_engine.validate_knowledge_conflict(candidate_data)
    # except json.JSONDecodeError as e:
    #     return json.dumps({"status": "error", "message": f"Invalid JSON format: {e}"}, ensure_ascii=False)
    # return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool(name="mcp_rag_flow_harvest_knowledge_candidates")
@log_tool_call
def harvest_knowledge_candidates(doc_path: str) -> str:
    """
    [支线任务] 从澄清文档中收割知识候选。
    仅提取已确认且有答案的条目。
    """
    return json.dumps({"status": "disabled", "message": "Lifecycle Engine is temporarily disabled."}, ensure_ascii=False)
    # result = lifecycle_engine.harvest_knowledge_candidates(doc_path)
    # return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool(name="mcp_rag_flow_promote_knowledge")
@log_tool_call
def promote_knowledge(candidate_json: str, target_kb_path: str) -> str:
    """
    [支线任务] 将知识候选晋升到永久知识库 (L1/L2)。
    
    Args:
        candidate_json: 候选知识的 JSON 字符串。
        target_kb_path: 目标知识库的目录路径。
    """
    return json.dumps({"status": "disabled", "message": "Lifecycle Engine is temporarily disabled."}, ensure_ascii=False)
    # try:
    #     candidate_data = json.loads(candidate_json)
    #     result = lifecycle_engine.promote_knowledge(candidate_data, target_kb_path)
    # except json.JSONDecodeError as e:
    #     return json.dumps({"status": "error", "message": f"Invalid JSON format: {e}"}, ensure_ascii=False)
    # return json.dumps(result, ensure_ascii=False, indent=2)

# ==========================================
# Implementation Tools (mcp_rag_base_*)
# ==========================================

@mcp.tool(name="mcp_rag_base_create_dataset")
@log_tool_call
def create_dataset(name: str, avatar: str = "", description: str = "") -> str:
    """Create a new Knowledge Base (Dataset)."""
    return base_tools.create_dataset(name, avatar, description)

@mcp.tool(name="mcp_rag_base_delete_dataset")
@log_tool_call
def delete_dataset(id: str) -> str:
    """Delete a Knowledge Base by ID."""
    return base_tools.delete_dataset(id)

@mcp.tool(name="mcp_rag_base_list_datasets")
@log_tool_call
def list_datasets(page: int = 1, page_size: int = 30) -> str:
    """List all Knowledge Bases."""
    return base_tools.list_datasets(page, page_size)

@mcp.tool(name="mcp_rag_base_update_dataset")
@log_tool_call
def update_dataset(id: str, name: str = None, description: str = None) -> str:
    """Update Knowledge Base metadata."""
    return base_tools.update_dataset(id, name, description)

@mcp.tool(name="mcp_rag_base_upload_document")
@log_tool_call
def upload_document(dataset_id: str, file_path: str) -> str:
    """
    Upload a file to a Knowledge Base.
    Args:
        dataset_id: The target Knowledge Base ID.
        file_path: Absolute path to the local file.
    """
    return base_tools.upload_document(dataset_id, file_path)

@mcp.tool(name="mcp_rag_base_delete_document")
@log_tool_call
def delete_document(dataset_id: str, document_id: str) -> str:
    """Delete a document from a Knowledge Base."""
    return base_tools.delete_document(dataset_id, document_id)

@mcp.tool(name="mcp_rag_base_update_document")
@log_tool_call
def update_document(dataset_id: str, document_id: str, name: str = None, enabled: bool = None) -> str:
    """Update document metadata (rename or enable/disable)."""
    return base_tools.update_document(dataset_id, document_id, name, enabled)

@mcp.tool(name="mcp_rag_base_get_document_content")
@log_tool_call
def get_document_content(dataset_id: str, document_id: str) -> str:
    """Get parsed chunks of a document."""
    return base_tools.get_document_content(dataset_id, document_id)

@mcp.tool(name="mcp_rag_base_list_documents")
@log_tool_call
def list_documents(dataset_id: str, keywords: str = "", page: int = 1, page_size: int = 30) -> str:
    """List documents in a Knowledge Base."""
    return base_tools.list_documents(dataset_id, page, page_size, keywords)

@mcp.tool(name="mcp_rag_base_retrieve_chunks")
@log_tool_call
def retrieve_chunks(dataset_id: str, query: str, page: int = 1, page_size: int = 30, similarity_threshold: float = 0.2) -> str:
    """
    [知识检索] 直接检索知识库切片 (不经过 LLM 生成)。
    适用于只查找相关内容而不进行问答的场景。
    
    Args:
        dataset_id: 知识库 ID
        query: 检索关键词或问题
        page: 页码 (默认 1)
        page_size: 每页数量 (默认 30)
        similarity_threshold: 相似度阈值 (0.0~1.0, 默认 0.2)
    """
    return base_tools.retrieve_chunks(dataset_id, query, page, page_size, similarity_threshold)

@mcp.tool(name="mcp_rag_base_rewrite_query")
@log_tool_call
def rewrite_query(query: str, context: str = "") -> str:
    """
    [Query Rewrite] Optimize user query for better retrieval.
    
    Args:
        query: The original user query.
        context: Optional context to help with rewriting.
    """
    return base_tools.rewrite_query(query, context)

@mcp.tool(name="mcp_rag_base_read_file")
@log_tool_call
def read_file(file_path: str) -> str:
    """Read content from a local file."""
    return base_tools.read_file(file_path)

@mcp.tool(name="mcp_rag_base_list_files")
@log_tool_call
def list_files(dir_path: str, pattern: str = "*") -> str:
    """List files in a local directory."""
    return base_tools.list_files(dir_path, pattern)

@mcp.tool(name="mcp_rag_base_inspect_config")
@log_tool_call
def inspect_config() -> str:
    """[System] Inspect current configuration (sensitive data masked)."""
    return base_tools.inspect_config()

# --- Atomic / Helper Tools (Also classified as Base/Implementation) ---

@mcp.tool(name="mcp_rag_base_fill_clarification_suggestions")
@log_tool_call
def fill_clarification_suggestions_controller(doc_path: str, dataset_id: str = "") -> str:
    """
    Scenario 1 Controller: Smart Clarification Suggestion Filling.
    Reads a Markdown file, identifies questions (Headers), retrieves answers from RAG,
    and fills them into a shadow copy of the file.
    
    Args:
        doc_path: Absolute path to the Markdown file.
        dataset_id: (Optional) ID of the Knowledge Base to search in. 
                    Currently uses the configured Chat Assistant's defaults.
    """
    # Note: This duplicates functionality of mcp_rag_flow_fill_clarification_suggestions but is kept for compatibility
    # or as a base controller if the flow tool adds more logic.
    # For now, let's redirect to the flow tool implementation or logic.
    if legacy_processor:
        result = legacy_processor.process_clarification_suggestions(doc_path, dataset_id)
    else:
        result = inference_engine.fill_clarification_suggestions(doc_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool(name="mcp_rag_base_create_shadow_file")
@log_tool_call
def create_shadow_file(file_path: str) -> str:
    """
    Atomic Tool: Create a shadow copy of the document (_ai_revision).
    Returns the path of the created shadow file.
    """
    if legacy_processor:
        return legacy_processor.create_shadow_file(file_path)
    return ""

@mcp.tool(name="mcp_rag_base_extract_questions_from_doc")
@log_tool_call
def extract_questions_from_doc(file_path: str) -> str:
    """
    Atomic Tool: Extract questions from a Markdown document (headers).
    Returns a list of identified questions with line numbers.
    """
    if legacy_processor:
        result = legacy_processor.extract_questions(file_path)
        return json.dumps(result, ensure_ascii=False, indent=2)
    return "[]"

@mcp.tool(name="mcp_rag_base_retrieve_rag_suggestion")
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
    if legacy_processor:
        result = legacy_processor.retrieve_rag_suggestion(query, dataset_id)
        return json.dumps(result, ensure_ascii=False, indent=2)
    return "{}"

@mcp.tool(name="mcp_rag_base_apply_suggestions_to_doc")
@log_tool_call
def apply_suggestions_to_doc(file_path: str, suggestions_map: str) -> str:
    """
    Atomic Tool: Apply suggestions to the document.
    Args:
        file_path: Path to the shadow file.
        suggestions_map: JSON string mapping line index (int) to content (str).
    """
    try:
        suggestions = json.loads(suggestions_map)
        # Convert keys to int
        suggestions = {int(k): v for k, v in suggestions.items()}
        if legacy_processor:
             result = legacy_processor.apply_suggestions(file_path, suggestions)
             return str(result)
        return "Legacy processor not available"
    except Exception as e:
        return f"Error: {e}"

# --- Other Tools ---

from src.apps.rag_flow_mcp.tools.visualization import view_last_diff
from src.apps.rag_flow_mcp.tools.qa_tool import capture_test_case

@mcp.tool(name="mcp_rag_flow_view_diff")
@log_tool_call
def view_diff(file_path: str) -> str:
    """
    [体验优化] 打开 VS Code 对比视图。
    对比指定文件的当前内容与其最新的影子副本 (Shadow Copy)。
    """
    result = view_last_diff(file_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool(name="mcp_rag_flow_add_test_case")
@log_tool_call
def add_test_case(query: str, expected_keywords: list[str], expected_document: str = "") -> str:
    """
    [闭环优化] 捕获测试用例到黄金数据集。
    """
    result = capture_test_case(query, expected_keywords, expected_document)
    return json.dumps(result, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    mcp.run()
