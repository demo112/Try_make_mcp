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

# @mcp.tool(name="mcp_rag_flow_check_metadata_compliance")
# @log_tool_call
# def check_metadata_compliance(doc_path: str) -> str:
#     """
#     [治理管控] 检查文档是否包含必要的元数据 (如 product, module 等)。
#     """
#     return json.dumps({"status": "disabled", "message": "Governance Engine is temporarily disabled."}, ensure_ascii=False)
#     # result = governance_engine.check_metadata_compliance(doc_path)
#     # return json.dumps(result, ensure_ascii=False, indent=2)

# @mcp.tool(name="mcp_rag_flow_validate_knowledge_conflict")
# @log_tool_call
# def validate_knowledge_conflict(candidate_json: str) -> str:
#     """
#     [治理管控] 验证知识候选是否与现有知识库冲突。
#     
#     Args:
#         candidate_json: 候选知识的 JSON 字符串。
#     """
#     return json.dumps({"status": "disabled", "message": "Governance Engine is temporarily disabled."}, ensure_ascii=False)
#     # try:
#     #     candidate_data = json.loads(candidate_json)
#     #     result = governance_engine.validate_knowledge_conflict(candidate_data)
#     # except json.JSONDecodeError as e:
#     #     return json.dumps({"status": "error", "message": f"Invalid JSON format: {e}"}, ensure_ascii=False)
#     # return json.dumps(result, ensure_ascii=False, indent=2)

# @mcp.tool(name="mcp_rag_flow_harvest_knowledge_candidates")
# @log_tool_call
# def harvest_knowledge_candidates(doc_path: str) -> str:
#     """
#     [支线任务] 从澄清文档中收割知识候选。
#     仅提取已确认且有答案的条目。
#     """
#     return json.dumps({"status": "disabled", "message": "Lifecycle Engine is temporarily disabled."}, ensure_ascii=False)
#     # result = lifecycle_engine.harvest_knowledge_candidates(doc_path)
#     # return json.dumps(result, ensure_ascii=False, indent=2)

# @mcp.tool(name="mcp_rag_flow_promote_knowledge")
# @log_tool_call
# def promote_knowledge(candidate_json: str, target_kb_path: str) -> str:
#     """
#     [支线任务] 将知识候选晋升到永久知识库 (L1/L2)。
#     
#     Args:
#         candidate_json: 候选知识的 JSON 字符串。
#         target_kb_path: 目标知识库的目录路径。
#     """
#     return json.dumps({"status": "disabled", "message": "Lifecycle Engine is temporarily disabled."}, ensure_ascii=False)
#     # try:
#     #     candidate_data = json.loads(candidate_json)
#     #     result = lifecycle_engine.promote_knowledge(candidate_data, target_kb_path)
#     # except json.JSONDecodeError as e:
#     #     return json.dumps({"status": "error", "message": f"Invalid JSON format: {e}"}, ensure_ascii=False)
#     # return json.dumps(result, ensure_ascii=False, indent=2)

# ==========================================
# Implementation Tools (mcp_rag_base_*)
# ==========================================

@mcp.tool(name="mcp_rag_base_dataset_manage")
@log_tool_call
def dataset_manage(
    action: str, 
    id: str = None, 
    name: str = None, 
    description: str = None, 
    avatar: str = "",
    page: int = 1,
    page_size: int = 30
) -> str:
    """
    Manage Knowledge Bases (Datasets).
    
    Args:
        action: One of ['create', 'delete', 'update', 'list'].
        id: Dataset ID (required for delete/update).
        name: Dataset Name (required for create, optional for update).
        description: Description (optional for create/update).
        avatar: Avatar (optional for create).
        page: Page number (for list).
        page_size: Page size (for list).
    """
    if action == 'create':
        if not name: return json.dumps({"error": "name is required for create"}, ensure_ascii=False)
        return base_tools.create_dataset(name, avatar, description)
    elif action == 'delete':
        if not id: return json.dumps({"error": "id is required for delete"}, ensure_ascii=False)
        return base_tools.delete_dataset(id)
    elif action == 'update':
        if not id: return json.dumps({"error": "id is required for update"}, ensure_ascii=False)
        return base_tools.update_dataset(id, name, description)
    elif action == 'list':
        return base_tools.list_datasets(page, page_size)
    else:
        return json.dumps({"error": f"Unknown action: {action}"}, ensure_ascii=False)

@mcp.tool(name="mcp_rag_base_document_manage")
@log_tool_call
def document_manage(
    action: str,
    dataset_id: str,
    document_id: str = None,
    file_path: str = None,
    name: str = None,
    enabled: bool = None,
    keywords: str = "",
    page: int = 1,
    page_size: int = 30
) -> str:
    """
    Manage Documents in a Knowledge Base.
    
    Args:
        action: One of ['upload', 'delete', 'update', 'list', 'get_content'].
        dataset_id: Target Dataset ID (required for all).
        document_id: Document ID (required for delete/update/get_content).
        file_path: Local file path (required for upload).
        name: New name (optional for update).
        enabled: Enable/Disable (optional for update).
        keywords: Search keywords (optional for list).
        page: Page number (for list).
        page_size: Page size (for list).
    """
    if action == 'upload':
        if not file_path: return json.dumps({"error": "file_path is required for upload"}, ensure_ascii=False)
        return base_tools.upload_document(dataset_id, file_path)
    elif action == 'delete':
        if not document_id: return json.dumps({"error": "document_id is required for delete"}, ensure_ascii=False)
        return base_tools.delete_document(dataset_id, document_id)
    elif action == 'update':
        if not document_id: return json.dumps({"error": "document_id is required for update"}, ensure_ascii=False)
        return base_tools.update_document(dataset_id, document_id, name, enabled)
    elif action == 'list':
        return base_tools.list_documents(dataset_id, page, page_size, keywords)
    elif action == 'get_content':
        if not document_id: return json.dumps({"error": "document_id is required for get_content"}, ensure_ascii=False)
        return base_tools.get_document_content(dataset_id, document_id)
    else:
        return json.dumps({"error": f"Unknown action: {action}"}, ensure_ascii=False)

@mcp.tool(name="mcp_rag_base_file_manage")
@log_tool_call
def file_manage(
    action: str,
    path: str,
    pattern: str = "*"
) -> str:
    """
    Local File System Operations.
    
    Args:
        action: One of ['read', 'list'].
        path: File path (for read) or Directory path (for list).
        pattern: Glob pattern (only for list).
    """
    if action == 'read':
        return base_tools.read_file(path)
    elif action == 'list':
        return base_tools.list_files(path, pattern)
    else:
        return json.dumps({"error": f"Unknown action: {action}"}, ensure_ascii=False)

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

@mcp.tool(name="mcp_rag_base_inspect_config")
@log_tool_call
def inspect_config() -> str:
    """[System] Inspect current configuration (sensitive data masked)."""
    return base_tools.inspect_config()

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
