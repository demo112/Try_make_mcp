# 任务：MCP 可用性检查 - 待办事项 (TODO)

## 待优化项
- [ ] **修复测试脚本编码问题**: `src/factory/verify_mcp.py` 在读取 stderr 时遇到 `UnicodeDecodeError`，建议增加错误处理或指定编码 (gbk/utf-8)。
- [ ] **CI/CD 集成**: 建议将构建流程集成到 CI/CD，确保每次 Release 自动包含 EXE。

## 用户操作指引
您现在可以直接在 Claude Desktop 或 Trae 中配置使用该 MCP：
```json
"get-in-rag-flow": {
  "command": "c:\\Users\\Administrator\\Documents\\Win_trae_projects\\released\\try_make_mcp\\dist\\rag_flow_mcp_release\\rag_flow_mcp.exe",
  "args": []
}
```
请确保该目录下的 `.env` 文件已正确配置您的 RAGFlow API Key。
