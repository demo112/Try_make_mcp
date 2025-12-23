# 用户手册 (User Manual)

## 1. 简介
欢迎使用 **GetInRAGFlow**。本手册将指导您如何配置 MCP 客户端并使用本服务来加速您的软件架构设计流程。

## 2. 客户端配置

### 2.1 Claude Desktop / Trae 配置 (推荐)

我们强烈建议使用构建好的 EXE 文件运行 MCP 服务，配置最简单且无需 Python 环境。

在 `claude_desktop_config.json` 或 Trae 的 MCP 设置中添加：

```json
{
  "mcpServers": {
    "get-in-rag-flow": {
      "command": "c:\\path\\to\\rag_flow_mcp.exe",
      "args": []
    }
  }
}
```

**关键步骤**:
1. 确保 `.env` 文件与 `rag_flow_mcp.exe` 位于**同一目录**。
2. 在 `.env` 文件中配置所有环境变量（如 `RAGFLOW_API_KEY` 等）。

### 2.2 源码运行 (仅限开发)
如果您需要调试源码，请确保已激活虚拟环境：

```json
{
  "mcpServers": {
    "get-in-rag-flow-dev": {
      "command": "python",
      "args": ["-m", "src.apps.rag_flow_mcp.server"],
      "cwd": "c:\\path\\to\\Try_make_mcp"
    }
  }
}
```
*注意：源码运行时，请确保项目根目录存在 `.env` 文件。*

### 2.3 环境变量配置
无论使用哪种方式，请在 `.env` 文件中配置以下参数，**不要**直接写在 MCP 配置文件中：


## 3. 使用场景演练

### 场景 A: 评审问题澄清 (Main Quest)
1.  **准备文档**: 确保您的 `04_评审问题记录.md` 包含 YAML 头信息 (Product/Module)。
2.  **调用工具**: 在对话框中输入：
    > "请帮我分析 `docs/MyProject/04_评审问题记录.md` 中的问题，并给出建议。"
3.  **查看结果**: Agent 会调用 `fill_clarification_suggestions`，文档中会自动出现 `**AI 参考建议**`。
4.  **人工决策**: 您阅读建议后，在文档中手动填写 `**回答**：确认采用...`。

### 场景 B: 方案文档进化 (Main Quest)
1.  **前提**: 已完成场景 A 的人工决策。
2.  **调用工具**: 输入：
    > "根据评审记录的结论，请帮我更新方案文档 `docs/MyProject/02_Architect/MyScheme_v1.0.md`。"
3.  **结果确认**: Agent 会调用 `evolve_scheme_document`，生成 `MyScheme_v1.1.md`，并在其中包含新的设计变更。

### 场景 C: 知识沉淀 (Side Quest)
1.  **调用工具**: 输入：
    > "请将评审记录中已解决的问题收割为知识资产。"
2.  **结果确认**: Agent 调用 `harvest_knowledge_candidates` 提取问答对。
3.  **晋升入库**: 输入：
    > "将这些知识晋升到 L2 产品知识库。"
4.  **结果**: Agent 调用 `promote_knowledge`，将 JSON 文件存入指定目录。

## 4. 工具列表详情 (Tool Reference)

### 4.1 主线任务 (Main Quest)
- `fill_clarification_suggestions(doc_path)`: [推理] 读取评审问题记录，自动填充 RAG 建议。
- `evolve_scheme_document(scheme_doc_path, clarification_doc_path)`: [进化] 基于澄清决策进化方案文档。

### 4.2 治理管控 (Governance)
- `check_metadata_compliance(doc_path)`: 检查文档元数据 (Product, Module)。
- `validate_knowledge_conflict(candidate_json)`: 验证知识冲突 (规划中)。

### 4.3 知识全生命周期 (Lifecycle)
- `harvest_knowledge_candidates(doc_path)`: 从文档收割知识。
- `promote_knowledge(candidate_json, target_kb_path)`: 知识入库。

### 4.4 知识库浏览 (Browser)
- `list_knowledge_bases(page, page_size)`: 列出知识库。
- `list_knowledge_base_files(dataset_id, ...)`: 列出文件。
- `retrieve_chunks(dataset_id, query)`: 直接检索切片。

### 4.5 辅助工具 (Utils)
- `view_diff(file_path)`: 打开 VS Code 对比视图。
- `add_test_case(query, expected_keywords)`: 捕获测试用例。

## 5. 常见问题 (FAQ)

**Q: 为什么进化引擎没有修改文档？**
A: 请检查 `04_评审问题记录.md` 中是否包含了标准的 `**回答**：...` 格式。引擎仅针对已由人工确认的问题进行进化。

**Q: 如何区分不同产品的知识？**
A: 通过文档头部的 YAML Frontmatter (`product: ...`)。引擎会自动识别并关联到对应的知识空间。

**Q: API 404 错误?**
A: 检查 `RAGFLOW_HOST` 是否正确，是否需要包含 `/api` 后缀（本系统默认会自动拼接 `/api/v1`）。

**Q: 无法生成建议?**
A: 检查日志，确认 `RAGFLOW_CHAT_ID` 是否配置，以及检索置信度是否过低 (默认阈值 0.2)。
