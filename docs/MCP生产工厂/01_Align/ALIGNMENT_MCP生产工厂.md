# 对齐文档：MCP生产工厂

## 1. 原始需求分析
**用户指令**：“整理项目，我准备用该项目作为生产mcp应用程序的工厂”

**核心解读**：
用户希望将当前项目（`Try_make_mcp`）升级为一个通用的、标准化的“工厂”，用于批量、快速、高质量地生产 MCP (Model Context Protocol) 应用程序。

这不仅仅是写一个 MCP Server，而是构建一套**基础设施**和**工作流**。

## 2. 项目上下文理解 (Context Engineering)

### 2.1 现有资产分析
*   **代码库 (`src/`)**:
    *   `server.py`: Math & Time 基础示例，使用 `FastMCP`。
    *   `review_flow.py`: 复杂的 Review 流程状态机示例，展示了高级 MCP 用法。
    *   `client_demo.py`: 客户端连接示例。
*   **构建系统**:
    *   `build/`, `dist/`: 现有的 PyInstaller 打包产物。
    *   `.spec` 文件: 打包配置文件。
*   **文档体系 (`docs/`)**:
    *   严格遵循 **6A 工作流** (Align, Architect, Atomize, Approve, Automate, Assess)。
    *   已有多个子项目目录（`ReviewFlow`, `构建MCP服务`, `测试用例助手`）。

### 2.2 技术栈确认
*   **语言**: Python 3.10+
*   **核心库**: `mcp[cli]`, `pydantic`
*   **开发环境**: Windows, PowerShell, `.venv`
*   **打包工具**: PyInstaller

## 3. 目标与愿景 (Vision)
“MCP生产工厂”应该具备以下能力：
1.  **标准化脚手架**: 一键生成符合 6A 标准的新 MCP 项目结构（代码 + 文档）。
2.  **复用组件库**: 提取通用的 MCP 工具（如文件操作、Git操作、状态管理）供新项目复用。
3.  **统一构建流**: 通用的打包脚本，支持将任意 Python MCP 脚本打包为独立 exe。
4.  **质量控制**: 统一的测试框架和代码规范检查。

## 4. 识别的模糊点与假设 (Ambiguities & Assumptions)

### 4.1 模糊点
*   **“工厂”的具体形态**：是一个 CLI 工具（如 `mcp-factory create my-app`），还是一组文档规范 + 脚本集合？
    *   *假设*: 初期形态为“脚本集合 + 模板”，后期可封装为 CLI。
*   **多项目管理**：是在同一个 repo 下管理多个 MCP Server（Monorepo），还是“工厂”负责生成独立的新 repo？
    *   *假设*: 目前是在此 repo 下 Monorepo 管理（根据现有 `docs/` 结构判断）。

### 4.2 待确认决策
*   是否需要将通用的工具（如 6A 文档生成）封装为一个“管理型 MCP Server”？（即用 MCP 来生产 MCP）

## 5. 拟定执行计划 (Preliminary Plan)
1.  **结构重组**: 将现有的分散脚本整理为模块化的结构（例如 `src/apps/math_time`, `src/apps/review_flow`）。
2.  **基础设施建设**: 编写通用构建脚本 `scripts/build.py`，编写通用脚手架脚本 `scripts/scaffold.py`。
3.  **文档固化**: 将 6A 流程模板化，作为新项目的默认文档。
