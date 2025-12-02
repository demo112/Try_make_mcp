# 任务拆解文档：构建 Math & Time MCP 服务

## 1. 任务依赖图

```mermaid
graph TD
    T1[Task 1: 环境配置] --> T2[Task 2: 项目结构]
    T2 --> T3[Task 3: 基础 Server 框架]
    T3 --> T4[Task 4: 实现 Tool (Add)]
    T3 --> T5[Task 5: 实现 Resource (Time)]
    T4 --> T6[Task 6: 验证与文档]
    T5 --> T6
```

## 2. 原子任务列表

### Task 1: 环境配置

- **目标**: 准备 Python 开发环境。
- **步骤**:
  1. 创建 `requirements.txt`，添加 `mcp`。
  2. 创建虚拟环境 `venv`。
  3. 安装依赖。
- **验收**: `pip list` 显示 `mcp` 已安装。

### Task 2: 项目结构

- **目标**: 建立文件骨架。
- **步骤**:
  1. 创建 `src/` 目录。
  2. 创建 `src/__init__.py` (空文件)。
  3. 创建 `src/server.py` (空文件)。
- **验收**: 目录结构符合架构设计。

## Task 3: 基础 Server 框架

- **目标**: 编写 `server.py` 的骨架代码。
- **步骤**:
  1. 导入 `mcp.server.fastmcp` 中的 `FastMCP`。
  2. 初始化 `mcp = FastMCP("MathTime")`。
  3. 添加主运行逻辑 (`mcp.run()`)。
- **验收**: `python src/server.py` 运行不报错（可能阻塞等待输入）。

### Task 4: 实现 Tool (Add)

- **目标**: 添加加法功能。
- **步骤**:
  1. 使用 `@mcp.tool()` 装饰器。
  2. 编写 `add(a: int, b: int) -> int` 函数。
  3. 添加清晰的 docstring（这对 LLM 很重要）。
- **验收**: 代码通过静态检查。

### Task 5: 实现 Resource (Time)

- **目标**: 添加时间查询功能。
- **步骤**:
  1. 使用 `@mcp.resource("time://now")` 装饰器。
  2. 编写 `get_time() -> str` 函数。
- **验收**: 代码通过静态检查。

### Task 6: 验证与文档

- **目标**: 确保服务可用并方便他人使用。
- **步骤**:
  1. 编写 `README.md`，说明如何运行。
  2. (可选) 使用 `npx @modelcontextprotocol/inspector` 进行测试。
- **验收**: 能够通过 Inspector 或 Client 成功调用。
