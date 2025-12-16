# 用户手册 (User Manual)

## 1. 简介
欢迎使用 **GetInRAGFlow**。本手册将指导您如何配置 MCP 客户端并使用本服务来加速您的软件架构设计流程。

## 2. 客户端配置

### 2.1 Claude Desktop 配置
在 `claude_desktop_config.json` 中添加以下配置：

```json
{
  "mcpServers": {
    "get-in-rag-flow": {
      "command": "python",
      "args": [
        "-m",
        "src.apps.rag_flow_mcp.server"
      ],
      "env": {
        "RAGFLOW_API_KEY": "your_key",
        "RAGFLOW_HOST": "http://your_host",
        "RAGFLOW_TIMEOUT": "120",
        "RAGFLOW_TOP_K": "10",
        "RAGFLOW_SIMILARITY_THRESHOLD": "0.2",
        "PYTHONPATH": "absolute/path/to/Try_make_mcp"
      }
    }
  }
}
```

### 2.2 Trae/Cursor 配置
通常支持直接导入 MCP Server。请指向项目根目录并指定启动命令：
- **Command**: `python -m src.apps.rag_flow_mcp.server`
- **Working Directory**: `c:\Users\Administrator\Documents\trae_projects\Try_make_mcp`

### 2.3 独立 EXE 运行
如果您使用打包好的 EXE 文件 (`dist/rag_flow_mcp_release/rag_flow_mcp.exe`)：
1. **配置环境**：将目录下的 `.env.example` 复制并重命名为 `.env`。
2. **填写参数**：编辑 `.env` 文件，填入您的 `RAGFLOW_API_KEY`、`RAGFLOW_HOST` 以及可选参数如 `RAGFLOW_TIMEOUT`, `RAGFLOW_TOP_K`, `RAGFLOW_SIMILARITY_THRESHOLD` 等信息。
3. **启动运行**：确保 `.env` 文件与 `.exe` 文件位于**同一目录**，然后双击运行或在命令行中启动。

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

## 4. 常见问题 (FAQ)

**Q: 为什么进化引擎没有修改文档？**
A: 请检查 `04_评审问题记录.md` 中是否包含了标准的 `**回答**：...` 格式。引擎仅针对已由人工确认的问题进行进化。

**Q: 如何区分不同产品的知识？**
A: 通过文档头部的 YAML Frontmatter (`product: ...`)。引擎会自动识别并关联到对应的知识空间。
