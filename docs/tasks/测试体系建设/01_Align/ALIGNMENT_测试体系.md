# 测试体系建设 - 需求对齐 (Align)

## 1. 项目背景
当前 MCP Factory 项目缺乏自动化的测试体系，导致：
1.  **工厂自身稳定性**：修改工厂代码（如 `init_app` 或构建逻辑）时，缺乏回归测试，容易引入 Bug。
2.  **MCP 质量保障**：生成的 MCP 应用没有内置测试框架，开发者难以验证 Tool/Resource 的逻辑，只能依赖手动集成测试（连接 Claude/Trae），效率低下且覆盖率低。

## 2. 目标
构建两套独立的自动化测试体系：

### 体系 A：工厂自动化测试 (Factory Test System)
*   **目标对象**：`src/factory`, `src/common` 等工厂核心代码。
*   **核心能力**：
    *   验证 `init_app` 是否能生成正确的文件结构。
    *   验证 `build_app` 是否能正确调用 PyInstaller。
    *   验证 `verify_mcp` 是否能正确检测 EXE。
*   **技术栈**：`pytest`。

### 体系 B：MCP 应用测试框架 (MCP App Test Framework)
*   **目标对象**：由工厂生成的各个 MCP 应用 (如 `src/apps/xxx`)。
*   **核心能力**：
    *   提供通用的 `McpTestClient`，模拟 MCP Client (如 Claude) 的行为。
    *   支持 **Stdio 交互测试**：启动 MCP 进程，发送 JSON-RPC 请求，断言响应。
    *   支持 **逻辑单元测试**：直接导入 Tool 函数进行测试（无需启动进程）。
*   **交付方式**：
    *   封装为通用模块 `src.testing`。
    *   修改 `init_app.py` 模板，使新创建的 APP 自动包含 `tests/` 目录和示例用例。

## 3. 详细需求与边界

### 3.1 工厂测试 (System A)
*   **位置**：项目根目录下 `tests/factory/`。
*   **运行方式**：在项目根目录运行 `pytest`。
*   **CI 集成**：未来可集成到 GitHub Actions。

### 3.2 MCP 测试框架 (System B)
*   **核心组件**：
    *   `src.testing.mcp_client.McpClient`: 封装 subprocess 和 JSON-RPC 协议（基于 `verify_mcp.py` 改造）。
    *   `src.testing.fixtures`: Pytest fixtures，自动管理 MCP 进程生命周期。
*   **使用场景**：
    *   开发者在 `src/apps/my_app/` 下编写测试。
    *   运行 `pytest src/apps/my_app` 即可测试该应用。

## 4. 依赖系统
*   **Python 环境**：必须在 `.venv` 下运行。
*   **Pytest**：核心测试运行器。
*   **FastMCP**：被测对象依赖。

## 5. 关键决策
*   **是否测试 Docker**？
    *   初步阶段主要测试 Python 源码和 EXE（Windows 环境）。Docker 测试作为后续扩展。
*   **如何处理异步**？
    *   MCP 协议本身是异步的，但通过 Stdio 测试时，通常是同步等待响应（Request-Response 模式）。`McpClient` 将实现同步阻塞等待，简化测试编写。

## 6. 疑问与澄清
*   **现有 APP 如何处理？**
    *   现有 APP（如 `rag_flow_mcp`）不会自动获得测试目录，需要手动补全或运行脚本补全。
    *   **决策**：优先支持新 APP，手动为关键的现有 APP 添加测试示例。
