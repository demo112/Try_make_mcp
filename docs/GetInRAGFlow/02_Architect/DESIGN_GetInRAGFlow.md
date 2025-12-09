# DESIGN: GetInRAGFlow (rag_flow_mcp)

## 1. 系统架构
采用分层架构设计，确保关注点分离。

```mermaid
graph TD
    User[用户/Agent] -->|MCP Protocol| Server[MCP Server]
    Server -->|Dispatch| Tools[工具层]
    
    subgraph Core Logic
        Tools --> DocProc[文档处理器]
        Tools --> RAGClient[RAG 客户端]
        Tools --> Evaluator[质量评估器]
    end
    
    RAGClient -->|HTTP/REST| ExternalRAG[RAGFlow 平台]
    DocProc -->|Read/Write| LocalFS[本地文件系统]
    Evaluator -->|Prompt| LLM[LLM 服务 (可选)]
```

## 2. 模块设计

### 2.1 Server Layer (`server.py`)
- **职责**: 暴露 MCP 工具接口，处理请求路由。
- **工具列表**:
  - `check_rag_connection()`: 验证 RAGFlow 连接。
  - `query_rag(question, dataset_ids)`: 单次查询。
  - `process_review_doc(file_path, dataset_ids)`: 批量处理评审文档。

### 2.2 RAG Client (`core/rag_client.py`)
- **职责**: 封装 RAGFlow API 调用。
- **接口**:
  - `retrieve(question)`: 仅检索文档。
  - `answer(question)`: 检索并生成答案。
- **配置**: `RAGFLOW_API_KEY`, `RAGFLOW_BASE_URL`.

### 2.3 Document Processor (`core/doc_processor.py`)
- **职责**: 解析和回写 Markdown 评审文档。
- **逻辑**:
  - 识别 `## [序号].[标题]` 块。
  - **关键增强 1 (Context)**: 
    - 提取文档级上下文（如 `ALIGNMENT` 文档内容或当前文档头部介绍）。
    - 提取局部 `**业务上下文**` 和 `**问题描述**`。
    - **Query 构造**: 调用 LLM 将 (Global Context + Local Context + Question) 总结为高质量的搜索 Query。
  - **关键增强 2 (Field)**:
    - 新增独立字段 `**AI 参考建议**`，不占用 `**回答**` 字段。
    - 插入位置：在 `**期望澄清**` 之后，`**回答**` 之前。
  - **安全策略**: 若 `**AI 参考建议**` 已存在，则更新其内容；不触碰 `**回答**` 字段。
  - 插入格式: 
    ```markdown
    **AI 参考建议**：
    > 🤖 **RAG自动回复** (置信度: {score})
    > {answer}
    >
    > *来源: {citation}*
    
    **回答**：[留空供负责人填写]
    ```

### 2.4 Quality Evaluator (`core/evaluator.py`)
- **职责**: 评估 QA 质量。
- **方法**: 
  - **Level 1**: 检查 RAGFlow 返回的相似度/置信度分数。
  - **Level 2**: 规则检查（是否包含“不知道”、“无法回答”等拒识词）。
  - **Level 3 (Optional)**: 调用轻量 LLM 校验 Answer 是否响应了 Question。
  - **决策**: 若置信度 < 阈值 (e.g. 0.3)，则标记为 "低置信度建议" 或仅作为注释插入。

## 3. 数据流设计
1.  **批量处理流程**:
    - 用户调用 `process_review_doc(path)`.
    - `DocProc` 读取文件，解析出 N 个问题。
    - 遍历问题:
        - 调用 `RAGClient.answer(q)`.
        - 调用 `Evaluator.evaluate(q, a)`.
        - 格式化答案字符串。
    - `DocProc` 将答案回写文件。
    - 返回处理统计（成功数、低分忽略数）。

## 4. 接口契约
- **输入**: 
  - 文件路径必须是绝对路径。
  - 必须符合 6A 评审问题文档格式。
- **异常处理**:
  - RAG 服务不可用 -> 记录错误，继续处理下一个问题。
  - 无法解析问题 -> 跳过并警告。

## 5. 质量门控
- 代码覆盖率 > 80%。
- 所有 RAG 调用必须有超时设置。
- 必须处理 API Key 缺失的情况。
