# 测试体系建设 - 架构设计 (Architect)

## 1. 整体架构图

```mermaid
graph TD
    subgraph "System A: Factory Tests"
        FT[Factory Tests] --> |Test| Init[init_app.py]
        FT --> |Test| Build[build_app.py]
        FT --> |Test| Verify[verify_mcp.py]
    end

    subgraph "System B: MCP Test SDK"
        SDK[src.testing]
        Client[McpTestClient] --> |Spawn| MCP[MCP Process (Stdio)]
        Client --> |JSON-RPC| MCP
        Fixture[Pytest Fixture] --> |Manage| Client
    end

    subgraph "Target App"
        AppTests[src/apps/xxx/tests] --> |Use| SDK
    end
```

## 2. 模块设计

### 2.1 `src.testing` 模块
这是核心的共享库，供所有 MCP APP 的测试使用。

#### `client.py` - McpTestClient
封装与 MCP Server 的 Stdio 交互。

```python
class McpTestClient:
    def __init__(self, command: List[str], env: Dict[str, str] = None):
        """
        初始化客户端
        :param command: 启动命令，如 ["python", "server.py"] 或 ["./app.exe"]
        :param env: 环境变量
        """
        pass

    def start(self):
        """启动子进程"""
        pass

    def stop(self):
        """停止子进程"""
        pass

    def send_request(self, method: str, params: Dict = None, timeout: float = 5.0) -> Dict:
        """发送 JSON-RPC 请求并等待响应"""
        pass

    def initialize(self) -> Dict:
        """发送 initialize 和 initialized 握手"""
        pass

    def list_tools(self) -> List[Dict]:
        """调用 tools/list 并返回工具列表"""
        pass

    def call_tool(self, name: str, arguments: Dict = None) -> Any:
        """调用 tools/call 并返回结果内容"""
        pass
```

#### `fixtures.py` - Pytest Fixtures
提供开箱即用的 Pytest 夹具。

```python
@pytest.fixture
def mcp_server(request):
    """
    启动当前 APP 的 Server。
    自动查找当前目录下的 server.py 或根据配置启动。
    """
    pass
```

### 2.2 工厂测试设计 (`tests/factory`)
*   `test_init_app.py`:
    *   创建一个临时目录。
    *   调用 `create_app`。
    *   断言文件结构 (`server.py`, `tests/`, `docs/`) 是否存在。
    *   断言 `server.py` 内容是否包含模板代码。
*   `test_verify.py`:
    *   Mock 一个 subprocess。
    *   验证 `verify_mcp` 的逻辑。

## 3. 模板更新 (`init_app.py`)
需要更新 `SERVER_TEMPLATE` 之外，新增 `TEST_TEMPLATE`。

```python
TEST_TEMPLATE = """import pytest
from src.testing.client import McpTestClient

def test_tool_list(mcp_client: McpTestClient):
    tools = mcp_client.list_tools()
    names = [t["name"] for t in tools]
    assert "hello_world" in names

def test_hello_world(mcp_client: McpTestClient):
    result = mcp_client.call_tool("hello_world")
    assert "Hello" in result
"""
```

并在 `create_app` 函数中生成 `tests/test_server.py` 和 `tests/conftest.py`。

## 4. 目录结构变更
```text
Try_make_mcp/
├── src/
│   ├── testing/          # [NEW] 测试 SDK
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── fixtures.py
│   └── factory/
│       └── init_app.py   # [UPDATE] 包含测试生成逻辑
├── tests/                # [NEW] 工厂自身测试
│   ├── factory/
│   │   └── test_init_app.py
│   └── conftest.py
└── pytest.ini            # [NEW] Pytest 配置
```
