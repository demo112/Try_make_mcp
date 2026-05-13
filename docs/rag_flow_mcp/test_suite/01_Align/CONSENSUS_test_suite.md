# 共识文档：完善 RAG Flow MCP 三层测试体系

## 1. 核心共识
- **测试框架**: 使用 `pytest` 作为唯一测试框架。
- **目录结构**: 采用 `unit/`, `integration/`, `e2e/` 分层结构。
- **Mock 策略**:
    - 单元测试：Mock 内部函数调用和所有 I/O。
    - 集成测试：Mock 外部 HTTP API。
    - E2E 测试：模拟 Client 调用，Mock Server 内部的外部依赖（保持测试独立性）。
- **覆盖率目标**: 新增的聚合工具逻辑覆盖率 100%。

## 2. 交付物
- 重构后的 `tests/` 目录。
- 能够一键运行所有测试的命令 (`pytest src/apps/rag_flow_mcp/tests`).
- 测试运行报告。
