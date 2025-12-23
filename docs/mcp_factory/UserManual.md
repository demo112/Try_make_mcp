# MCP生产工厂 使用手册

## 1. 简介
`mcp_factory` 是一个用于生产 MCP 应用程序的 MCP 服务。它将 MCP 制作工厂的核心能力（初始化、构建、验证）封装为标准的 MCP Tools，允许用户或 AI 助手通过工具调用来自动化创建 MCP。

## 2. 核心功能
*   **list_projects**: 列出当前工厂中已有的所有 MCP 项目。
*   **init_project**: 初始化一个新的 MCP 项目，生成符合 6A 标准的目录结构和文档模板。
*   **build_project**: 将指定的 Python MCP 项目打包为独立的 EXE 文件。
*   **verify_project**: 对构建好的 EXE 进行冒烟测试。

## 3. 安装与运行

### 3.1 源码运行 (推荐)
由于 `mcp_factory` 需要频繁操作项目源码和调用系统构建命令，建议直接在开发环境中运行。

**Claude Desktop 配置示例**:
```json
{
  "mcpServers": {
    "mcp_factory": {
      "command": "path/to/python",
      "args": ["-m", "src.apps.mcp_factory.server"],
      "cwd": "path/to/Try_make_mcp"
    }
  }
}
```

### 3.2 独立运行 (EXE)
您也可以将 `mcp_factory` 自身构建为 EXE。
```powershell
python mcp_manager.py build mcp_factory
```
构建后运行 `dist/mcp_factory.exe`。注意，EXE 版本运行时，默认的工作目录可能是 EXE 所在目录，这可能会影响它寻找其他项目源码的能力，因此建议通过配置文件或参数指定工作根目录（当前版本暂未完全实现动态根目录配置，建议源码运行）。

## 4. 常见工作流
1.  **新建项目**: 调用 `init_project(app_name="weather_bot", display_name="天气助手")`。
2.  **开发实现**: (人工或 AI) 编辑 `src/apps/weather_bot/server.py` 实现逻辑。
3.  **构建发布**: 调用 `build_project(app_name="weather_bot")`。
4.  **验证交付**: 调用 `verify_project(app_name="weather_bot")`。
