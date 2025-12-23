# ALIGNMENT_MD转多格式MCP

## 1. 原始需求分析
**用户需求**: "现在我需要一个将md文件输出为excel、word、pdf等格式的的mcp"

**核心功能**:
1. 输入: Markdown 文件 (路径或内容)。
2. 处理: 格式转换逻辑。
3. 输出: Excel (.xlsx), Word (.docx), PDF (.pdf) 等格式文件。
4. 接口: MCP Tool 接口。

## 2. 项目现状分析
- **架构**: 使用 Python 的 `mcp` 库，特别是 `FastMCP` 模式 (参考 `src/apps/math_time/server.py`)。
- **目录结构**: 
  - 代码应位于 `src/apps/md_converter/server.py` (新建)。
  - 文档位于 `docs/MD转多格式MCP/`。
- **环境**: Windows, Python 3.13 (虚拟环境 .venv)。
- **现有依赖**: 需要检查 `requirements.txt` 是否包含转换所需的库。

## 3. 歧义澄清与假设
- **Q1: Markdown 转 Excel 的逻辑是什么？**
  - *假设*: 提取 Markdown 中的表格转换为 Excel Sheets。如果无表格，则转换可能无意义或仅作为纯文本放入单元格。
- **Q2: 转换库的选择？**
  - *Word*: `python-docx` + `markdown2` (或直接解析 MD)。
  - *PDF*: `markdown-pdf` 或 `weasyprint` (需要 HTML 中间层)。
  - *Excel*: `openpyxl` 或 `pandas` (用于处理表格)。
  - *策略*: 优先使用纯 Python 库以避免复杂的系统依赖 (如 pandoc)。
- **Q3: 输入方式？**
  - *假设*: 提供本地文件路径 `source_path` 和目标路径 `output_path`。
- **Q4: 是否支持批量？**
  - *假设*: 先实现单文件转换，批量可通过多次调用 Tool 实现。

## 4. 推荐技术方案
- **Server Name**: `MDConverter`
- **Tools**:
  - `convert_md_to_word(source_path, output_path)`
  - `convert_md_to_pdf(source_path, output_path)`
  - `convert_md_to_excel(source_path, output_path)` (提取表格)
- **依赖**:
  - `markdown` (基础解析)
  - `python-docx` (Word)
  - `pdfkit` 或 `weasyprint` (PDF, 需注意 Windows 依赖) -> 推荐 `markdown-pdf` 或 `xhtml2pdf` 尽量减少非 Python 依赖。
  - `openpyxl` (Excel)
  - `beautifulsoup4` (辅助 HTML 解析以提取表格)
