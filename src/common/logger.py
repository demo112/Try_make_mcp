import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def get_app_logger(app_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger for the application.
    Logs to both stderr (for dev) and a file (for prod/audit).
    Note: MCP uses stdout for communication, so NEVER log to stdout!
    """
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)
    
    if logger.handlers:
        return logger

    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
    )

    # 1. File Handler (Rotating)
    # Ensure logs directory exists
    # Assuming we are in src/common, go up to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "mcp_server.log")
    
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. Stderr Handler (Safe for MCP)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    logger.info(f"Logger initialized. Log file: {log_file}")
    return logger
