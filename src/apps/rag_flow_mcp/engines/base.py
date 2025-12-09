from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from src.common import get_app_logger

logger = get_app_logger("rag_flow_mcp.engines")

class BaseEngine(ABC):
    """
    所有引擎的基类 (Base Class for All Engines)
    
    定义了核心组件的通用接口和日志记录能力。
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logger
        
    @abstractmethod
    def initialize(self) -> bool:
        """初始化引擎资源 (Initialize Engine Resources)"""
        pass
