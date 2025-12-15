# 对齐文档 (ALIGNMENT) - Everything2MD PDF 优化

## 1. 背景与目标
### 1.1 背景
当前的 PDF 转换方案 (`LibreOffice` -> `HTML` -> `Pandoc` -> `Markdown`) 是一种通用的兜底方案。其缺点包括：
- **依赖重**: 需要安装庞大的 LibreOffice。
- **质量差**: 对于复杂的 PDF 排版（多栏、页眉页脚、表格），LibreOffice 的 HTML 导出功能表现不佳，导致最终 Markdown 可读性差。
- **速度慢**: 启动 LibreOffice 进程开销大。

### 1.2 目标
- 引入专门的 PDF 解析库 `pymupdf4llm` (基于 PyMuPDF)。
- 显著提升 PDF 转 Markdown 的结构还原度（标题、表格、列表）。
- 降低对外部命令 (LibreOffice) 的依赖（仅针对 PDF）。

## 2. 技术选型分析
### 2.1 选项 A: pdfminer.six
- **优点**: 纯 Python，无 C 扩展依赖（易安装）。
- **缺点**: 速度较慢，布局分析需要大量自定义逻辑，表格识别困难。

### 2.2 选项 B: PyMuPDF (fitz)
- **优点**: 速度极快，功能强大，支持复杂的文本提取。
- **缺点**: API 较底层，需要自己处理 Markdown 格式化。

### 2.3 选项 C: pymupdf4llm (推荐)
- **优点**: 基于 PyMuPDF，专门为 LLM/RAG 场景设计，直接输出高质量 Markdown，支持表格还原。
- **缺点**: 引入了新的 Python 依赖。

## 3. 需求澄清 (Q&A)
- **Q**: 是否完全移除 LibreOffice 的 PDF 转换？
  - **A**: 是的。一旦引入 `pymupdf4llm`，它将成为 PDF 的默认转换器。LibreOffice 仍用于 DOCX/XLSX/PPTX。
- **Q**: 如果 `pymupdf4llm` 失败怎么办？
  - **A**: 可以保留 LibreOffice 作为 fallback（备选方案），或者直接报错。考虑到 `pymupdf4llm` 的健壮性，通常不需要 fallback，但为了稳健性，可以设计为：先尝试 PyMuPDF，若崩溃则回退（虽然不太可能）。**决策**: 简化设计，直接使用 PyMuPDF，不设 fallback，因为 LibreOffice 转 PDF 效果太差，回退也没有意义。
- **Q**: 依赖包大小？
  - **A**: `pymupdf` 包含二进制文件，大约几十 MB，但在可接受范围内。

## 4. 交付物
- 更新 `requirements.txt` (添加 `pymupdf4llm`)
- 更新 `server.py` (重构 PDF 分支)
- 验证测试脚本 (对比新旧效果，或仅验证新效果)
