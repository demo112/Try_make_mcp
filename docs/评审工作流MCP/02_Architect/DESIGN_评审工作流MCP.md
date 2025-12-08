# DESIGN_评审工作流MCP

## 1. 系统架构

### 1.1 架构图 (Mermaid)

```mermaid
graph TD
    Client[MCP Client (Trae/Claude)] <-->|JSON-RPC| Server[MCP Server (FastMCP)]
    Server <--> Manager[WorkflowManager]
    Manager <-->|Read/Write| FS[File System]
    FS -- Stores --> Docs[Markdown Docs]
    FS -- Stores --> State[State JSON]
```

### 1.2 模块设计

#### A. `server.py`

- 入口文件。
- 定义 MCP Tools, Resources, Prompts。
- 依赖 `WorkflowManager` 处理业务逻辑。

#### B. `workflow_manager.py`

- **类 `WorkflowManager`**:
  - `__init__(root_path)`: 初始化根目录。
  - `init_project(name)`: 创建目录和初始状态。
  - `get_state(name)`: 读取状态。
  - `advance_stage(name)`: 状态流转逻辑。
  - `save_document(name, relative_path, content)`: 安全写文件。
  - `get_stage_rules(stage)`: 获取当前阶段的执行规则（Prompt片段）。

#### C. `models.py`

- Pydantic 模型定义。
- `WorkflowState`: 包含 `current_stage`, `project_name`, `updated_at` 等。
- `StageEnum`: 枚举所有阶段。

### 1.3 数据结构

**状态文件 (`workflow_state.json`)**:

```json
{
  "project_name": "DemoProject",
  "current_stage": "Align",
  "created_at": "2023-10-01T10:00:00",
  "updated_at": "2023-10-01T11:00:00",
  "documents": {
    "Align": ["01_Align/ALIGNMENT_DemoProject.md"],
    "Architect": []
  }
}
```

### 1.4 接口契约 (MCP Tools)

1. **`init_review(project_name: str) -> str`**

   - 创建 `docs/{project_name}/...` 目录。
   - 创建 `workflow_state.json`。
   - 返回成功消息。
2. **`get_current_state(project_name: str) -> str`**

   - 返回当前阶段、已完成文档、下一步建议。
3. **`save_document(project_name: str, stage: str, filename: str, content: str) -> str`**

   - 验证 `stage` 是否匹配当前状态（可选，或者允许修改历史）。
   - 写入文件。
4. **`advance_stage(project_name: str) -> str`**

   - 检查当前阶段必要文档是否存在。
   - 更新状态到下一阶段。

### 1.5 异常处理

- **FileExistsError**: 初始化同名项目时提示。
- **StageValidationError**: 缺少必要文档时拒绝流转。
- **ProjectNotFoundError**: 操作不存在的项目。

## 2. 设计原则

- **无状态 Server**: Server 本身不存状态，状态全在文件系统，重启不丢失。
- **兼容性**: 路径处理使用 `pathlib` 兼容 Windows/Linux。
- **鲁棒性**: 文件读写加锁（简化起见，单用户场景暂不加锁，但需异常捕获）。
