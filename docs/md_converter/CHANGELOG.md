# 变更日志 (Change Log)

本项目的所有重要变更都将记录在此文件中。

## [1.1.0] - 2025-12-04

### 新增 (Added)
- **Excel 复杂排版支持**: 
  - 自动识别并保留 Markdown 中的换行 (`<br>`)、无序列表 (`<ul>`)、有序列表 (`<ol>`) 和段落 (`<p>`)。
  - Excel 单元格内自动换行，列宽根据内容自适应调整。
- **离线安全模式**: 
  - 彻底禁用 PDF 转换时的所有网络请求，防止在无网环境下挂起。
  - 仅允许访问本地资源文件。
- **自动化验证**:
  - 构建流程新增 `verify_mcp.py`，在打包后自动启动 EXE 并验证 MCP 协议响应。
- **自动归档**:
  - 构建完成后自动生成带版本号的 ZIP 压缩包 (e.g., `md_converter_v1.1.0.zip`)。

### 优化 (Changed)
- **Excel 样式**:
  - 表头采用淡蓝色背景、加粗微软雅黑字体、居中对齐。
  - 所有单元格添加细边框，内容左上对齐。
- **构建系统**:
  - `build_app.py` 支持自动从 `server.py` 提取版本号。
  - 优化了 PyInstaller 配置，使用 `--collect-all` 确保 `reportlab` 等依赖完整打包。

### 修复 (Fixed)
- 修复了 PDF 转换中中文字体无法显示的问题 (需系统安装 SimHei/微软雅黑)。
- 修复了 `server.py` 在打包环境下导入路径错误的问题。

## [1.0.0] - 2025-12-04

### 初始发布 (Initial Release)
- 实现 Markdown 转 Word (.docx)。
- 实现 Markdown 转 PDF (.pdf)。
- 实现 Markdown 表格转 Excel (.xlsx)。
- 基于 FastMCP 框架实现 MCP Server。
- 支持打包为独立 EXE 文件。
