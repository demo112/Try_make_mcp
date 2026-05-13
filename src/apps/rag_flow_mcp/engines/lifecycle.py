import os
import re
import json
import datetime
from typing import Dict, Any, List
from .base import BaseEngine

class LifecycleEngine(BaseEngine):
    """
    生命周期引擎 (Lifecycle Engine)
    
    职责:
    1. 收割新知识候选 (Harvest Candidates)。
    2. 晋升知识到 L1/L2 库 (Promote Knowledge)。
    """
    
    def initialize(self) -> bool:
        self.logger.info("正在初始化生命周期引擎...")
        try:
            from src.apps.rag_flow_mcp.core.rag_client import RAGClient
            self.rag_client = RAGClient(
                self.config.get("RAGFLOW_API_KEY", ""),
                self.config.get("RAGFLOW_HOST", ""),
                self.config.get("RAGFLOW_CHAT_ID", ""),
                timeout=self.config.get("RAGFLOW_TIMEOUT", 120),
                top_k=self.config.get("RAGFLOW_TOP_K", 10),
                similarity_threshold=self.config.get("RAGFLOW_SIMILARITY_THRESHOLD", 0.2)
            )
            return True
        except Exception as e:
            self.logger.error(f"生命周期引擎初始化失败: {e}")
            return False

    def list_knowledge_bases(self, page: int = 1, page_size: int = 30) -> Dict[str, Any]:
        """
        列出所有知识库 (List Knowledge Bases)
        """
        self.logger.info(f"正在查询知识库列表 (Page: {page})")
        return self.rag_client.list_datasets(page, page_size)

    def list_knowledge_base_files(self, dataset_id: str, page: int = 1, page_size: int = 30, keywords: str = "") -> Dict[str, Any]:
        """
        列出指定知识库的文件 (List Knowledge Base Files)
        """
        self.logger.info(f"正在查询知识库文件 (Dataset: {dataset_id}, Keywords: {keywords})")
        return self.rag_client.list_documents(dataset_id, page, page_size, keywords)
        
    def retrieve_chunks(self, dataset_id: str, query: str, page: int = 1, page_size: int = 30, similarity_threshold: float = 0.2) -> Dict[str, Any]:
        """
        检索知识库切片 (Retrieve Chunks)
        """
        # Optimize query before retrieval
        optimized_query = self.query_rewriter.rewrite(query)
        self.logger.info(f"正在检索知识切片 (Dataset: {dataset_id}, Query: {optimized_query})")
        return self.rag_client.retrieve_chunks(dataset_id, optimized_query, page, page_size, similarity_threshold)

    def harvest_knowledge_candidates(self, doc_path: str) -> List[Dict[str, Any]]:
        """
        收割知识候选 (Harvest Knowledge Candidates)
        
        Extracts Q&A pairs that have been answered in the clarification doc.
        """
        self.logger.info(f"正在从文档收割知识: {doc_path}")
        
        if not os.path.exists(doc_path):
            self.logger.error(f"文件未找到: {doc_path}")
            return []
            
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract Metadata first
        metadata = self._extract_metadata(content)
        
        candidates = []
        # Regex to match blocks
        pattern = re.compile(r'(##\s+(\d+)\.(.+?)\n)(.*?)(?=\n##\s+\d+\.|\Z)', re.DOTALL)
        matches = pattern.findall(content)
        
        for _, idx, title, body in matches:
            # Extract Question Description
            q_match = re.search(r'\*\*问题描述\*\*：(.*?)\n\*\*', body, re.DOTALL)
            question = q_match.group(1).strip() if q_match else ""
            
            # Extract Answer (Human or Final Decision)
            a_match = re.search(r'\*\*回答\*\*：(.*?)(?=\n\*\*|\Z)', body, re.DOTALL)
            answer = a_match.group(1).strip() if a_match else ""
            
            if question and answer and len(answer) > 5:
                candidate = {
                    "id": f"{metadata.get('product', 'unknown')}_{metadata.get('module', 'unknown')}_{idx}",
                    "question": question,
                    "answer": answer,
                    "source_doc": doc_path,
                    "metadata": metadata,
                    "harvested_at": datetime.datetime.now().isoformat(),
                    "status": "candidate"
                }
                candidates.append(candidate)
                
        return candidates
        
    def promote_knowledge(self, candidate_data: Dict[str, Any], target_kb_path: str) -> Dict[str, Any]:
        """
        晋升知识 (Promote Knowledge)
        
        Saves the candidate as a JSON or MD file in the target Knowledge Base.
        """
        candidate_id = candidate_data.get("id", "unknown")
        self.logger.info(f"正在晋升候选知识 {candidate_id} 到 {target_kb_path}")
        
        self.file_service.ensure_dir(target_kb_path)
        
        # Save as JSON for machine readability
        file_name = f"knowledge_{candidate_id}.json"
        full_path = os.path.join(target_kb_path, file_name)
        
        try:
            candidate_data["status"] = "promoted"
            candidate_data["promoted_at"] = datetime.datetime.now().isoformat()
            
            self.file_service.write_json(full_path, candidate_data)
                
            return {
                "status": "success",
                "path": full_path
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _extract_metadata(self, content: str) -> Dict[str, str]:
        metadata = {"product": "General", "module": "General"}
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            yaml_block = match.group(1)
            for line in yaml_block.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    metadata[key.strip().lower()] = val.strip()
        return metadata
