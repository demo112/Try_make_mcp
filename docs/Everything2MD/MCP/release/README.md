# Everything2MD 用户手册 (User Manual)

## 1. 简介 (Introduction)

Everything2MD 是一个强大的 MCP (Model Context Protocol) 服务，旨在将各种常见的文档格式转换为 Markdown 格式，以便 LLM (大语言模型) 能够轻松读取和理解。

### 支持的格式
*   **Microsoft Office**: `.docx`, `.doc`, `.xlsx`, `.xls`, `.pptx`, `.ppt`
*   **PDF**: `.pdf` (支持文本提取和 OCR)
*   **Images**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp` (使用 OCR 提取文本)

## 2. 安装与运行 (Installation & Execution)

### 2.1 直接运行 EXE (推荐)
1.  下载最新版本的 `everything2md.exe` 及 `config.json`。
2.  确保它们在同一目录下。
3.  双击 `everything2md.exe` 即可启动服务（注意：MCP 服务通常由 Client 自动调用，直接双击可能无明显界面，但会在后台运行）。
4.  在 Claude Desktop 或其他 MCP Client 中配置该 EXE 路径。

### 2.2 通过 Python 运行
1.  克隆代码库。
2.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```
3.  运行服务：
    ```bash
    python src/apps/everything2md/server.py
    ```

## 3. 配置说明 (Configuration)

Everything2MD 使用 `config.json` 进行配置。请确保该文件位于 EXE 同级目录或 Python 脚本运行目录。

### 3.1 默认配置示例
```json
{
  "mcp_debug": false,
  "host_root": "",
  "container_root": "",
  "log_level": "INFO"
}
```

### 3.2 字段详解

| 字段名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `mcp_debug` | boolean | `false` | 是否开启 MCP 调试模式。开启后会输出详细日志到 stderr。 |
| `log_level` | string | `"INFO"` | 日志级别。可选值：`DEBUG`, `INFO`, `WARNING`, `ERROR`。 |
| `host_root` | string | `""` | **Docker 部署专用**。宿主机上的根路径（例如 `C:\`）。用于路径映射。 |
| `container_root` | string | `""` | **Docker 部署专用**。容器内的挂载路径（例如 `/mnt/c/`）。用于路径映射。 |

### 3.3 常见场景配置

#### 场景 A: 本地直接使用 (Windows)
无需修改默认配置即可。

#### 场景 B: Docker 部署 (Windows 挂载到 Linux 容器)
如果你的 MCP 服务运行在 Docker 中，但需要访问宿主机文件，需配置路径映射：
```json
{
  "host_root": "C:\\",
  "container_root": "/mnt/c/"
}
```
此时，Client 传入的 `C:\Users\Doc.docx` 会被自动映射为 `/mnt/c/Users/Doc.docx`。

## 4. 使用指南 (Usage Guide)

### 4.1 MCP Client 配置
在 Claude Desktop 的配置文件 (`claude_desktop_config.json`) 中添加：

```json
{
  "mcpServers": {
    "everything2md": {
      "command": "path/to/everything2md.exe",
      "args": []
    }
  }
}
```

### 4.2 工具调用
Everything2MD 提供了一个核心工具：

#### `convert_to_markdown`
将指定文件转换为 Markdown。

*   **参数**:
    *   `source_path` (string): 源文件的绝对路径。
    *   `output_path` (string): 目标 Markdown 文件的保存路径。
*   **示例**:
    ```text
    请帮我把 C:\Documents\report.pdf 转换为 Markdown。
    ```

## 5. 版本迭代日志 (Changelog)

### v0.1.0 (2024-05-20)
*   **Initial Release**: 首次发布。
*   **Feature**: 支持 Office (Word, Excel, PowerPoint) 转 Markdown。
*   **Feature**: 支持 PDF 转 Markdown。
*   **Feature**: 支持图片 OCR 转 Markdown。
*   **Config**: 引入 `config.json` 配置文件支持。
