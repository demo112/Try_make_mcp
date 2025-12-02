# Math & Time MCP Server

这是一个简单的 MCP 服务，用于演示如何构建 MCP 的核心功能。

## 功能
- **Tool**: `add(a, b)` - 计算两个数字的和。
- **Resource**: `time://now` - 获取当前系统时间。

## 快速开始

### 1. 环境配置
确保已安装 Python 3.10+。

```bash
# 创建虚拟环境
py -3 -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行服务
本服务使用 stdio 协议，通常由 MCP Client (如 Claude Desktop 或 mcp-inspector) 调用。

如果你想手动测试，可以使用 MCP Inspector:

```bash
npx @modelcontextprotocol/inspector py src/server.py
```

或者直接运行 (它会等待标准输入):

```bash
py src/server.py
```
