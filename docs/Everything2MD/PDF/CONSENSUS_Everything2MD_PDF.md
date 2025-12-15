# 共识文档 (CONSENSUS) - Everything2MD PDF 优化

## 1. 需求定义
### 1.1 核心功能
- **PDF 解析引擎替换**: 将 PDF 转换逻辑从 subprocess 调用 LibreOffice 更改为调用 Python 库 `pymupdf4llm`。
- **Markdown 输出**: 利用 `pymupdf4llm.to_markdown()` 直接生成 Markdown 内容并写入文件。

### 1.2 验收标准
- [ ] 能够正确转换纯文本 PDF。
- [ ] 能够识别并保留 PDF 中的表格结构（Markdown 表格）。
- [ ] 转换速度明显快于原 LibreOffice 方案。
- [ ] 不再依赖 LibreOffice 处理 PDF 文件。

## 2. 技术实现方案
### 2.1 依赖变更
- 添加 `pymupdf4llm` 到 `requirements.txt`。
- 注意：`pymupdf4llm` 依赖 `pymupdf`。

### 2.2 代码变更 (`server.py`)
- 导入 `pymupdf4llm`。
- 修改 `convert_to_markdown` 函数中 `elif file_extension == '.pdf':` 的分支逻辑。
- 删除原有的 PDF -> HTML -> MD 中间文件清理逻辑。

## 3. 风险评估
- **OCR 支持**: `pymupdf4llm` 主要处理可提取文本的 PDF。对于扫描版 PDF（纯图片），它可能无法提取文本。
- **缓解措施**: 目前仅处理文本版 PDF。OCR 是未来的长期规划（Todo List 中已有）。如果遇到扫描版，返回提示信息 "No text found (Scanned PDF?)"。
