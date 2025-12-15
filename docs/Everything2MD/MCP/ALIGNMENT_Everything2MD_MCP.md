# 对齐文档: Everything2MD MCP 集成

## 1. 原始需求
用户希望将 `Everything2MD` 项目的核心功能集成到 `Try_make_mcp` 项目中，作为一个模型上下文协议 (MCP) 服务。
`Everything2MD` 是一个将各种文档格式（Office、PDF、PPTX）转换为 Markdown 的工具。

## 2. 项目背景分析

### 源项目: Everything2MD
- **类型**: 基于 Shell 脚本的工具 (主要面向 Linux/Bash)。
- **核心逻辑**: `src/main.sh` 协调各种转换。
- **依赖项**:
  - LibreOffice (Doc/Docx/PDF -> HTML)
  - Pandoc (HTML -> Markdown)
  - pptx2md (PPTX -> Markdown)
- **结构**: 模块化的 Shell 脚本，Web UI (FastAPI)。

### 目标项目: Try_make_mcp
- **类型**: 基于 Python 的 MCP 项目。
- **结构**: `src/apps/` 包含 MCP 服务。
- **环境**: Windows。
- **限制**:
  - 系统工具如 LibreOffice 和 Pandoc 目前在 PATH 中不可用。
  - Python 虚拟环境 (`.venv`) 可用。

## 3. 澄清的歧义与决策

### Q1: 实现策略?
- **方案 A**: 将 Shell 脚本移植到 Python，由我负责下载安装 LibreOffice/Pandoc。(摩擦力高，与原始功能高度一致)
- **方案 B**: 尽可能使用 Python 原生库来复制功能，避免外部系统依赖。(摩擦力低，输出质量可能有所不同)
- **决策**: **方案 A** (将 Shell 脚本移植到 Python，并安装 LibreOffice/Pandoc) 是首选，以保持与原始功能的高度一致性。我将负责下载和安装这些工具。

### Q2: 架构?
- 创建一个新的应用 `src/apps/everything2md`。
- 通过 `FastMCP` 暴露工具。

### Q3: 范围?
- 核心功能: 文件转换为 Markdown。
- 支持格式: .docx, .xlsx, .pptx, .pdf, .doc, .xls, .ppt (基于文本)。

## 4. 后续步骤
- 创建共识文档。
- 使用 Python 库设计架构。
