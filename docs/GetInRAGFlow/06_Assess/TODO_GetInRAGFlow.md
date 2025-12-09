# TODO: GetInRAGFlow

## 待办事项 (Backlog)

### High Priority
- [ ] **Prompt 调优**: 针对复杂文档结构，优化 `evolution.py` 中的提示词，提高 Markdown 格式保持的稳定性。
- [ ] **L2 知识库扩容**: 导入更多历史评审记录，构建初始的 L2 知识库，避免“冷启动”时 RAG 效果不佳。

### Medium Priority
- [ ] **可视化配置**: 为 MCP Server 增加简单的 Web UI 用于配置 API Key 和 RAG Endpoint (目前依赖 .env)。
- [ ] **流式响应**: 将 RAG 检索过程改为 Streaming 响应，减少用户等待焦虑。

### Low Priority
- [ ] **多语言支持**: 虽然当前要求全中文，但架构上可预留 i18n 接口，支持未来扩展。
