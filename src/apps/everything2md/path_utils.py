import os
import logging

logger = logging.getLogger(__name__)

def map_path_to_container(path: str) -> str:
    r"""
    Maps a host path to a container path based on environment variables.
    
    Env Vars:
        HOST_ROOT: The root directory on the host (default: C:\)
        CONTAINER_ROOT: The root directory mapped in the container (default: /mnt/c/)
        
    Example:
        HOST_ROOT="C:\"
        CONTAINER_ROOT="/mnt/c/"
        Input: "C:\Users\Test\file.docx"
        Output: "/mnt/c/Users/Test/file.docx"
    """
    # Only perform mapping if we are running in a container context
    # We can infer this if CONTAINER_ROOT is set explicitly, or just try mapping always
    # if the path matches HOST_ROOT.
    
    host_root = os.environ.get("HOST_ROOT")
    container_root = os.environ.get("CONTAINER_ROOT")
    
    if not host_root or not container_root:
        # Mapping not configured, return original path
        return path
        
    # Normalize slashes for comparison
    # Windows paths are case-insensitive usually, but Python string ops are sensitive
    # We'll try to be robust
    
    norm_path = path.replace("\\", "/")
    norm_host_root = host_root.replace("\\", "/")
    
    # Ensure host root ends with slash for clean replacement, unless it's just "C:"
    if not norm_host_root.endswith("/") and not norm_path.startswith(norm_host_root + "/"):
         # If host root is "C:" and path is "C:/Users", it works
         pass
    elif not norm_host_root.endswith("/"):
         norm_host_root += "/"

    if norm_path.lower().startswith(norm_host_root.lower()):
        # Extract relative part
        # We use the length of the configured root to slice
        # Note: We use the *original* path casing for the relative part to preserve it,
        # but we matched using lowercase.
        
        # Find the index where the root ends (case insensitive match)
        start_idx = len(norm_host_root)
        
        # Handle edge case where norm_host_root might not have trailing slash in config but path has it
        # e.g. ROOT=C: PATH=C:/Users
        if norm_path[start_idx-1] != '/' and norm_path[start_idx] == '/':
            start_idx += 1
            
        rel_path = norm_path[start_idx:]
        
        # Construct container path
        # Ensure container root ends with slash
        if not container_root.endswith("/") and not container_root.endswith("\\"):
            container_root += "/"
            
        mapped_path = os.path.join(container_root, rel_path).replace("\\", "/")
        logger.debug(f"Mapped path: {path} -> {mapped_path}")
        return mapped_path
        
    return path
