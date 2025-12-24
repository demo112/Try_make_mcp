# 需求对齐文档：完善 RAG Flow MCP 三层测试体系

## 1. 原始需求
用户要求“完善三层测试”，即建立包含单元测试、集成测试和系统/端到端测试的完整测试体系，以保障 `rag_flow_mcp` 的质量，特别是针对近期工具精简优化后的新架构。

## 2. 项目背景与理解
- **现状**: `rag_flow_mcp` 刚刚完成了工具精简，将细粒度的 CRUD 工具聚合为 `dataset_manage`, `document_manage`, `file_manage`。
- **现有测试**: `tests/` 目录下散落着一些测试文件 (`test_core_markdown.py`, `test_engine_logic.py` 等)，缺乏结构化，且可能未覆盖新的聚合工具逻辑。
- **目标**: 建立符合 6A 规范和用户要求的测试子系统。

## 3. 三层测试定义
1.  **单元测试 (Unit Tests)**:
    -   **对象**: `src/apps/rag_flow_mcp/tools/base_tools.py` (具体实现), `src/apps/rag_flow_mcp/server.py` (路由逻辑).
    -   **方法**: Mock 所有外部依赖 (RAGFlow API, File System)，只测试逻辑分支。
    -   **覆盖**: 确保每个 `action` (如 create, delete) 都能正确调用对应的底层函数。

2.  **集成测试 (Integration Tests)**:
    -   **对象**: `engines/` 模块与 `rag_client.py` 的交互。
    -   **方法**: Mock 外部 HTTP 请求 (使用 `requests_mock` 或类似工具)，但保留模块间的调用链路。验证数据在模块间的流转。

3.  **系统/端到端测试 (System/E2E Tests)**:
    -   **对象**: 整个 MCP Server 进程。
    -   **方法**: 启动 Server (作为子进程或异步任务)，使用 MCP Client (Python SDK) 发送真实请求，验证响应。
    -   **场景**: 模拟用户完整操作路径 (例如：创建数据集 -> 上传文档 -> 检索 -> 删除)。

## 4. 待确认问题 (Q&A)
- **Q**: 是否需要真实的 RAGFlow 环境？
  - **A**: 单元和集成测试不需要（使用 Mock）。E2E 测试理想情况下需要，但考虑到环境依赖复杂，初期可以使用 Mock Server 或记录/回放机制（VCR.py），或者仅在配置了真实 API Key 的环境中运行。为了通用性，我们将优先实现基于 Mock 的 E2E 测试。

## 5. 推荐方案
1.  **重构目录**: 将 `tests/` 划分为 `unit/`, `integration/`, `e2e/`。
2.  **迁移现有测试**: 将现有测试归类放入对应目录。
3.  **新增测试**:
    -   `test_dataset_manage.py`: 测试数据集聚合工具。
    -   `test_document_manage.py`: 测试文档聚合工具。
    -   `test_file_manage.py`: 测试文件聚合工具。
    -   `test_e2e_workflow.py`: 模拟完整工作流。
