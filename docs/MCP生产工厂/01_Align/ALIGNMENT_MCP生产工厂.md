# MCP生产工厂 - 需求对齐 (Align)

## 1. 项目背景
用户希望将当前的 MCP 制作流程（MCP Factory）封装为一个标准化的 MCP 服务。这将使得用户可以通过 MCP Client (如 Trae, Claude Desktop) 直接调用工具来创建、构建和验证新的 MCP 项目，实现“用 MCP 生产 MCP”的闭环。

## 2. 目标用户
*   **MCP 开发者**: 希望快速搭建新项目骨架。
*   **AI 助手 (如 Trae)**: 希望通过工具调用自动化地完成 MCP 的创建和交付。

## 3. 核心能力
本 MCP (`mcp_factory`) 将提供以下工具：

1.  **初始化项目 (`init_project`)**:
    *   创建符合 6A 标准的项目结构。
    *   生成代码骨架 (`server.py`, `config.json`)。
    *   生成文档模板 (`ALIGNMENT`, `DESIGN`, `TASK` 等)。
2.  **构建项目 (`build_project`)**:
    *   调用 PyInstaller 将 Python 代码打包为独立 EXE。
    *   自动处理依赖和隐藏导入。
3.  **验证项目 (`verify_project`)**:
    *   对构建出的 EXE 进行冒烟测试，验证 MCP 协议兼容性。
4.  **列出项目 (`list_projects`)**:
    *   查看当前工厂中已有的所有 App。

## 4. 依赖系统
*   **Python 环境**: 依赖当前项目的 `.venv` 环境。
*   **PyInstaller**: 用于打包。
*   **FileSystem**: 需要读写 `src/apps` 和 `docs/` 目录。
*   **Subprocess**: 需要执行系统命令进行打包和验证。

## 5. 核心约束
*   **工具复用**: 必须复用现有的 `src.factory` 下的 `init_app.py`, `build_app.py`, `verify_mcp.py` 逻辑，避免重复造轮子。
*   **路径感知**: 必须能够正确识别项目根目录，不受运行位置影响。
*   **异步兼容**: 构建过程可能耗时，需考虑是否需要异步或长轮询（当前版本暂定同步阻塞，因为 FastMCP 支持）。
