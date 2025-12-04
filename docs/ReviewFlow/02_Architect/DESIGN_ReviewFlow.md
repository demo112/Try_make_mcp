# DESIGN_ReviewFlow: 状态机架构设计

## 1. 系统架构图 (Mermaid)

```mermaid
graph TD
    Client[Client (Claude/Trae)] <-->|MCP Protocol| Server[ReviewFlow Server]
    Server <-->|Read/Write| FS[File System]
    Server <-->|Load/Save| StateDB[State JSON]
    
    subgraph StateMachine [状态机逻辑]
        IDLE -->|start_review| STAGE_0_INIT
        STAGE_0_INIT -->|submit| STAGE_1_ALIGN
        STAGE_1_ALIGN -->|submit| STAGE_2_ARCHITECT
        STAGE_2_ARCHITECT -->|submit| STAGE_3_ATOMIZE
        STAGE_3_ATOMIZE -->|submit| STAGE_4_APPROVE
        STAGE_4_APPROVE -->|submit| STAGE_5_AUTOMATE
        STAGE_5_AUTOMATE -->|submit| WAITING_FOR_HUMAN
        WAITING_FOR_HUMAN -->|check_human_input| STAGE_6_ASSESS
        STAGE_6_ASSESS -->|submit| STAGE_7_EXTEND
        STAGE_7_EXTEND -->|submit| COMPLETED
    end
```

## 2. 核心组件

### 2.1 StateManager (状态管理器)
- **职责**: 维护当前流程状态、项目名称、上下文数据。
- **数据结构**:
  ```python
  class ReviewState(str, Enum):
      IDLE = "IDLE"
      STAGE_0_INIT = "STAGE_0_INIT"
      STAGE_1_ALIGN = "STAGE_1_ALIGN"
      # ...
      WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
      # ...

  class ReviewContext(BaseModel):
      project_name: str
      current_state: ReviewState
      base_dir: str
      # 存储每个阶段的关键文件路径，用于验证
      deliverables: Dict[ReviewState, str] 
  ```
- **持久化**: 每次状态变更后自动保存到 `.review_flow_state.json`。

### 2.2 PromptEngine (提示词引擎)
- **职责**: 根据当前状态，返回对应的 `6a.md` 规则片段作为指令。
- **实现**: 将 `6a.md` 的内容按阶段拆分，`get_current_instruction` 工具根据状态返回对应的 Markdown 文本。

### 2.3 Validator (验证器)
- **职责**: 在 `submit_work` 时检查产出物是否符合要求。
- **规则**:
  - 文件是否存在
  - 文件大小是否 > 0
  - (进阶) 是否包含特定标题或关键字

## 3. MCP 工具接口设计

| 工具名称 | 参数 | 返回值 | 描述 |
| :--- | :--- | :--- | :--- |
| `start_review` | `project_name: str` | `str` | 初始化项目，进入 STAGE_0 |
| `get_current_instruction` | 无 | `str` | 获取当前阶段的任务指南 (Prompt) |
| `submit_work` | `proof_file: str` | `str` | 提交当前阶段成果，触发验证和状态流转 |
| `check_human_response` | `file_path: str` | `str` | (仅限等待阶段) 检查人工是否已填写回复 |

## 4. 交互流程示例 (Happy Path)

1. **User**: "开始评审项目 A"
2. **LLM**: 调用 `start_review("ProjectA")`
3. **Server**: 初始化目录，State -> STAGE_0_INIT
4. **LLM**: 调用 `get_current_instruction()`
5. **Server**: 返回 "请检查目录结构..."
6. **LLM**: 执行检查，调用 `submit_work("docs/ProjectA/Readme.md")`
7. **Server**: 验证通过，State -> STAGE_1_ALIGN
...
8. **Server**: State -> WAITING_FOR_HUMAN
9. **LLM**: 调用 `get_current_instruction()` -> "请等待用户填写 docs/.../06_xxx.md"
10. **User**: (在编辑器中填写回复)
11. **User**: "我填好了"
12. **LLM**: 调用 `check_human_response(...)`
13. **Server**: 验证有内容，State -> STAGE_6_ASSESS
