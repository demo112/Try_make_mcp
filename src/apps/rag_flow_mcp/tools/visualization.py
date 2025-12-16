import os
import glob
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def view_last_diff(file_path: str) -> Dict[str, Any]:
    """
    Open VS Code Diff view comparing the original file with its latest shadow copy.
    
    Args:
        file_path: Absolute path to the original file.
    """
    if not os.path.exists(file_path):
        return {"status": "error", "message": f"File not found: {file_path}"}
        
    base, ext = os.path.splitext(file_path)
    # Pattern: original_ai_revision_TIMESTAMP.ext
    pattern = f"{base}_ai_revision_*{ext}"
    
    candidates = glob.glob(pattern)
    if not candidates:
        return {"status": "error", "message": f"No shadow copies found for: {file_path}"}
        
    # Sort by modification time, newest first
    candidates.sort(key=os.path.getmtime, reverse=True)
    latest_shadow = candidates[0]
    
    logger.info(f"Opening diff: {file_path} vs {latest_shadow}")
    
    try:
        # Use 'code --diff file1 file2'
        # Check if 'code' command is available
        subprocess.run(["code", "--diff", file_path, latest_shadow], shell=True, check=True)
        return {
            "status": "success", 
            "message": "VS Code Diff view opened.",
            "original": file_path,
            "shadow": latest_shadow
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to open VS Code: {e}")
        return {"status": "error", "message": "Failed to launch VS Code. Ensure 'code' is in PATH."}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"status": "error", "message": str(e)}
