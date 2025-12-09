# ALIGNMENT: GetInRAGFlow

## 1. 原始需求与背景
**用户输入**：
> 在执行评审工作流的过程中，会产生很多的待澄清点... 需要从原有的资料中找到这部分内容来解答新方案的待澄清点。此时就需要调用ragflow平台的知识库来查询相关的信息以做出澄清。同时，需要对检索以及回答的质量要有个评估和规范。

**核心痛点**：
- 评审过程中产生的“待澄清点”数量多，人工回答效率低。
- 很多问题的答案其实存在于旧有的产品文档或方案中，但由于信息分散，新方案编写者未注意到。
- 依赖人工检索容易遗漏，且质量参差不齐。

**业务目标**：
- **自动化答疑**：利用 RAGFlow 检索现有知识库，自动回答待澄清点。
- **质量可控**：建立回答质量评估机制，确保自动生成的答案准确、相关，不误导用户。
- **无缝集成**：嵌入现有的“评审工作流”中，作为辅助工具。

## 2. 业务上下文分析
### 2.1 现有评审工作流 (Reference: `docs\评审工作流MCP\评审工作流原文.md`)
- **Stage 3 (Atomize)**: 产生 `04_业务澄清点_【方案名称】.md`。
- **Stage 5 (Automate)**: 生成 `06_方案业务评审问题_【方案名称】.md`，其中包含 `**回答**：[留空供负责人填写]`。
- **切入点**：在 Stage 5 生成问题列表后，或者在 Stage 3 识别澄清点时，引入 GetInRAGFlow。
- **最佳切入时机**：在生成 `06_方案业务评审问题` 文档之前或之后，自动预填充“回答”字段，并标记“置信度/来源”。

### 2.2 RAGFlow 角色
- 作为知识源（Knowledge Base）。
- 提供检索（Retrieval）和生成（Generation）能力。
- 需要通过 API 进行交互。

### 2.3 质量评估 (Quality Assurance)
- 仅有 RAG 结果是不够的，必须评估：
    - **检索相关性 (Context Relevance)**: 检索到的文档片段是否真的与问题相关？
    - **答案忠实度 (Faithfulness)**: 答案是否忠实于检索到的文档？
    - **答案有用性 (Answer Relevance)**: 答案是否直接解决了用户的澄清点？
- 策略：引入 **LLM-as-a-Judge** 或使用 RAGFlow 自带的评分（如果有），输出置信度分数。低分答案不予展示或标记为“需人工确认”。

## 3. 待澄清问题与假设
1.  **RAGFlow 接口**：假设 RAGFlow 提供了标准的 HTTP API 用于查询和检索。我们需要具体的 API 文档或 Endpoint。
2.  **知识库准备**：假设相关的旧产品文档、方案已导入 RAGFlow。
3.  **触发方式**：是用户手动触发“自动回答”，还是工作流自动触发？建议作为 MCP Tool 提供，由 Agent 或用户按需调用。
4.  **输出形式**：直接修改 Markdown 文档，还是提供一个独立的建议报告？建议直接填充到 `06` 文档的“回答”栏，并附带引用来源。

## 4. 建议方案方向
开发一个名为 `get_in_ragflow` 的 MCP Server (或集成进 `review_workflow_mcp`)，提供以下工具：
- `rag_answer_question(question, context)`: 查询 RAGFlow 并返回答案及引用。
- `evaluate_rag_quality(question, answer, contexts)`: 评估答案质量。
- `batch_process_clarifications(file_path)`: 读取澄清点文档，批量回答并回写。

## 5. 决策点
- **架构模式**：独立 MCP App 还是 现有 App 的插件？
    - *建议*：独立 App `rag_flow_mcp`，保持职责单一，通用性强。
- **评估标准**：使用 RAGAS 框架思想（Relevance, Faithfulness, Correctness）。
