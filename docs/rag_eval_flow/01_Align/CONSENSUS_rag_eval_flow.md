# 项目共识文档 (Consensus Document)

## 1. 需求概述
构建一个名为 `rag_eval_flow` 的 MCP 服务，用于自动化执行 RAG 系统的 "生成用例 -> 执行问答 -> 评估打分" 闭环流程。

## 2. 工具定义 (Tools)

### 2.1 `generate_test_dataset`
*   **功能**: 从指定知识库文件生成问答对。
*   **输入**:
    *   `source_path` (string): 知识库文件或目录的绝对路径。
    *   `output_path` (string): 输出 CSV 文件的绝对路径。
    *   `num_pairs` (integer): 生成问答对的数量 (默认 20)。
*   **输出**: 生成摘要信息 (成功生成的数量，文件路径)。

### 2.2 `run_qa_test`
*   **功能**: 读取问题，基于知识库生成回答。
*   **输入**:
    *   `dataset_path` (string): 包含问题的 CSV 文件路径 (由 2.1 生成)。
    *   `knowledge_base_path` (string): 知识库源文件路径 (用于检索上下文)。
    *   `output_path` (string): 包含回答的 CSV 输出路径。
*   **输出**: 执行结果摘要。
*   **逻辑**:
    *   读取 CSV 中的 `question` 列。
    *   对每个问题，检索 `knowledge_base_path` 中的相关内容 (简单起见，如果文件较小，直接作为 Context；如果较大，进行简单切片检索)。
    *   调用 LLM 生成答案。
    *   保存为新文件，包含 `question`, `generated_answer`。

### 2.3 `evaluate_answers`
*   **功能**: 对生成回答进行打分。
*   **输入**:
    *   `qa_result_path` (string): 包含生成回答的 CSV 路径 (由 2.2 生成)。
    *   `standard_dataset_path` (string): 包含标准答案的 CSV 路径 (由 2.1 生成)。
    *   `output_path` (string): 最终评分 CSV 路径。
*   **输出**: 评估结果摘要 (平均分等)。
*   **逻辑**:
    *   读取 `generated_answer` 和 `standard_answer`。
    *   调用 LLM 评估相似度和准确性 (0-10分)。
    *   输出包含 `score` 和 `reason` 的 CSV。

## 3. 技术实现方案
*   **框架**: `fastmcp`
*   **LLM 调用**: 使用 `litellm` 或项目现有的 `src.common.llm` 封装。
*   **数据处理**: 使用 Python `csv` 和 `pandas` (如果需要)。
*   **环境**: 依赖 `.env` 中的 `GEMINI_API_KEY` (或相关 Key)。

## 4. 交付物
*   `src/apps/rag_eval_flow/server.py`: MCP 服务入口。
*   `src/apps/rag_eval_flow/logic.py`: 核心业务逻辑。
*   `docs/RAG评估工作流/UserManual.md`: 使用说明。
