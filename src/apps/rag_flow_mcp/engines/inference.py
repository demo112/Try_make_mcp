import os
import re
from typing import Dict, Any, List, Optional
from .base import BaseEngine
from src.apps.rag_flow_mcp.core.rag_client import RAGClient
from src.apps.rag_flow_mcp.core.evaluator import QualityEvaluator

class InferenceEngine(BaseEngine):
    """
    推理引擎 (Inference Engine)
    
    职责:
    1. 负责澄清问题的智能回答 (RAG 检索)。
    2. 生成含建议的澄清文档。
    """
    
    def initialize(self) -> bool:
        self.logger.info("Initializing Inference Engine...")
        try:
            self.rag_client = RAGClient(
                self.config.get("RAGFLOW_API_KEY", ""),
                self.config.get("RAGFLOW_HOST", ""),
                self.config.get("RAGFLOW_CHAT_ID", "")
            )
            self.evaluator = QualityEvaluator()
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Inference Engine: {e}")
            return False
        
    def fill_clarification_suggestions(self, doc_path: str) -> Dict[str, Any]:
        """
        填充澄清建议 (Fill Clarification Suggestions)
        
        Args:
            doc_path: 待澄清问题记录文档路径 (04_评审问题记录.md)
            
        Returns:
            Dict: 执行结果摘要
        """
        self.logger.info(f"Starting clarification inference for: {doc_path}")
        
        if not os.path.exists(doc_path):
            return {"status": "error", "message": f"File not found: {doc_path}"}
            
        try:
            # 1. Read Content
            content = self._read_file(doc_path)
            
            # 2. Extract Metadata
            metadata = self._extract_metadata(content)
            context_str = f"Product: {metadata.get('product')}, Module: {metadata.get('module')}"
            
            # 3. Parse Questions
            questions = self._parse_questions(content)
            if not questions:
                return {"status": "success", "message": "No questions found.", "processed_count": 0}
            
            answers_map = {}
            processed_count = 0
            
            # 4. Process Each Question
            for q in questions:
                # Combine context
                combined_context = f"{context_str}\n{q['business_context']}"
                
                # Perform Search
                result = self.rag_client.agentic_search(
                    global_ctx="", # In a real scenario, we might load global context separately
                    local_ctx=combined_context,
                    question=q["description"],
                    dataset_ids=self.config.get("RAG_DATASET_IDS", "")
                )
                
                # Evaluate
                eval_res = self.evaluator.evaluate(q["description"], result)
                
                if eval_res["is_valid"]:
                    answers_map[str(q["id"])] = result
                    processed_count += 1
                else:
                    self.logger.info(f"Skipped question {q['id']} due to low quality: {eval_res['reason']}")
            
            # 5. Write Back
            if answers_map:
                new_content = self._inject_ai_answers(content, answers_map)
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return {
                    "status": "success", 
                    "message": f"Processed {processed_count} questions.", 
                    "processed_count": processed_count
                }
            else:
                return {"status": "success", "message": "No valid answers generated.", "processed_count": 0}
                
        except Exception as e:
            self.logger.error(f"Inference failed: {e}")
            return {"status": "error", "message": str(e)}

    # --- Private Helper Methods (Ported from doc_processor.py) ---

    def _read_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

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

    def _parse_questions(self, content: str) -> List[Dict]:
        questions = []
        # Regex to match ## [index].[title] blocks
        pattern = re.compile(r'(##\s+(\d+)\.(.+?)\n)(.*?)(?=\n##\s+\d+\.|\Z)', re.DOTALL)
        matches = pattern.findall(content)
        
        for header, idx, title, body in matches:
            q_data = {
                "id": idx,
                "title": title.strip(),
                "full_block": header + body
            }
            desc_match = re.search(r'\*\*问题描述\*\*：(.*?)\n\*\*', body, re.DOTALL)
            ctx_match = re.search(r'\*\*业务上下文\*\*：(.*?)\n\*\*', body, re.DOTALL)
            
            q_data["description"] = desc_match.group(1).strip() if desc_match else ""
            q_data["business_context"] = ctx_match.group(1).strip() if ctx_match else ""
            questions.append(q_data)
        return questions

    def _inject_ai_answers(self, content: str, answers_map: Dict[str, Dict]) -> str:
        # Simple replacement strategy (naive but functional for now)
        # We need to be careful not to double-inject if run multiple times.
        # Ideally, we should check if an answer block already exists.
        
        # Strategy: Re-parse and reconstruct to be safe, or just insert if missing.
        # For this version, I'll use a split/join approach based on the blocks logic
        
        # Better approach: Iterate over matches again and replace the body
        
        pattern = re.compile(r'(##\s+(\d+)\.(.+?)\n)(.*?)(?=\n##\s+\d+\.|\Z)', re.DOTALL)
        
        def replacement_func(match):
            header = match.group(1)
            idx = match.group(2)
            # title = match.group(3)
            body = match.group(4)
            
            if idx in answers_map:
                ans_data = answers_map[idx]
                score_str = f"{ans_data.get('score', 0.0) * 100:.0f}%"
                
                # Check if AI block already exists to avoid duplication
                if "**AI 参考建议**" in body:
                    # Remove existing AI block or skip? 
                    # Let's replace the existing AI block if possible, or just append if complex.
                    # For simplicity, if it exists, we skip injection to avoid duplicates
                    # Or we could strip it.
                    pass # TODO: Enhanced replacement logic
                
                # Construct AI block
                ai_block = (
                    f"\n**AI 参考建议**：\n"
                    f"> 🤖 **RAG自动回复** (置信度: {score_str})\n"
                    f"> {ans_data['answer']}\n"
                    f">\n"
                    f"> *来源: {ans_data.get('citation', 'Unknown')}*\n"
                )
                
                # Insert before **回答** (Decision) if it exists, otherwise append
                if "**回答**" in body:
                    parts = body.split("**回答**")
                    new_body = parts[0] + ai_block + "\n**回答**" + "".join(parts[1:])
                else:
                    new_body = body + ai_block
                
                return header + new_body
            else:
                return match.group(0) # No change
                
        new_content = pattern.sub(replacement_func, content)
        return new_content
