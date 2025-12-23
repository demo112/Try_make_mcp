import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from src.apps.rag_flow_mcp.core.file_service import FileService
from src.apps.rag_flow_mcp.core.rag_client import RAGClient
from src.apps.rag_flow_mcp.core.query_rewriter import QueryRewriter

class BaseEngine(ABC):
    """
    Base class for all business engines.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"rag_flow_mcp.engines.{self.__class__.__name__}")
        self.file_service = FileService()
        
        # Initialize RAGClient here to be shared
        self.rag_client = RAGClient(
            self.config.get("RAGFLOW_API_KEY", ""),
            self.config.get("RAGFLOW_HOST", ""),
            self.config.get("RAGFLOW_CHAT_ID", ""),
            timeout=self.config.get("RAGFLOW_TIMEOUT", 120),
            top_k=self.config.get("RAGFLOW_TOP_K", 10),
            similarity_threshold=self.config.get("RAGFLOW_SIMILARITY_THRESHOLD", 0.2)
        )
        self.query_rewriter = QueryRewriter(self.rag_client)
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize engine resources."""
        pass
