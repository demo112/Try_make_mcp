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
