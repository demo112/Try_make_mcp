# CONSENSUS: GetInRAGFlow

## 1. 需求定义
构建一个基于 MCP 协议的 RAG 服务代理（`rag_flow_mcp`），用于连接 RAGFlow 知识库与评审工作流。核心能力是自动回答业务澄清点，并提供质量评估报告。

## 2. 核心功能规范

### 2.1 知识检索与问答 (Retrieval & QA)
- **输入**: 
  - `question`: 待澄清的问题描述。
  - `context` (可选): 问题的业务上下文（如所属模块、关联实体）。
- **处理**: 调用 RAGFlow API 进行语义检索和答案生成。
- **输出**: 
  - `answer`: 生成的答案文本。
  - `citations`: 引用来源（文档名、段落）。

### 2.2 质量评估 (Quality Evaluation)
- **机制**: 对每个 RAG 生成的答案进行实时评估。
- **指标**:
  - **Relevance Score (0-1)**: 答案与问题的相关性。
  - **Confidence Score (0-1)**: 模型对自己回答的置信度。
- **策略**: 
  - 设定阈值（如 0.7）。低于阈值的答案标记为“低置信度”，提示人工复核。

### 2.3 批量处理 (Batch Processing)
- **能力**: 支持读取 `06_方案业务评审问题_*.md` 格式文档。
- **动作**: 自动解析其中的“问题描述”，批量调用 QA 接口，并将结果回填至“回答”字段。

## 3. 技术约束与依赖
- **协议**: MCP (Model Context Protocol)。
- **语言**: Python 3.10+。
- **外部依赖**: RAGFlow API (需配置 Endpoint 和 API Key)。
- **评估模型**: 可复用当前环境的 LLM 或 RAGFlow 内置能力进行评估。

## 4. 交付物
1.  **源代码**: `src/apps/rag_flow_mcp/`
2.  **配置文件**: `.env` (包含 RAGFLOW_API_KEY, RAGFLOW_HOST 等)
3.  **工具定义**:
    - `query_ragflow`
    - `batch_answer_clarifications`
4.  **文档**: 使用说明与集成指南。

## 5. 验收标准
- [ ] 能够成功连接 RAGFlow 并获取答案。
- [ ] 能够准确解析评审工作流的 Markdown 问题文档。
- [ ] 能够将答案回填到 Markdown 文档中，且格式正确。
- [ ] 能够输出每个答案的质量评分。
