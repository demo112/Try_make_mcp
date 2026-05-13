"""
Common utilities for MCP Factory
"""
import logging
import sys
import os
from pathlib import Path
from .config import load_config

def get_app_logger(name: str) -> logging.Logger:
    """
    获取一个配置好的 Logger。
    支持输出到 stderr 和 logs/app.log 文件。
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
        )

        # 1. Stream Handler (Stderr)
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # 2. File Handler
        try:
            # Determine log directory
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path.cwd()
            
            log_dir = base_dir / "logs"
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / "mcp_server.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            # Log initialization info
            logger.info(f"Logger initialized. Log file: {log_file}")
            
        except Exception as e:
            sys.stderr.write(f"Failed to setup file logging: {e}\n")

    return logger

__all__ = ['get_app_logger', 'load_config']
