"""
Common utilities for MCP Factory
"""
import logging
import sys
from .config import load_config

def get_app_logger(name: str) -> logging.Logger:
    """
    获取一个配置好的 Logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

__all__ = ['get_app_logger', 'load_config']
