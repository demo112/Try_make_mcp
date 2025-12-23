# CONSENSUS_MD转多格式MCP

## 1. 需求定义
开发一个 MCP Server (`MDConverter`)，提供将 Markdown 文件转换为 Word, PDF, Excel 格式的能力。

## 2. 验收标准
1. **Word 转换**: 
   - 支持标题、段落、列表、代码块的基本样式保留。
   - 输出 `.docx` 文件。
2. **PDF 转换**:
   - 布局清晰，支持中文显示 (需处理字体问题)。
   - 输出 `.pdf` 文件。
3. **Excel 转换**:
   - 自动提取 Markdown 中的表格。
   - 每个表格存为 Sheet 或在同一 Sheet 中排列。
   - 若无表格，返回提示或空文件。
   - 输出 `.xlsx` 文件。
4. **接口规范**:
   - 符合 MCP Tool 标准。
   - 参数清晰：`source_path` (绝对路径), `output_path` (绝对路径)。
   - 错误处理：文件不存在、权限不足、格式错误均有明确报错。

## 3. 技术实现路径
- **基础框架**: `mcp[cli]` (FastMCP)。
- **核心库**:
  - Markdown 解析: `markdown`
  - Word: `python-docx` + 自定义解析器 (将 HTML/AST 转为 docx 元素)。
  - PDF: `markdown` -> HTML -> `xhtml2pdf` (支持 CSS，且纯 Python 相对好配置)。
  - Excel: `markdown` -> HTML -> `BeautifulSoup` (提取 table) -> `openpyxl` / `pandas`。

## 4. 约束与限制
- **环境**: Windows。
- **字体**: PDF 生成需指定支持中文的字体 (如 SimHei 或微软雅黑)，否则会乱码。
- **安全性**: 仅允许操作用户授权目录下的文件 (MCP 机制保障，但代码层也应做基本路径检查)。

## 5. 依赖变更
需要在 `requirements.txt` 中添加:
- `markdown`
- `python-docx`
- `xhtml2pdf`
- `openpyxl`
- `beautifulsoup4`
