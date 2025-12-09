import os
import re
import datetime
from typing import Dict, Any, List, Tuple
from .base import BaseEngine
from src.apps.rag_flow_mcp.core.rag_client import RAGClient

class EvolutionEngine(BaseEngine):
    """
    进化引擎 (Evolution Engine)
    
    职责:
    1. 基于澄清结果，自动迭代方案文档。
    2. 维护文档版本和修订日志。
    """
    
    def initialize(self) -> bool:
        self.logger.info("Initializing Evolution Engine...")
        try:
            self.rag_client = RAGClient(
                self.config.get("RAGFLOW_API_KEY", ""),
                self.config.get("RAGFLOW_HOST", ""),
                self.config.get("RAGFLOW_CHAT_ID", "")
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Evolution Engine: {e}")
            return False
        
    def evolve_scheme_document(self, scheme_doc_path: str, clarification_doc_path: str) -> Dict[str, Any]:
        """
        进化方案文档 (Evolve Scheme Document)
        
        Args:
            scheme_doc_path: 原方案文档路径 (v1.0)
            clarification_doc_path: 已决策的澄清文档路径 (04_评审问题记录.md)
            
        Returns:
            Dict: 进化结果 (新文档路径, 修改点摘要)
        """
        self.logger.info(f"Evolving scheme {scheme_doc_path} using {clarification_doc_path}")
        
        if not os.path.exists(scheme_doc_path) or not os.path.exists(clarification_doc_path):
            return {"status": "error", "message": "File not found"}
            
        try:
            # 1. Parse Decisions from Clarification Doc
            decisions = self._parse_decisions(clarification_doc_path)
            if not decisions:
                return {"status": "success", "message": "No decisions found to evolve.", "changes": []}
            
            # 2. Read Scheme Doc
            with open(scheme_doc_path, 'r', encoding='utf-8') as f:
                scheme_content = f.read()
            
            changes_log = []
            current_content = scheme_content
            
            # 3. Apply Evolutions
            for idx, (question, answer) in enumerate(decisions):
                self.logger.info(f"Processing decision {idx+1}/{len(decisions)}...")
                
                # Use LLM to identify and rewrite the section
                # We treat the RAGClient as a general LLM interface here
                # Prompt Engineering:
                prompt = (
                    f"You are a technical writer. "
                    f"I have a software design document and a clarification decision.\n"
                    f"Please rewrite the relevant section of the document to incorporate the decision.\n\n"
                    f"**Decision**:\nQuestion: {question}\nAnswer: {answer}\n\n"
                    f"**Task**:\n"
                    f"1. Identify the most relevant section in the document.\n"
                    f"2. Rewrite that section to reflect the answer.\n"
                    f"3. Return ONLY the new section content, wrapped in ```markdown ... ```.\n"
                    f"If the document already covers it or no change is needed, reply 'NO_CHANGE'."
                )
                
                # Note: sending the whole doc might exceed context window. 
                # In a robust implementation, we would chunk or use RAG to find the section first.
                # For this MVP, we assume the doc fits or we truncate.
                truncated_content = current_content[:10000] # Simple truncation safety
                
                response = self.rag_client.agentic_search(
                    global_ctx=truncated_content,
                    local_ctx="",
                    question=prompt
                )
                
                generated_text = response.get("answer", "")
                
                if "NO_CHANGE" in generated_text or not generated_text:
                    continue
                    
                # Extract markdown block
                match = re.search(r'```markdown\n(.*?)\n```', generated_text, re.DOTALL)
                if match:
                    new_section = match.group(1)
                    # Ideally we need to know WHICH section to replace.
                    # This is the tricky part of "Evolution".
                    # For MVP, we might just append a "Clarifications" section or use a placeholder.
                    # Or we ask LLM to return "Original Text" and "New Text" for search-replace.
                    
                    # Let's try the Append Strategy for safety in this version, 
                    # or better: Ask LLM for a diff.
                    
                    # Alternative Strategy: Append to a "## Version 1.1 Updates" section
                    changes_log.append(f"- Incorporated decision for: {question[:50]}...")
                    
                    # For now, let's just append to the end as a proof of concept
                    current_content += f"\n\n## 进化更新 (Based on Q{idx+1})\n{new_section}\n"
            
            # 4. Save v1.1
            new_path = scheme_doc_path.replace("v1.0", "v1.1")
            if new_path == scheme_doc_path:
                new_path = scheme_doc_path.replace(".md", "_v1.1.md")
                
            # Add Revision Log
            revision_log = "\n\n---\n**Revision Log (Auto-Evolved)**:\n" + "\n".join(changes_log)
            final_content = current_content + revision_log
            
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
                
            return {
                "status": "success", 
                "new_path": new_path, 
                "changes_count": len(changes_log)
            }
            
        except Exception as e:
            self.logger.error(f"Evolution failed: {e}")
            return {"status": "error", "message": str(e)}

    def _parse_decisions(self, file_path: str) -> List[Tuple[str, str]]:
        """
        Parse (Question, Answer) tuples from the clarification doc.
        Only returns items where an Answer exists.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        decisions = []
        # Regex to match blocks
        pattern = re.compile(r'(##\s+(\d+)\.(.+?)\n)(.*?)(?=\n##\s+\d+\.|\Z)', re.DOTALL)
        matches = pattern.findall(content)
        
        for _, _, _, body in matches:
            # Extract Question Description
            q_match = re.search(r'\*\*问题描述\*\*：(.*?)\n\*\*', body, re.DOTALL)
            question = q_match.group(1).strip() if q_match else ""
            
            # Extract Answer (Human or Final Decision)
            # We look for **回答**：...
            a_match = re.search(r'\*\*回答\*\*：(.*?)(?=\n\*\*|\Z)', body, re.DOTALL)
            answer = a_match.group(1).strip() if a_match else ""
            
            if question and answer and len(answer) > 5: # Basic valid check
                decisions.append((question, answer))
                
        return decisions
