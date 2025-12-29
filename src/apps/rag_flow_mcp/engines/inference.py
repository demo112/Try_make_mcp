import os
import re
import time
from typing import Dict, Any, List, Optional
from .base import BaseEngine
from src.apps.rag_flow_mcp.core.rag_client import RAGClient
# from src.apps.rag_flow_mcp.core.shadow_file_manager import ShadowFileManager # Removed

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
            # rag_client and query_rewriter are initialized in BaseEngine
            
            from src.apps.rag_flow_mcp.core.evaluator import QualityEvaluator
            # Use configured threshold
            self.threshold = self.config.get("RAG_CONFIDENCE_THRESHOLD", 0.6)
            self.evaluator = QualityEvaluator(threshold=self.threshold)
            # self.shadow_manager = ShadowFileManager() # Removed, using FileService
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
        
        if not self.file_service.exists(doc_path):
            return {"status": "error", "message": f"文件未找到: {doc_path}"}
            
        try:
            # 1. 读取内容 (Use FileService)
            content = self.file_service.read_text(doc_path)
            
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
                # 组合上下文 (Product + Module + Business Context)
                combined_context = f"{context_str}\n{q['business_context']}"
                
                # 构建完整的查询内容 (Full Question Content)
                # 使用整个问题块作为查询输入，确保上下文完整
                # 移除可能存在的旧 AI 回答，避免干扰
                clean_block = re.sub(r'\n\*\*AI 参考建议\*\*：.*?(?=\n\*\*回答\*\*|\Z)', '', q['full_block'], flags=re.DOTALL)
                
                # 执行安全检索 (含重试/降级)
                # 使用 QueryRewriter 优化查询
                optimized_query = self.query_rewriter.rewrite(clean_block, context=combined_context)
                
                result = self._safe_rag_search(
                    global_ctx="", 
                    local_ctx=combined_context,
                    question=optimized_query,  # Use optimized query
                    dataset_ids=self.config.get("RAG_DATASET_IDS", "")
                )
                
                # 真实性校验 (Still verify against the specific description if available, or the full block)
                # Using description for verification is usually better as it's the core question, 
                # but if description is empty, use title or block.
                verify_text = q["description"] if q["description"] else q["title"]
                is_valid, reason = self._verify_truthfulness(verify_text, result)
                
                if is_valid:
                    answers_map[str(q["id"])] = result
                    processed_count += 1
                else:
                    self.logger.info(f"跳过问题 {q['id']}，原因: {reason}")
                    # 即使置信度低，也尝试填充，但标注为低置信度
                    # answers_map[str(q["id"])] = result # 暂时保持跳过，后续可优化为降级显示

            
            # 5. 回写文档 (使用影子副本)
            if answers_map:
                new_content = self._inject_ai_answers(content, answers_map)
                
                # Use ShadowFileManager instead of direct write
                shadow_path, diff_path = self.shadow_manager.generate_shadow_copy(doc_path, new_content)
                
                return {
                    "status": "success", 
                    "processed_count": processed_count,
                    "shadow_path": shadow_path,
                    "diff_path": diff_path,
                    "message": "已生成影子副本，请 Review。"
                }
            
            return {"status": "success", "message": "无有效建议生成。", "processed_count": 0}

        except Exception as e:
            self.logger.error(f"处理澄清建议失败: {e}")
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
        if score < self.threshold:
            return False, f"置信度过低 ({score:.2f} < {self.threshold})"
            
        # 2. 拒绝回答检测
        eval_res = self.evaluator.evaluate(question, result)
        if not eval_res["is_valid"]:
            return False, eval_res["reason"]
            
        return True, "Pass"

    # --- Private Helper Methods (Ported from doc_processor.py) ---

    # _read_file is removed as we use FileService

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
        pattern = re.compile(r'(##\s+(\d+)\.(.+?)\n)(.*?)(?=\n##\s+\d+\.|\Z)', re.DOTALL)
        
        def replacement_func(match):
            header = match.group(1)
            idx = match.group(2)
            body = match.group(4)
            
            if idx in answers_map:
                ans_data = answers_map[idx]
                score_val = ans_data.get('score', 0.0)
                
                # Construct AI block
                ai_block = (
                    f"\n**AI 参考建议**：\n"
                    f"> 🤖 **AI 解答** (置信度: {score_val:.2f})\n"
                    f">\n"
                    f"> {ans_data['answer']}\n"
                    f">\n"
                    f"> 📚 **来源**:\n"
                    f"> - `{ans_data.get('citation', 'Unknown')}`\n"
                )
                
                # Check if AI block already exists and replace it
                # Match from **AI 参考建议** start until **回答** or end of block
                existing_ai_pattern = re.compile(r'\n\*\*AI 参考建议\*\*：.*?(?=\n\*\*回答\*\*|\Z)', re.DOTALL)
                
                if existing_ai_pattern.search(body):
                    # Replace existing AI block
                    new_body = existing_ai_pattern.sub(ai_block, body)
                else:
                    # Insert before **回答** if it exists, otherwise append
                    if "**回答**" in body:
                        parts = body.split("**回答**")
                        # parts[0] is content before answer, parts[1:] is answer content
                        # We inject AI block between them
                        new_body = parts[0] + ai_block + "\n**回答**" + "**回答**".join(parts[1:])
                    else:
                        new_body = body + ai_block
                
                return header + new_body
            else:
                return match.group(0) # No change
                
        new_content = pattern.sub(replacement_func, content)
        return new_content
