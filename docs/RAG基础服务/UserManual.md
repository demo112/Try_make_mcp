# 用户手册：RAG基础服务 (User Manual)

## 1. 简介
本服务提供 RAGFlow 知识库的基础管理能力，并支持智能澄清建议填充。

## 2. 配置说明
在使用前，请确保项目根目录或 `src/apps/rag_base/` 下存在 `.env` 文件：

```ini
RAGFLOW_API_KEY=ragflow-xxxxxxxxxxxxxxxx
RAGFLOW_HOST=http://192.168.150.76:8081
RAGFLOW_CHAT_ID=xxxxxxxxxxxxxxxx  # 必填，用于场景一检索
LOG_LEVEL=INFO
```

## 3. 工具列表

### 3.1 知识库管理
- `create_dataset(name, ...)`: 创建知识库
- `delete_dataset(id)`: 删除知识库
- `list_datasets(page, page_size)`: 列出知识库

### 3.2 文档管理
- `upload_document(dataset_id, file_path)`: 上传文件
- `delete_document(document_id)`: 删除文件
- `list_documents(dataset_id)`: 列出文件

### 3.3 业务场景
- `fill_clarification_suggestions(doc_path)`: 
  - 读取 Markdown 文档中的问题。
  - 自动调用 RAG 检索。
  - 生成带有 AI 建议的副本 (`_ai_revision_...md`)。

#### 💡 如何编写文档以被识别？
工具使用以下规则识别问题：
1. **Header 识别**: 任何以 `#` 开头的标题，如果包含 `?`、`？` 或以 `Question` 开头，会被识别为问题。
   - 示例: `## 什么是 RAG?` 或 `### Question 1`
2. **字段补充**: 如果标题本身不含问号，工具会检查标题下是否有 `- 描述:` 或 `- 问题:` 字段。
   - 示例:
     ```markdown
     ## 功能点 A
     - 描述: 用户登录时鉴权失败如何处理？
     ```
     此时，工具会将“功能点 A 用户登录时鉴权失败如何处理？”作为查询词。

### 3.4 场景一原子工具 (高级用法)
如果您希望自定义工作流，可以使用以下原子工具：
- `create_shadow_file(file_path)`: 创建文件的安全副本。
- `extract_questions_from_doc(file_path)`: 从文档中解析 Header 问题。
- `retrieve_rag_suggestion(query)`: 获取单条问题的 AI 建议及置信度（会自动清洗 Query）。
- `apply_suggestions_to_doc(file_path, suggestions_map)`: 将建议回填到文档。

## 4. 提示词与自定义
本工具在 MCP 端执行简单的**查询清洗**（去除Markdown符号和前缀），最终的回答质量取决于 RAGFlow 服务端的配置。
建议在 RAGFlow 控制台中为 `RAGFLOW_CHAT_ID` 配置如下 **System Prompt**：
```text
你是一个专业的架构评审助手。
请基于检索到的知识库片段回答用户的问题。
回答应简明扼要，适合作为评审意见。
```

## 5. 故障排查
- **API 404 错误**: 检查 `RAGFLOW_HOST` 是否正确，是否需要包含 `/api` 后缀（本系统默认会自动拼接 `/api/v1`，如果您的部署不同，请修改代码或 Host）。
- **无法生成建议**: 检查日志，确认 `RAGFLOW_CHAT_ID` 是否配置，以及检索置信度是否过低。
