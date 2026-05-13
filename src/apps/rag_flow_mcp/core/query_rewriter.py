import logging
from typing import Optional
from src.apps.rag_flow_mcp.core.rag_client import RAGClient

logger = logging.getLogger(__name__)

class QueryRewriter:
    """
    查询改写服务 (Query Rewriter)
    
    职责: 将用户的自然语言查询或任务描述，改写为更适合 RAG 检索的关键词或问题。
    """
    
    def __init__(self, rag_client: RAGClient):
        self.rag_client = rag_client
        
    def rewrite(self, query: str, context: str = "") -> str:
        """
        执行查询改写。
        
        Args:
            query: 原始查询或任务描述。
            context: 可选的上下文信息。
            
        Returns:
            str: 改写后的查询字符串。
        """
        # 如果没有配置 Chat ID，无法调用 LLM，直接返回原查询
        if not self.rag_client.chat_id:
            logger.warning("RAGFLOW_CHAT_ID 未配置，跳过查询改写，使用原始查询。")
            return query
            
        try:
            system_prompt = (
                "你是一个专业的搜索引擎查询优化专家。\n"
                "你的任务是将用户的输入（可能包含模糊描述、上下文或长文本）改写为精简、准确的搜索关键词或短语，以便在知识库中进行 RAG 检索。\n"
                "要求：\n"
                "1. 去除无关的语气词、礼貌用语。\n"
                "2. 提取核心实体、技术术语和关键动作。\n"
                "3. 如果有上下文，利用上下文补充指代不明的部分。\n"
                "4. 直接输出改写后的查询，不要包含任何解释或额外内容。"
            )
            
            user_prompt = f"原始查询: {query}\n"
            if context:
                user_prompt += f"补充上下文: {context}\n"
            user_prompt += "改写后的搜索查询:"
            
            rewritten = self.rag_client.call_llm(system_prompt, user_prompt)
            
            if rewritten:
                # 清理可能的多余空白或标点
                rewritten = rewritten.strip().strip('"').strip("'")
                logger.info(f"查询改写: '{query}' -> '{rewritten}'")
                return rewritten
            else:
                logger.warning("LLM 返回为空，使用原始查询。")
                return query
                
        except Exception as e:
            logger.error(f"查询改写失败: {e}，回退到原始查询。")
            return query
