import os
import sys
import json
from mcp.server.fastmcp import FastMCP
from src.common import get_app_logger

__version__ = "2.0.0"

# Ensure core modules can be imported
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    sys.path.append(sys._MEIPASS)
else:
    # Running in a normal Python environment
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
config = load_config()
logger = get_app_logger("rag_flow_mcp")
mcp = FastMCP("rag_flow_mcp")

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
def fill_clarification_suggestions(doc_path: str) -> str:
    """
    [主线任务] 填充澄清建议。
    读取评审问题记录文档，调用 RAG 检索知识库，并将带有置信度的建议填入文档。
    
    Args:
        doc_path: '04_评审问题记录.md' 的绝对路径。
    """
    result = inference_engine.fill_clarification_suggestions(doc_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
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
def check_metadata_compliance(doc_path: str) -> str:
    """
    [治理管控] 检查文档是否包含必要的元数据 (如 product, module 等)。
    """
    result = governance_engine.check_metadata_compliance(doc_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
def validate_knowledge_conflict(candidate_json: str) -> str:
    """
    [治理管控] 验证知识候选是否与现有知识库冲突。
    
    Args:
        candidate_json: 候选知识的 JSON 字符串。
    """
    try:
        candidate_data = json.loads(candidate_json)
        result = governance_engine.validate_knowledge_conflict(candidate_data)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "无效的 JSON 格式"}, ensure_ascii=False)

# --- Lifecycle Tools (Side Task) ---

@mcp.tool()
def harvest_knowledge_candidates(doc_path: str) -> str:
    """
    [支线任务] 从澄清文档中收割知识候选。
    仅提取已确认且有答案的条目。
    """
    candidates = lifecycle_engine.harvest_knowledge_candidates(doc_path)
    return json.dumps(candidates, ensure_ascii=False, indent=2)

@mcp.tool()
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
        return json.dumps(result, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "无效的 JSON 格式"}, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()
