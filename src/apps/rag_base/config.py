import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def load_config():
    """Load configuration for rag_base."""
    
    # Load .env with priority:
    # 1. Directory of the executable (if frozen)
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        env_path = exe_dir / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)

    # 2. Current working directory / standard location
    # Try loading from src/apps/rag_base/.env explicitly if running from source
    current_dir = Path(__file__).parent
    env_path_local = current_dir / '.env'
    if env_path_local.exists():
        load_dotenv(dotenv_path=env_path_local)
        
    # 3. Default load (looks in CWD)
    load_dotenv()

    return {
        "RAGFLOW_API_KEY": os.getenv("RAGFLOW_API_KEY", ""),
        "RAGFLOW_HOST": os.getenv("RAGFLOW_HOST", "http://127.0.0.1:9380"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")
    }
