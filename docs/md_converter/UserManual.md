# MDConverter 用户手册

## 简介
MDConverter 是一个强大的 MCP (Model Context Protocol) 工具服务，专门用于将 Markdown 文件转换为多种常见办公格式。它支持本地运行，并可轻松集成到 Claude Desktop、Cursor 等支持 MCP 的 AI 助手中。

## 功能特性
- **Markdown 转 Word (.docx)**: 保留标题、段落、列表、表格等基础格式。
- **Markdown 转 PDF (.pdf)**: 生成排版整洁的 PDF 文档，内置中文支持（依赖 Windows 系统字体）。
- **Markdown 转 Excel (.xlsx)**: 自动提取 Markdown 中的表格数据，支持多表格导出到不同 Sheet。

## 快速开始

### 1. 环境要求
- 操作系统: Windows (推荐), Linux/macOS (需自行配置字体)
- 无需安装 Python (使用发布的 EXE 版本时)

### 2. 在 Claude Desktop 中使用
编辑 Claude Desktop 的配置文件 `%APPDATA%\Claude\claude_desktop_config.json`，添加以下内容：

```json
{
  "mcpServers": {
    "md_converter": {
      "command": "C:\\path\\to\\md_converter.exe",
      "args": []
    }
  }
}
```
*请将 `C:\\path\\to\\md_converter.exe` 替换为您实际存放 `md_converter.exe` 的绝对路径。*

### 3. 在 Cursor 中使用
1. 打开 Cursor 设置 -> Features -> MCP。
2. 点击 "+ Add New MCP Server"。
3. Name: `MDConverter` (或任意名称)。
4. Type: `command`。
5. Command: `C:\path\to\md_converter.exe` (填入绝对路径)。

## 工具说明

### `convert_to_word`
将 Markdown 文件转换为 Word 文档。
- **参数**:
  - `source_path`: 源 Markdown 文件的绝对路径。
  - `output_path`: 目标 `.docx` 文件的绝对路径。

### `convert_to_pdf`
将 Markdown 文件转换为 PDF 文档。
- **参数**:
  - `source_path`: 源 Markdown 文件的绝对路径。
  - `output_path`: 目标 `.pdf` 文件的绝对路径。
- **注意**: 默认使用 `SimHei` (黑体) 或 `Microsoft YaHei` (微软雅黑) 以支持中文显示。

### `convert_to_excel`
提取 Markdown 文件中的表格并保存为 Excel。
- **参数**:
  - `source_path`: 源 Markdown 文件的绝对路径。
  - `output_path`: 目标 `.xlsx` 文件的绝对路径。
- **说明**: 如果源文件包含多个表格，它们将被分别保存在 Excel 的不同工作表 (Sheet) 中。

## 常见问题
**Q: PDF 中文乱码怎么办？**
A: 本工具在 Windows 下会自动查找系统字体 (`C:\Windows\Fonts\simhei.ttf` 或 `msyh.ttc`)。请确保您的系统安装了这些字体。

**Q: 转换后的格式错乱？**
A: 目前工具支持 Markdown 的基础语法。对于复杂的嵌套结构或自定义 HTML 标签，转换效果可能有所差异。建议保持 Markdown 结构简洁。
