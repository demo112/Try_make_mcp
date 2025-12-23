import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from src.common import load_config as load_common_config

# Load .env with priority:
# 1. Directory of the executable (if frozen/compiled)
if getattr(sys, 'frozen', False):
    exe_dir = Path(sys.executable).parent
    env_path = exe_dir / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

# 2. Current working directory (standard behavior)
load_dotenv()

# 3. Directory of this config file (useful for dev/source mode)
config_dir = Path(__file__).parent
env_path_local = config_dir / '.env'
if env_path_local.exists():
    load_dotenv(dotenv_path=env_path_local)

def load_config():
    """Load configuration for rag_flow_mcp."""
    common_conf = load_common_config()
    
    return {
        "RAGFLOW_API_KEY": os.getenv("RAGFLOW_API_KEY", "mock_key"),
        "RAGFLOW_HOST": os.getenv("RAGFLOW_HOST", "http://localhost:9380"),
        "RAGFLOW_CHAT_ID": os.getenv("RAGFLOW_CHAT_ID", ""),
        "RAG_DATASET_IDS": os.getenv("RAG_DATASET_IDS", ""),  # Comma separated
        "RAGFLOW_TIMEOUT": int(os.getenv("RAGFLOW_TIMEOUT", "120")),
        "RAGFLOW_TOP_K": int(os.getenv("RAGFLOW_TOP_K", "10")),
        "RAGFLOW_SIMILARITY_THRESHOLD": float(os.getenv("RAGFLOW_SIMILARITY_THRESHOLD", "0.2")),
        "RAG_CONFIDENCE_THRESHOLD": float(os.getenv("RAG_CONFIDENCE_THRESHOLD", "0.6")),
        "LOG_LEVEL": common_conf.get("log_level", "INFO")
    }
