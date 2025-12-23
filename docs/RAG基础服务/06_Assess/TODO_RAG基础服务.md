# 待办事项清单：RAG基础服务 (TODO)

## 1. 用户需执行的操作

### 1.1 环境配置 (.env)
请在运行环境（或 `dist/rag_base_release` 目录）下创建或更新 `.env` 文件，填入以下关键配置：

```ini
# RAGFlow 服务地址
RAGFLOW_HOST=http://127.0.0.1:9380
# RAGFlow API Key (必须提供)
RAGFLOW_API_KEY=sk-xxxxxxxxxxxxxxxx

# [可选] MCP 端 LLM 配置 (用于场景一的高级编排)
# 如果不配置，默认使用 RAGFLOW_HOST 和 RAGFLOW_API_KEY
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-yyyyyyyyyyyyyyyy
```

### 1.2 知识库准备
- 确保 RAGFlow 中已存在相关的知识库。
- 如果使用场景一的 `fill_clarification_suggestions`，建议获取目标知识库的 `dataset_id`，以便使用更精准的 MCP-side LLM 编排流程。

### 1.3 运行验证
- 双击 `rag_base.exe` 运行服务（注意：它是 Stdio 服务，通常需要由 MCP Client 如 Claude Desktop 或 VS Code 启动）。
- 使用 MCP Inspector 进行调试：
  ```powershell
  npx @modelcontextprotocol/inspector dist/rag_base_release/rag_base.exe
  ```

## 2. 遗留/待优化项 (开发侧)
- [ ] **自动复制 UserManual**: 目前构建脚本未自动将 UserManual.md 复制到 dist 目录，需手动复制。
- [ ] **日志轮转**: 目前日志文件会无限增长，建议添加 LogRotation 配置。
- [ ] **流式响应**: 目前所有工具均为同步返回，对于长文本生成，未来可考虑支持 MCP 的 Progress 通知。

## 3. 支持与反馈
如有任何问题，请联系开发团队或查阅 `UserManual.md`。
