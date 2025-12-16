import os
import re
import datetime
from typing import Dict, Any, List, Tuple
from .base import BaseEngine
from src.apps.rag_flow_mcp.core.rag_client import RAGClient
from src.apps.rag_flow_mcp.core.markdown_ast import MarkdownASTManager
from src.apps.rag_flow_mcp.core.shadow_file_manager import ShadowFileManager

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
            self.ast_manager = MarkdownASTManager()
            self.shadow_manager = ShadowFileManager()
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
                
                # Prompt Engineering: Ask LLM for specific section Header and Content
                prompt = (
                    f"你是一位技术文档撰写专家。"
                    f"请基于以下决策点更新文档。\n\n"
                    f"**决策点**:\n问题: {question}\n回答: {answer}\n\n"
                    f"**任务**:\n"
                    f"1. 识别文档中需要修改的一个具体章节标题（Header Text，不含 #）。\n"
                    f"2. 重写该章节下的内容以包含决策点。\n"
                    f"3. 严格按以下 JSON 格式返回:\n"
                    f"```json\n"
                    f"{{\n"
                    f"  \"target_header\": \"章节标题\",\n"
                    f"  \"new_content\": \"新内容(Markdown格式)...\"\n"
                    f"}}\n"
                    f"```\n"
                    f"如果无需修改，返回 `{{\"target_header\": null}}`。"
                )
                
                # Truncate content for context
                truncated_content = current_content[:8000] 
                
                response = self.rag_client.agentic_search(
                    global_ctx=truncated_content,
                    local_ctx="",
                    question=prompt
                )
                
                generated_text = response.get("answer", "")
                
                # Extract JSON
                try:
                    import json
                    match = re.search(r'```json\n(.*?)\n```', generated_text, re.DOTALL)
                    if match:
                        json_str = match.group(1)
                        result = json.loads(json_str)
                        target_header = result.get("target_header")
                        new_content = result.get("new_content")
                        
                        if target_header and new_content:
                            # Apply AST Replacement
                            current_content = self.ast_manager.replace_section(current_content, target_header, new_content)
                            changes_log.append(f"Updated section '{target_header}' for question: {question[:30]}...")
                            
                except Exception as parse_err:
                    self.logger.warning(f"Failed to parse LLM response for evolution: {parse_err}")
                    continue

            # 4. Save Shadow Copy
            if changes_log:
                # Add revision log
                revision_log = "\n\n## 修订记录 (Auto-generated)\n" + "\n".join([f"- {log}" for log in changes_log])
                current_content += revision_log
                
                shadow_path, diff_path = self.shadow_manager.generate_shadow_copy(scheme_doc_path, current_content)
                
                return {
                    "status": "success",
                    "shadow_path": shadow_path,
                    "diff_path": diff_path,
                    "changes": changes_log,
                    "message": "已生成进化后的影子副本，请 Review。"
                }
            else:
                return {"status": "success", "message": "未产生有效修改。", "changes": []}

        except Exception as e:
            self.logger.error(f"进化过程失败: {e}")
            return {"status": "error", "message": str(e)}

    def _parse_decisions(self, doc_path: str) -> List[Tuple[str, str]]:
        """
        解析评审问题记录，提取已决策的条目
        (Simplified implementation using Regex for MVP)
        """
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Match pattern: **问题**: ... **回答**: ...
        # This is a simple approximation. A robust parser would use AST or block splitting.
        decisions = []
        
        # Split by question blocks (assuming standard format)
        blocks = content.split("### 问题")
        for block in blocks[1:]:
            q_match = re.search(r'\*\*描述\*\*：(.*?)\n', block)
            a_match = re.search(r'\*\*回答\*\*：(.*?)\n', block)
            
            if q_match and a_match:
                q_text = q_match.group(1).strip()
                a_text = a_match.group(1).strip()
                
                # Filter out empty answers or placeholders
                if a_text and "待回答" not in a_text:
                    decisions.append((q_text, a_text))
                    
        return decisions
