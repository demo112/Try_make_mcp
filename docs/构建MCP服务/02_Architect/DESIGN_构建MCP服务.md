# 架构设计文档：Math & Time MCP Server

## 1. 系统架构图 (Mermaid)

```mermaid
graph TD
    Client[MCP Client\n(Claude Desktop / Inspector)] <-->|Stdio / JSON-RPC| Protocol[MCP Protocol]
    Protocol <--> Server[Math & Time Server]
    
    subgraph "Server (Python)"
        Server -->|Expose| Tool_Add[Tool: Add]
        Server -->|Expose| Resource_Time[Resource: time://now]
        
        Tool_Add --> Logic_Math[Math Logic]
        Resource_Time --> Logic_Time[Time Logic]
    end
```

## 2. 核心组件设计

### 2.1 项目结构
```
project_root/
├── src/
│   ├── __init__.py
│   └── server.py       # 核心服务入口
├── docs/               # 6A 文档
├── requirements.txt    # 依赖定义
└── README.md           # 说明文档
```

### 2.2 接口设计 (Interface Contracts)

#### A. Tool: `add`
- **描述**: 执行两个数字的加法。
- **输入 (Schema)**:
  ```json
  {
    "type": "object",
    "properties": {
      "a": { "type": "integer", "description": "第一个加数" },
      "b": { "type": "integer", "description": "第二个加数" }
    },
    "required": ["a", "b"]
  }
  ```
- **输出**: 文本格式的计算结果。

#### B. Resource: `time://now`
- **URI**: `time://now`
- **MimeType**: `text/plain`
- **描述**: 获取服务器当前时间。
- **输出**: ISO 8601 格式的时间字符串 (e.g., "2023-10-27T10:00:00")。

## 3. 数据流 (Data Flow)
1.  **初始化**: Client 启动 Server (`python server.py`)。
2.  **握手**: Client 发送 `initialize` 请求，Server 返回 capabilities (支持 tools, resources)。
3.  **调用工具**: Client 发送 `call_tool("add", {a:1, b:2})` -> Server 计算 1+2 -> 返回 "3"。
4.  **读取资源**: Client 发送 `read_resource("time://now")` -> Server 获取系统时间 -> 返回时间字符串。

## 4. 技术选型
- **Python Library**: `mcp` (官方 SDK)。
- **Asyncio**: 使用 Python 的 `asyncio` 处理并发请求。
