# 测试体系建设 Documentation


# Module: 测试体系建设


## Stage: 01_Align


### File: ALIGNMENT_测试体系.md

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


---

### File: CONSENSUS_测试体系.md

# 测试体系建设 - 达成共识 (Consensus)

## 1. 核心决策
*   **确认采用双重体系**：
    1.  **Factory Test**：保障生产工具的质量。
    2.  **MCP App Test SDK**：保障生产出来的产品的质量。
*   **技术选型**：
    *   测试框架：`pytest` (标准、插件丰富)。
    *   通信模拟：基于 `subprocess` 的 Stdio 管道交互。
    *   协议处理：手动构造 JSON-RPC 2.0 消息（保持轻量，不引入额外复杂的 MCP SDK 依赖，确保测试的独立性）。

## 2. 交付物清单
1.  **代码**：
    *   `src/testing/`: 包含 `client.py` (测试客户端) 和 `fixtures.py` (Pytest 夹具)。
    *   `tests/factory/`: 工厂自身的测试用例。
    *   `src/factory/init_app.py`: 更新后的模板，包含 `tests/` 目录生成逻辑。
2.  **文档**：
    *   更新 `MCP_FACTORY_MANUAL.md`，增加“测试指南”章节。

## 3. 验收标准
*   **Factory Test**：
    *   运行 `pytest tests/factory` 全部通过。
    *   能够模拟创建一个临时 APP 并成功通过构建检查。
*   **MCP App Test**：
    *   新创建的 APP (`init_app`) 自带 `tests/test_server.py`。
    *   运行 `pytest src/apps/new_app` 能通过默认的 `hello_world` 测试。
    *   测试框架能正确处理 `initialize`, `tools/list`, `tools/call` 流程。


---

## Stage: 02_Architect


### File: DESIGN_测试体系.md

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


---

## Stage: 03_Atomize


### File: TASK_测试体系.md

# 测试体系建设 - 任务拆解 (Atomize)

## 1. 任务清单

- [ ] **Task 1: 实现 MCP 测试 SDK (System B)**
    - 创建 `src/testing/` 目录。
    - 实现 `src/testing/client.py` (`McpTestClient` 类)。
    - 实现 `src/testing/fixtures.py` (Pytest fixtures)。
- [ ] **Task 2: 更新工厂初始化逻辑 (System B Integration)**
    - 修改 `src/factory/init_app.py`。
    - 增加 `TEST_TEMPLATE` 和 `CONFTEST_TEMPLATE`。
    - 在 `create_app` 中增加生成 `tests/` 目录及文件的逻辑。
- [ ] **Task 3: 实现工厂自身测试 (System A)**
    - 创建项目根目录 `tests/factory/`。
    - 创建 `pytest.ini` 配置 python path。
    - 编写 `tests/factory/test_init_app.py` (测试 APP 生成)。
- [ ] **Task 4: 验证与交付**
    - 运行 `pytest tests/factory` 验证工厂测试。
    - 运行 `python -m src.factory.init_app auto_test_demo "自动测试演示"`。
    - 运行 `pytest src/apps/auto_test_demo` 验证生成的 APP 测试是否通过。
    - 清理 `auto_test_demo`。

## 2. 依赖关系
Task 1 -> Task 2 -> Task 3 -> Task 4


---

## Stage: 06_Assess


### File: FINAL_测试体系.md

# 测试体系建设 - 项目总结 (Final)

## 1. 交付成果
我们成功构建了双重自动化测试体系，满足了项目质量保障的需求。

### 1.1 体系 A：工厂自动化测试 (Factory Test System)
*   **位置**: `tests/factory/`
*   **内容**: 包含 `test_init_app.py`，用于验证 `create_app` 逻辑是否正确生成文件结构。
*   **运行**: 在根目录运行 `pytest tests/factory`。

### 1.2 体系 B：MCP 应用测试框架 (MCP App Test Framework)
*   **位置**: `src/testing/`
*   **组件**:
    *   `client.McpTestClient`: 封装了基于 Stdio 的 JSON-RPC 交互逻辑。
    *   `fixtures.mcp_client`: Pytest 夹具，自动启动 Server 并注入 Client。
*   **集成**: `init_app.py` 已更新，新创建的 APP 会自动包含 `tests/` 目录和示例用例。

## 2. 验证结果
*   [x] **工厂测试通过**: `tests/factory/test_init_app.py` 运行成功。
*   [x] **生成的 APP 测试通过**: 创建 `auto_test_demo` 并运行其内置测试，验证了 SDK 的有效性。

## 3. 使用指南
### 3.1 测试工厂
```bash
pytest tests/factory
```

### 3.2 测试 MCP 应用
对于新生成的应用 (如 `my_app`)：
```bash
pytest src/apps/my_app
```

### 3.3 为旧应用添加测试
对于旧应用，请手动创建 `tests/` 目录，并参考 `src/factory/init_app.py` 中的 `TEST_TEMPLATE` 添加测试文件。

## 4. 后续规划 (TODO)
*   [ ] 为现有的核心 APP (`rag_flow_mcp` 等) 补全测试用例。
*   [ ] 集成 GitHub Actions CI。
*   [ ] 扩展 `McpTestClient` 以支持更复杂的 MCP 功能 (如 Sampling, Roots)。


---
