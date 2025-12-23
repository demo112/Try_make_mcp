# 待办事项：RAG基础服务 (Todo)

## 1. 遗留配置
- [ ] **RAGFlow API 配置**: 用户需在 `.env` 中填写真实的 `RAGFLOW_API_KEY` 和 `RAGFLOW_HOST`。
- [ ] **Chat ID**: 场景一依赖 `RAGFLOW_CHAT_ID`，需在 `.env` 中配置。

## 2. 待优化
- [ ] **构建脚本优化**: 修改 `src/factory/build_app.py` 以支持中文文档目录的自动复制。
- [ ] **流式响应**: 目前场景一使用非流式响应，未来可考虑支持流式以提升体验（虽然对于文件写入场景非必须）。

## 3. 支持请求
- 如遇到 RAGFlow 连接 404，请确认 API 前缀是否为 `/api/v1`。
