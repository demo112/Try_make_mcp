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
        self.logger.info("Initializing Lifecycle Engine...")
        return True
        
    def harvest_knowledge_candidates(self, doc_path: str) -> List[Dict[str, Any]]:
        """
        收割知识候选 (Harvest Knowledge Candidates)
        
        Extracts Q&A pairs that have been answered in the clarification doc.
        """
        self.logger.info(f"Harvesting knowledge from {doc_path}")
        
        if not os.path.exists(doc_path):
            self.logger.error(f"File not found: {doc_path}")
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
        self.logger.info(f"Promoting candidate {candidate_id} to {target_kb_path}")
        
        if not os.path.exists(target_kb_path):
            try:
                os.makedirs(target_kb_path)
            except Exception as e:
                return {"status": "error", "message": f"Failed to create KB dir: {e}"}
        
        # Save as JSON for machine readability
        file_name = f"knowledge_{candidate_id}.json"
        full_path = os.path.join(target_kb_path, file_name)
        
        try:
            candidate_data["status"] = "promoted"
            candidate_data["promoted_at"] = datetime.datetime.now().isoformat()
            
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(candidate_data, f, ensure_ascii=False, indent=2)
                
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
