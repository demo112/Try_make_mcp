# 共识文档: Everything2MD MCP 集成

## 1. 需求描述
在 `Try_make_mcp` 中构建一个模型上下文协议 (MCP) 服务，该服务能够将各种文档格式转换为 Markdown，灵感来源于 `Everything2MD` 项目。

## 2. 验收标准
- [ ] **MCP 服务**: 在 `src/apps/everything2md` 中实现一个新的 MCP 服务。
- [ ] **暴露工具**:
  - `convert_to_markdown(source_path, output_path)`: 通用转换工具。
- [ ] **支持格式**:
  - **DOCX**: 将 Word 文档转换为 Markdown。
  - **XLSX**: 将 Excel 表格转换为 Markdown 表格。
  - **PPTX**: 将 PowerPoint 演示文稿转换为 Markdown (使用 `pptx2md`)。
  - **PDF**: 将 PDF 文本转换为 Markdown。
  - **DOC**: 将 Word 97-2003 文档转换为 Markdown。
  - **XLS**: 将 Excel 97-2003 表格转换为 Markdown 表格。
  - **PPT**: 将 PowerPoint 97-2003 演示文稿转换为 Markdown。
- [ ] **依赖项**:
  - **LibreOffice**: 用于 DOC, XLS, PPT, PDF, DOCX, XLSX 的转换。
  - **Pandoc**: 用于 HTML 到 Markdown 的转换。
  - **pptx2md**: 用于 PPTX 到 Markdown 的转换。

## 3. 技术实现
- **语言**: Python 3.12+
- **框架**: `mcp` (FastMCP)
- **位置**: `src/apps/everything2md/`
- **入口点**: `server.py`

## 4. 边界
- **超出范围**:
  - 扫描 PDF 的 OCR (需要 Tesseract，重度依赖)。
  - 复杂 PDF 的完美布局保留。
  - Web UI (这是一个无头 MCP 服务)。
