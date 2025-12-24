# 任务拆解：完善 RAG Flow MCP 三层测试体系

## 任务清单

### T1: 环境与目录重构
- [ ] 创建 `tests/unit`, `tests/integration`, `tests/e2e` 目录。
- [ ] 迁移现有测试文件到对应目录。
- [ ] 创建 `tests/conftest.py` 配置通用 Fixtures。

### T2: 单元测试实现 (聚合工具)
- [ ] 实现 `unit/test_tool_dataset.py`: 覆盖 create, delete, update, list。
- [ ] 实现 `unit/test_tool_document.py`: 覆盖 upload, delete, update, list, get_content。
- [ ] 实现 `unit/test_tool_file.py`: 覆盖 read, list。

### T3: 集成测试实现
- [ ] 实现 `integration/test_rag_flow.py`: 验证 base_tools 与 RAGClient 的交互。

### T4: E2E 测试实现
- [ ] 实现 `e2e/test_server_e2e.py`: 模拟完整调用链路。

### T5: 执行与修复
- [ ] 运行所有测试，确保通过率 100%。
- [ ] 生成测试报告。
