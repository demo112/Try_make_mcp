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
    [Main Task] Fill clarification suggestions into the review document.
    Reads questions, queries RAG, and injects answers with confidence scores.
    
    Args:
        doc_path: Absolute path to '04_评审问题记录.md'
    """
    result = inference_engine.fill_clarification_suggestions(doc_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
def evolve_scheme_document(scheme_doc_path: str, clarification_doc_path: str) -> str:
    """
    [Main Task] Evolve the scheme document based on clarified decisions.
    Applies changes to the scheme document and generates v1.1.
    
    Args:
        scheme_doc_path: Path to the original scheme document (v1.0)
        clarification_doc_path: Path to the clarified questions doc
    """
    result = evolution_engine.evolve_scheme_document(scheme_doc_path, clarification_doc_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

# --- Governance Tools ---

@mcp.tool()
def check_metadata_compliance(doc_path: str) -> str:
    """
    [Governance] Check if the document has required metadata (product, module, etc.).
    """
    result = governance_engine.check_metadata_compliance(doc_path)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
def validate_knowledge_conflict(candidate_json: str) -> str:
    """
    [Governance] Validate if a knowledge candidate conflicts with existing knowledge.
    
    Args:
        candidate_json: JSON string representing the candidate
    """
    try:
        candidate_data = json.loads(candidate_json)
        result = governance_engine.validate_knowledge_conflict(candidate_data)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "Invalid JSON"}, ensure_ascii=False)

# --- Lifecycle Tools (Side Task) ---

@mcp.tool()
def harvest_knowledge_candidates(doc_path: str) -> str:
    """
    [Side Task] Harvest knowledge candidates from a clarification document.
    Returns a list of candidates found.
    """
    candidates = lifecycle_engine.harvest_knowledge_candidates(doc_path)
    return json.dumps(candidates, ensure_ascii=False, indent=2)

@mcp.tool()
def promote_knowledge(candidate_json: str, target_kb_path: str) -> str:
    """
    [Side Task] Promote a candidate to the permanent knowledge base.
    
    Args:
        candidate_json: JSON string of the candidate
        target_kb_path: Directory path for the knowledge base (L1/L2)
    """
    try:
        candidate_data = json.loads(candidate_json)
        result = lifecycle_engine.promote_knowledge(candidate_data, target_kb_path)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "Invalid JSON"}, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()
