# TASK_评审工作流MCP

## 1. 任务清单

### T1: 基础结构搭建
- [x] 创建 `src/apps/review_workflow_mcp/core/` 目录。
- [x] 创建 `__init__.py`。

### T2: 数据模型实现 (`models.py`)
- [x] 定义 `StageEnum` (Init, Align, Architect, Atomize, Approve, Automate, Assess, Extend, Done)。
- [x] 定义 `WorkflowState` Pydantic 模型。

### T3: 核心逻辑实现 (`workflow_manager.py`)
- [x] 实现 `init_project`: 创建目录和状态文件。
- [x] 实现 `load_state` / `save_state`。
- [x] 实现 `advance_stage`: 状态流转控制。
- [x] 实现 `save_document`: 路径检查与写入。

### T4: Server 实现 (`server.py`)
- [x] 定义 MCP 实例。
- [x] 实现 `init_review` Tool。
- [x] 实现 `get_current_state` Tool。
- [x] 实现 `advance_stage` Tool。
- [x] 实现 `save_document` Tool。
- [x] 实现 `review_workflow` Prompt (注入角色和当前状态)。

### T5: 验证与构建
- [ ] 使用 Inspector 验证 Tools。
- [ ] 模拟完整流程测试。
- [ ] 构建 EXE。

## 2. 依赖关系
T1 -> T2 -> T3 -> T4 -> T5
