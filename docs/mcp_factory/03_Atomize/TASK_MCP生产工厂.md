# MCP生产工厂 - 任务拆解 (Atomize)

## 1. 任务清单
- [x] **Task 1**: 初始化 `mcp_factory` 应用结构
    - 创建 `src/apps/mcp_factory` 目录
    - 创建 `src/apps/mcp_factory/__init__.py`
    - 创建 `config.json`
- [x] **Task 2**: 实现 `server.py` 基础框架
    - 引入 `FastMCP`
    - 配置 Logger
- [x] **Task 3**: 实现 `list_projects` 工具
    - 扫描 `src/apps`
    - 返回 JSON 列表
- [x] **Task 4**: 实现 `init_project` 工具
    - 封装 `src.factory.init_app`
    - 捕获输出并返回
- [x] **Task 5**: 实现 `build_project` 工具
    - 封装 `src.factory.build_app`
    - 捕获输出并返回
- [x] **Task 6**: 实现 `verify_project` 工具
    - 调用 `src.factory.verify_mcp` (subprocess)
    - 返回验证结果
- [x] **Task 7**: 验证与交付
    - 运行 Inspector 测试所有工具
    - 更新 `CONSENSUS` 和 `ACCEPTANCE` 文档
    - 补充 `UserManual.md`
    - 构建 `mcp_factory` 自身

## 2. 依赖关系
Task 1 -> Task 2 -> Task 3 -> Task 4 -> Task 5 -> Task 6 -> Task 7
