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
