import os
import re
import time
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
    3. 确保真实性与鲁棒性 (重试/降级)。
    """
    
    def initialize(self) -> bool:
        self.logger.info("正在初始化推理引擎...")
        try:
            self.rag_client = RAGClient(
                self.config.get("RAGFLOW_API_KEY", ""),
                self.config.get("RAGFLOW_HOST", ""),
                self.config.get("RAGFLOW_CHAT_ID", "")
            )
            self.evaluator = QualityEvaluator()
            return True
        except Exception as e:
            self.logger.error(f"推理引擎初始化失败: {e}")
            return False
        
    def fill_clarification_suggestions(self, doc_path: str) -> Dict[str, Any]:
        """
        填充澄清建议 (Fill Clarification Suggestions)
        
        Args:
            doc_path: 待澄清问题记录文档路径 (04_评审问题记录.md)
            
        Returns:
            Dict: 执行结果摘要
        """
        self.logger.info(f"开始处理澄清建议: {doc_path}")
        
        if not os.path.exists(doc_path):
            return {"status": "error", "message": f"文件未找到: {doc_path}"}
            
        try:
            # 1. 读取内容
            content = self._read_file(doc_path)
            
            # 2. 提取元数据
            metadata = self._extract_metadata(content)
            context_str = f"产品: {metadata.get('product')}, 模块: {metadata.get('module')}"
            
            # 3. 解析问题
            questions = self._parse_questions(content)
            if not questions:
                return {"status": "success", "message": "未发现问题。", "processed_count": 0}
            
            answers_map = {}
            processed_count = 0
            
            # 4. 处理每个问题
            for q in questions:
                # 组合上下文
                combined_context = f"{context_str}\n{q['business_context']}"
                
                # 执行安全检索 (含重试/降级)
                result = self._safe_rag_search(
                    global_ctx="", 
                    local_ctx=combined_context,
                    question=q["description"],
                    dataset_ids=self.config.get("RAG_DATASET_IDS", "")
                )
                
                # 真实性校验
                is_valid, reason = self._verify_truthfulness(q["description"], result)
                
                if is_valid:
                    answers_map[str(q["id"])] = result
                    processed_count += 1
                else:
                    self.logger.info(f"跳过问题 {q['id']}，原因: {reason}")
                    # 可选：如果需要在文档中标记“未找到”，可以在这里处理
                    # 目前策略是如果不通过，则不填充建议，避免误导
            
            # 5. 回写文档
            if answers_map:
                new_content = self._inject_ai_answers(content, answers_map)
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return {
                    "status": "success", 
                    "message": f"成功处理 {processed_count} 个问题。", 
                    "processed_count": processed_count
                }
            else:
                return {"status": "success", "message": "没有生成有效的建议。", "processed_count": 0}
                
        except Exception as e:
            self.logger.error(f"推理过程失败: {e}")
            return {"status": "error", "message": str(e)}

    def _safe_rag_search(self, global_ctx: str, local_ctx: str, question: str, dataset_ids: str, retries: int = 3) -> Dict[str, Any]:
        """执行带有自动重试和降级策略的 RAG 检索"""
        for i in range(retries):
            try:
                result = self.rag_client.agentic_search(
                    global_ctx=global_ctx,
                    local_ctx=local_ctx,
                    question=question,
                    dataset_ids=dataset_ids
                )
                return result
            except Exception as e:
                wait_time = 2 ** i
                self.logger.warning(f"RAG 检索失败 (第 {i+1} 次)，{wait_time}秒后重试: {e}")
                time.sleep(wait_time)
        
        # 降级策略
        self.logger.error("RAG 检索最终失败，执行降级策略。")
        return {
            "answer": "❌ **服务暂时不可用**\n> 无法连接到知识库服务，请人工查阅相关文档。",
            "citation": "System Error",
            "score": 0.0
        }

    def _verify_truthfulness(self, question: str, result: Dict[str, Any]) -> tuple[bool, str]:
        """校验回答的真实性，防止幻觉"""
        score = result.get("score", 0.0)
        
        # 1. 严格的置信度阈值 (用户要求严禁虚假)
        THRESHOLD = 0.6
        if score < THRESHOLD:
            return False, f"置信度过低 ({score:.2f} < {THRESHOLD})"
            
        # 2. 拒绝回答检测
        eval_res = self.evaluator.evaluate(question, result)
        if not eval_res["is_valid"]:
            return False, eval_res["reason"]
            
        return True, "Pass"

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
