# 需求共识文档：构建 Math & Time MCP 服务

## 1. 需求描述
构建一个基于 Python 的 MCP Server，旨在演示 MCP 的核心功能：Tools（工具）和 Resources（资源）。该服务将提供简单的数学计算功能和系统时间查询功能。

## 2. 验收标准 (Acceptance Criteria)
1.  **环境就绪**：项目包含 `venv` 虚拟环境，且安装了必要的 `mcp` 依赖。
2.  **服务运行**：`server.py` 能够无报错启动，并监听标准输入/输出 (stdio) 或 SSE (我们将优先使用 stdio 模式，因为它是 CLI 交互的标准)。
3.  **功能验证**：
    - **Tool**: `add` 工具能够接收两个数字并返回它们的和。
    - **Resource**: `time://now` 资源能够返回当前的格式化时间。
4.  **文档完整**：代码包含中文注释，且有 README 说明如何运行。

## 3. 技术实现路径
- **语言**: Python 3.10+
- **依赖管理**: `requirements.txt` (包含 `mcp`)
- **核心库**: `mcp[cli]`
- **通信协议**: Stdio (Standard Input/Output) Server Transport

## 4. 任务边界
- 不涉及 HTTP Server (SSE) 的复杂配置，仅使用 Stdio 以简化演示。
- 不涉及数据库连接。
