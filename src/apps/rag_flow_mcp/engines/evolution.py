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
        self.logger.info("正在初始化进化引擎...")
        try:
            self.rag_client = RAGClient(
                self.config.get("RAGFLOW_API_KEY", ""),
                self.config.get("RAGFLOW_HOST", ""),
                self.config.get("RAGFLOW_CHAT_ID", "")
            )
            return True
        except Exception as e:
            self.logger.error(f"进化引擎初始化失败: {e}")
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
        self.logger.info(f"正在基于 {clarification_doc_path} 进化方案 {scheme_doc_path}")
        
        if not os.path.exists(scheme_doc_path) or not os.path.exists(clarification_doc_path):
            return {"status": "error", "message": "文件未找到"}
            
        try:
            # 1. 解析决策
            decisions = self._parse_decisions(clarification_doc_path)
            if not decisions:
                return {"status": "success", "message": "未发现需要进化的决策点。", "changes": []}
            
            # 2. 读取方案文档
            with open(scheme_doc_path, 'r', encoding='utf-8') as f:
                scheme_content = f.read()
            
            changes_log = []
            current_content = scheme_content
            
            # 3. 应用进化
            for idx, (question, answer) in enumerate(decisions):
                self.logger.info(f"正在处理决策 {idx+1}/{len(decisions)}...")
                
                # Use LLM to identify and rewrite the section
                # Prompt Engineering:
                prompt = (
                    f"你是一位技术文档撰写专家。"
                    f"我有一份软件设计文档和一个评审澄清决策。\n"
                    f"请基于决策内容重写文档的相关章节。\n\n"
                    f"**决策点**:\n问题: {question}\n回答: {answer}\n\n"
                    f"**任务**:\n"
                    f"1. 识别文档中最相关的章节。\n"
                    f"2. 重写该章节以包含决策内容。\n"
                    f"3. 仅返回新的章节内容，使用 ```markdown ... ``` 包裹。\n"
                    f"如果文档已经包含该内容或无需修改，请回复 'NO_CHANGE'。"
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
                    
                    # Alternative Strategy: Append to a "## Version 1.1 Updates" section
                    changes_log.append(f"- 已整合决策: {question[:50]}...")
                    
                    # For now, let's just append to the end as a proof of concept
                    current_content += f"\n\n## 进化更新 (基于 Q{idx+1})\n{new_section}\n"
            
            # 4. 保存 v1.1
            new_path = scheme_doc_path.replace("v1.0", "v1.1")
            if new_path == scheme_doc_path:
                new_path = scheme_doc_path.replace(".md", "_v1.1.md")
                
            # Add Revision Log
            revision_log = "\n\n---\n**修订日志 (自动进化)**:\n" + "\n".join(changes_log)
            final_content = current_content + revision_log
            
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
                
            return {
                "status": "success", 
                "new_path": new_path, 
                "changes_count": len(changes_log)
            }
            
        except Exception as e:
            self.logger.error(f"方案进化失败: {e}")
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
