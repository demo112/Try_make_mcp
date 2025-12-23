from typing import Dict

# Prompt Engineering Configuration

# 1. LLM Query Preprocessing Prompt
# Used in retrieve_rag_suggestion to clean and refine the user query.
PREPROCESS_SYSTEM_PROMPT = (
    "你是一个专业的搜索查询优化助手。你的任务是从用户的输入中提取核心检索关键词。"
    "去除无关的修饰语、格式符号（如markdown标记）和冗余信息。"
    "请直接返回优化后的查询字符串，不要包含任何解释或额外内容。"
)

# 2. RAG Synthesis Prompt
# Used in retrieve_rag_suggestion (when dataset_id is provided) to generate the final answer from chunks.
SYNTHESIS_SYSTEM_PROMPT = (
    "你是一个专业的文档助手。请根据提供的上下文片段回答用户的问题。"
    "如果上下文中包含答案，请提供详细的建议。"
    "如果上下文与问题不相关，请回答“无相关信息”。"
    "保持回答客观、准确。"
)

# Function to get default prompts (can be extended to load from file)
def get_prompts() -> Dict[str, str]:
    return {
        "preprocess_system_prompt": PREPROCESS_SYSTEM_PROMPT,
        "synthesis_system_prompt": SYNTHESIS_SYSTEM_PROMPT
    }
