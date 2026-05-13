# 设计文档：RAG Flow MCP 测试体系架构

## 1. 目录结构设计

```
src/apps/rag_flow_mcp/tests/
├── conftest.py                   # 全局 Fixtures (Mock RAG Client, Env vars)
├── unit/                         # 单元测试
│   ├── conftest.py               # Unit 专用 Fixtures
│   ├── test_tool_dataset.py      # 测试 dataset_manage 路由与逻辑
│   ├── test_tool_document.py     # 测试 document_manage 路由与逻辑
│   ├── test_tool_file.py         # 测试 file_manage 路由与逻辑
│   └── test_core_logic.py        # (迁移) 原 test_engine_logic.py
├── integration/                  # 集成测试
│   ├── test_rag_flow.py          # 测试 Engine 到 RAG Client 的调用链路
│   └── test_governance.py        # (迁移) 原 test_engine_governance.py
└── e2e/                          # 端到端测试
    └── test_server_e2e.py        # 模拟 MCP Client 调用 Server
```

## 2. 关键测试策略

### 2.1 单元测试 (Unit)
- **目标**: 验证 `server.py` 中的聚合函数能否正确解析 `action` 参数并调用 `base_tools`。
- **Mock**: Patch `src.apps.rag_flow_mcp.tools.base_tools` 中的函数。
- **示例**:
  ```python
  @patch('src.apps.rag_flow_mcp.tools.base_tools.create_dataset')
  def test_dataset_create(mock_create):
      dataset_manage(action='create', name='test')
      mock_create.assert_called_with('test', '', None)
  ```

### 2.2 集成测试 (Integration)
- **目标**: 验证 `base_tools` -> `RAGClient` -> `requests` 的链路。
- **Mock**: 使用 `requests_mock` 拦截 HTTP 请求。
- **示例**:
  ```python
  def test_create_dataset_api(requests_mock):
      requests_mock.post('http://api/v1/dataset', json={'code': 0, 'data': {'id': '123'}})
      result = base_tools.create_dataset('test')
      assert '123' in result
  ```

### 2.3 E2E 测试 (System)
- **目标**: 验证 Server 启动及 MCP 协议交互。
- **Mock**: 使用 `mcp.server.fastmcp.FastMCP` 的测试接口，或者直接调用 `mcp.call_tool` (如果 FastMCP 暴露了该方法)，或者使用 `MCP Inspector` 的自动化模式（如果可行）。
- **FastMCP 测试方案**:
  FastMCP 提供了 `mcp.call_tool(name, arguments)` 方法（需确认 API），或者我们可以直接实例化 Server 对象并调用其内部注册的函数。为了更接近真实，我们将模拟 Client 行为。

## 3. 依赖管理
确保 `requirements.txt` 中包含:
- `pytest`
- `pytest-asyncio`
- `requests-mock`
- `pytest-cov` (可选，查看覆盖率)
