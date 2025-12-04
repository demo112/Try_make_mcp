# 待办事项: Everything2MD MCP 集成

## 1. 已完成
- [x] **路径配置**: 引入环境变量配置 (`LIBREOFFICE_PATH`, `PANDOC_PATH`)，允许用户在 `.env` 文件中自定义路径。
- [x] **PDF 转换优化**: 引入 `pymupdf4llm`，显著提升 PDF 到 Markdown 的转换质量（支持表格还原）。
- [x] **Docker 化**: 编写了 `Dockerfile` 和 `build_docker.sh`，并实现了宿主机到容器的路径映射 (`path_utils.py`)。
- [x] **并发处理**: 使用 `asyncio` 和线程池实现了异步转换，避免了 MCP 服务器阻塞。
- [x] **Web 预览**: 添加了基于 FastAPI 的 Web 界面 (`web_app.py`)，支持浏览器上传和预览。

## 2. 遗留问题
- 暂无关键阻碍。

## 3. 长期规划
- **更多格式**: 支持图片 OCR (使用 Tesseract) 转换为 Markdown。
- **CI/CD**: 在 GitHub Actions 中自动构建并推送 Docker 镜像。
- **UI 优化**: Web 界面目前较简陋，可进一步美化。
