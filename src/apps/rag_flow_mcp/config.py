import os
from dotenv import load_dotenv
from src.common import load_config as load_common_config

# Explicitly load .env
load_dotenv()

def load_config():
    """Load configuration for rag_flow_mcp."""
    common_conf = load_common_config()
    
    return {
        "RAGFLOW_API_KEY": os.getenv("RAGFLOW_API_KEY", "mock_key"),
        "RAGFLOW_HOST": os.getenv("RAGFLOW_HOST", "http://localhost:9380"),
        "RAGFLOW_CHAT_ID": os.getenv("RAGFLOW_CHAT_ID", ""),
        "RAG_DATASET_IDS": os.getenv("RAG_DATASET_IDS", ""),  # Comma separated
        "LOG_LEVEL": common_conf.get("log_level", "INFO")
    }
