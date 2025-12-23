# 自动生成测试 使用手册

## 1. 简介
本应用提供 MCP 服务，支持通过 Stdio 进行交互。

## 2. 安装与运行
无需安装，直接运行发布包中的 `test_auto_generated_app.exe` 即可。通常需要配合 MCP Client (如 Claude Desktop, Trae 等) 使用。

### 2.1 Client 配置
请在您的 MCP Client 配置文件（例如 Claude Desktop 的配置）中添加以下内容。
**注意**：请将 `command` 中的路径替换为 `test_auto_generated_app.exe` 的实际绝对路径。

```json
{
  "mcpServers": {
    "test_auto_generated_app": {
      "command": "D:/path/to/test_auto_generated_app.exe",
      "args": []
    }
  }
}
```

### 2.2 应用配置
在 EXE 同级目录下存在 `config.json` 文件，您可以修改它来调整应用行为。

```json
{
    "log_level": "INFO",
    "custom_message": "Hello from config.json!"
}
```

- `log_level`: 日志级别 (DEBUG, INFO, WARNING, ERROR)
- `custom_message`: `hello_world` 工具返回的自定义消息

## 3. 故障排查
如果应用无法启动，请尝试在命令行中运行 EXE，查看输出日志。
