# FINAL_MD转多格式MCP

## 1. 项目概述
本项目实现了一个基于 MCP 的 Markdown 文件转换服务，支持将 `.md` 文件转换为 `.docx`, `.pdf`, `.xlsx` 格式。

## 2. 交付物清单
- **源代码**:
  - `src/apps/md_converter/server.py`: MCP Server 入口。
  - `src/apps/md_converter/converters.py`: 核心转换逻辑。
- **文档**:
  - `docs/MD转多格式MCP/`: 包含完整的 6A 工作流文档。
- **依赖**:
  - `requirements.txt`: 已添加必要库。

## 3. 技术总结
- **Word**: 使用 `markdown` 解析 HTML，通过 `BeautifulSoup` 遍历并映射到 `python-docx`。
- **PDF**: 使用 `xhtml2pdf`，通过注册 Windows 本地字体 (`simhei.ttf` / `msyh.ttc`) 解决了中文乱码问题。
- **Excel**: 提取 Markdown 中的 `<table>`，解析为 Excel Sheet，支持多表格提取。

## 4. 遗留问题与改进建议
- **PDF 字体依赖**: 目前硬编码了 Windows 字体路径，迁移到 Linux/Mac 需调整。
- **样式还原度**: Word 和 PDF 仅还原了基础结构 (标题、段落、列表、表格)，复杂 Markdown 样式 (如引用、代码高亮、嵌套列表) 可能表现不佳。
- **图片支持**: 目前未处理 Markdown 中的本地图片或网络图片。
