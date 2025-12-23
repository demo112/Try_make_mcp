import os
import sys
import json
import functools
import traceback

# Ensure core modules can be imported
# Must be done BEFORE importing from src or local modules
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    sys.path.append(sys._MEIPASS)
else:
    # Running in a normal Python environment
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)
    
    # Add project root to sys.path to allow 'src' imports
    # current_dir is .../src/apps/rag_flow_mcp
    # root is .../ (3 levels up)
    project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from mcp.server.fastmcp import FastMCP
from src.common import get_app_logger

__version__ = "2.0.0"

try:
    from config import load_config
except ImportError:
    # Try absolute import if relative/implicit fails
    from src.apps.rag_flow_mcp.config import load_config

from engines import (
    InferenceEngine,
    EvolutionEngine,
    GovernanceEngine,
    LifecycleEngine
)

# Initialize Configuration and Logger
# Ensure .env is loaded correctly from CWD if running as script
from dotenv import load_dotenv
load_dotenv()

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
            # Log input
            logger.info(f"🔧 Calling Tool [{tool_name}]")
            if args:
                logger.info(f"  Args: {args}")
            if kwargs:
                logger.info(f"  Kwargs: {json.dumps(kwargs, ensure_ascii=False)}")
            
            # Execute
            result = func(*args, **kwargs)
            
            # Log output (truncate if too long)
            res_str = str(result)
            if len(res_str) > 500:
                res_str = res_str[:500] + "... (truncated)"
            logger.info(f"✅ Tool [{tool_name}] Success: {res_str}")
            
            return result
        except Exception as e:
            logger.error(f"❌ Tool [{tool_name}] Failed: {e}")
            logger.error(traceback.format_exc())
            # Re-raise or return error JSON depending on strategy. 
            # MCP usually expects tools to return a string result even on error to show to LLM.
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
lifecycle_engine = LifecycleEngine(config)

# Initialize them (Connect to RAG, etc.)
inference_engine.initialize()
evolution_engine.initialize()
governance_engine.initialize()
lifecycle_engine.initialize()

# --- Main Task Tools (Inference & Evolution) ---

@mcp.tool()
@log_tool_call
def fill_clarification_suggestions(doc_path: str) -> str:
    """
    [主线任务] 填充澄清建议 (P0 - 核心功能)。
    读取评审问题记录文档，调用 RAG 检索知识库，并将带有置信度的建议填入文档。
    
    Args:
        doc_path: '04_评审问题记录.md' 的绝对路径。
    """
    result = inference_engine.fill_clarification_suggestions(doc_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
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

# --- Governance Tools ---

@mcp.tool()
@log_tool_call
def check_metadata_compliance(doc_path: str) -> str:
    """
    [治理管控] 检查文档是否包含必要的元数据 (如 product, module 等)。
    """
    result = governance_engine.check_metadata_compliance(doc_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def validate_knowledge_conflict(candidate_json: str) -> str:
    """
    [治理管控] 验证知识候选是否与现有知识库冲突。
    
    Args:
        candidate_json: 候选知识的 JSON 字符串。
    """
    try:
        candidate_data = json.loads(candidate_json)
        result = governance_engine.validate_knowledge_conflict(candidate_data)
    except json.JSONDecodeError as e:
        return json.dumps({"status": "error", "message": f"Invalid JSON format: {e}"}, ensure_ascii=False)
    return json.dumps(result, ensure_ascii=False, indent=2)

# --- Lifecycle Tools (Side Task) ---

@mcp.tool()
@log_tool_call
def harvest_knowledge_candidates(doc_path: str) -> str:
    """
    [支线任务] 从澄清文档中收割知识候选。
    仅提取已确认且有答案的条目。
    """
    result = lifecycle_engine.harvest_knowledge_candidates(doc_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def promote_knowledge(candidate_json: str, target_kb_path: str) -> str:
    """
    [支线任务] 将知识候选晋升到永久知识库 (L1/L2)。
    
    Args:
        candidate_json: 候选知识的 JSON 字符串。
        target_kb_path: 目标知识库的目录路径。
    """
    try:
        candidate_data = json.loads(candidate_json)
        result = lifecycle_engine.promote_knowledge(candidate_data, target_kb_path)
    except json.JSONDecodeError as e:
        return json.dumps({"status": "error", "message": f"Invalid JSON format: {e}"}, ensure_ascii=False)
    return json.dumps(result, ensure_ascii=False, indent=2)

# Debug/Admin Tools (Kept for development but can be hidden from normal users if needed)
@mcp.tool()
@log_tool_call
def list_knowledge_bases(page: int = 1, page_size: int = 30) -> str:
    """
    [调试工具] 列出所有知识库 (Datasets)。
    """
    result = lifecycle_engine.list_knowledge_bases(page, page_size)
    return json.dumps(result, ensure_ascii=False, indent=2)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
@log_tool_call
def list_knowledge_base_files(dataset_id: str, page: int = 1, page_size: int = 30, keywords: str = "") -> str:
    """
    [知识浏览] 列出指定知识库中的文件。
    
    Args:
        dataset_id: 知识库 ID
        page: 页码 (默认 1)
        page_size: 每页数量 (默认 30)
        keywords: 搜索关键词 (可选)
    """
    result = lifecycle_engine.list_knowledge_base_files(dataset_id, page, page_size, keywords)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
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
    result = lifecycle_engine.retrieve_chunks(dataset_id, query, page, page_size, similarity_threshold)
    return json.dumps(result, ensure_ascii=False, indent=2)

from src.apps.rag_flow_mcp.tools.visualization import view_last_diff
from src.apps.rag_flow_mcp.tools.qa_tool import capture_test_case

# --- Visualization Tools ---

@mcp.tool()
@log_tool_call
def view_diff(file_path: str) -> str:
    """
    [体验优化] 打开 VS Code 对比视图。
    对比指定文件的当前内容与其最新的影子副本 (Shadow Copy)。
    
    Args:
        file_path: 原文件的绝对路径。
    """
    result = view_last_diff(file_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

# --- QA Tools ---

@mcp.tool()
@log_tool_call
def add_test_case(query: str, expected_keywords: list[str], expected_document: str = "") -> str:
    """
    [闭环优化] 捕获测试用例到黄金数据集。
    
    Args:
        query: 问题。
        expected_keywords: 预期答案中必须包含的关键词列表。
        expected_document: (可选) 预期来源文档。
    """
    result = capture_test_case(query, expected_keywords, expected_document)
    return json.dumps(result, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    mcp.run()
