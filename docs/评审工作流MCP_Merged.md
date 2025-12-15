# 评审工作流MCP Documentation


# Module: 评审工作流MCP


## Stage: 01_Align


### File: ALIGNMENT_评审工作流MCP.md

# ALIGNMENT_评审工作流MCP

## 1. 业务上下文分析

### 1.1 原始需求
用户希望将“评审工作流”（6A工作流）封装为一个 MCP Server，目的是“控制大模型按照规定的工作流稳定可靠的完成任务”。

### 1.2 核心痛点
- 大模型在执行复杂任务时容易发散，缺乏严谨的步骤控制。
- 评审过程需要产生大量标准文档，手动管理繁琐且易出错。
- 缺乏状态记忆，难以保证从“对齐”到“评估”的连贯性。

### 1.3 业务实体
- **Workflow (工作流)**: 整个评审过程的生命周期管理。
- **Stage (阶段)**: 6A 的各个阶段 (Align, Architect, Atomize, Approve, Automate, Assess, Extend)。
- **Document (文档)**: 每个阶段产出的 Markdown 文件（如 ALIGNMENT_xxx.md, DESIGN_xxx.md）。
- **Checklist (检查项)**: 每个阶段的质量门控标准。
- **Task (任务)**: 评审中的具体原子任务。

## 2. 需求理解与共识

### 2.1 核心能力 (Core Capabilities)
本 MCP Server 将作为“流程向导”和“执行工具箱”，提供以下能力：

1.  **工作流状态管理 (State Management)**
    - 初始化工作流。
    - 记录当前所处阶段。
    - 验证前置条件，控制阶段流转（只有通过质量门控才能进入下一阶段）。

2.  **标准化文档操作 (Document Operations)**
    - 提供模板化的文档创建工具。
    - 读取和更新特定阶段的文档。
    - 自动维护文档目录结构。

3.  **质量门控 (Quality Gates)**
    - 提供工具让 LLM 确认当前阶段的 Checklist。
    - 记录审批状态。

4.  **上下文引导 (Context Guidance)**
    - 提供 `get_current_step` 工具，告诉 LLM 当前应该做什么，下一步做什么。
    - 注入当前阶段所需的系统提示词或规则。

### 2.2 目标用户
- 使用 Trae 或 Claude Desktop 的开发者。
- 希望让 AI 辅助完成系统化设计和评审的架构师/PM。

### 2.3 依赖系统
- **本地文件系统**: 用于存储生成的 Markdown 文档。
- **Python 环境**: 运行 MCP Server。

## 3. 关键决策点 (Key Decisions)

- **Q: MCP 是被动工具还是主动代理？**
  - A: MCP 本质是工具集合。但我们将设计 `get_next_instruction` 类型的工具，让 LLM 在每一轮对话中主动查询“我现在该干什么”，从而实现“控制”的效果。
- **Q: 状态存储在哪里？**
  - A: 状态应持久化存储，建议使用本地 JSON 文件 (`workflow_state.json`) 存储在文档目录下，以便跨会话记忆。
- **Q: 如何处理多轮评审？**
  - A: 文件命名支持版本或覆盖，状态机应支持“驳回”或“重来”。

## 4. 待澄清事项
- 无。


---

### File: CONSENSUS_评审工作流MCP.md

# CONSENSUS_评审工作流MCP

## 1. 方案概述
构建一个名为 `review_workflow_mcp` 的 MCP Server，用于强制执行 6A 评审工作流。它通过提供状态管理、文档模板和流程引导工具，确保 LLM 严格遵循规范。

## 2. 系统边界
- **输入**: 用户自然语言指令，项目名称。
- **输出**: Markdown 文档（存储在本地），流程状态更新，下一步指引。
- **范围**: 覆盖从 Initialization 到 Assess (及 Extend) 的全生命周期。

## 3. 详细规格

### 3.1 鉴权与配置
- 无需远程鉴权，本地运行。
- 配置：根目录路径（默认为当前工作区）。

### 3.2 核心功能定义

#### A. 状态机 (State Machine)
维护每个项目的当前阶段：
`Init -> Align -> Architect -> Atomize -> Approve -> Automate -> Assess -> (Extend) -> Done`

#### B. 工具集 (Tools)

| 工具名称 | 描述 | 输入参数 |
| :--- | :--- | :--- |
| `init_review` | 初始化评审项目，创建目录结构 | `project_name` |
| `get_current_state` | 获取当前阶段和待办事项 | `project_name` |
| `advance_stage` | 完成当前阶段，进入下一阶段 | `project_name`, `confirmation` |
| `save_document` | 保存/更新指定阶段的文档 | `project_name`, `stage`, `filename`, `content` |
| `read_project_files` | 读取项目下的文档 | `project_name`, `filename` (optional) |
| `check_quality_gate` | 验证当前阶段的质量门控 | `project_name`, `stage`, `checklist_items` |

#### C. 资源 (Resources)
- `review://{project_name}/state`: 实时获取项目状态 JSON。
- `review://{project_name}/docs/{filename}`: 实时获取文档内容。

#### D. 提示词 (Prompts)
- `activate_reviewer`: 激活评审专家角色。包含：
    - 当前项目状态。
    - 当前阶段的详细执行规则（从原文动态加载）。
    - 角色设定（资深业务分析师）。

## 4. 交付物
- 源代码 (`src/apps/review_workflow_mcp/`)
- 可执行文件 (`review_workflow_mcp.exe`)
- 使用文档 (`UserManual.md`)

## 5. 验收标准
1.  能够通过 MCP 工具成功初始化一个新评审项目。
2.  能够按顺序完成所有 6A 阶段，并且每个阶段都产出正确命名的文档。
3.  未完成当前阶段任务时，拒绝进入下一阶段（软限制或提示）。
4.  生成的文档结构符合《评审工作流原文》规范。


---

## Stage: 02_Architect


### File: DESIGN_评审工作流MCP.md

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


---

## Stage: 03_Atomize


### File: TASK_评审工作流MCP.md

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


---

## Stage: 04_Approve


### File: CHECKLIST_评审工作流MCP.md

# CHECKLIST_评审工作流MCP

## 1. 完整性检查
- [x] 覆盖了从 Init 到 Assess 的所有阶段。
- [x] 包含了状态管理机制。
- [x] 定义了必要的 MCP Tools。

## 2. 安全性检查
- [x] **路径遍历风险**: `save_document` 必须检查路径是否在项目目录下。
- [ ] **API Key**: 本项目不涉及外部 API Key，安全。

## 3. 可维护性检查
- [x] 代码结构分层 (`core` vs `server`)。
- [x] 使用 Pydantic 进行类型验证。

## 4. 交付标准
- [x] 包含 Dockerfile (虽然主要是本地 EXE，但 Factory 模板自带)。
- [x] 文档结构完整。

## 5. 待确认
- 无。


---

## Stage: 05_Automate


### File: ACCEPTANCE_评审工作流MCP.md

# ACCEPTANCE_评审工作流MCP

## 1. 功能验证
- [x] **初始化**: `init_review` 成功创建项目目录结构和状态文件。
- [x] **状态获取**: `get_current_state` 返回正确的 JSON 状态。
- [x] **状态流转**: `advance_stage` 更新状态到下一阶段。
- [x] **文档保存**: `save_review_document` 成功写入文件并更新状态记录。
- [x] **Prompt**: `review_assistant` 正确注入当前上下文。

## 2. 代码质量
- [x] 模块化设计 (`core` + `server`)。
- [x] 异常处理覆盖主要路径。
- [x] 无硬编码路径。

## 3. 交付物确认
- [x] 源代码完整。
- [x] 文档结构完整。

## 4. 结论
项目符合需求，准备交付。


---

## Stage: 06_Assess


### File: FINAL_评审工作流MCP.md

# FINAL_评审工作流MCP

## 1. 项目概况
本项目成功将《评审工作流》封装为 MCP Server，实现了流程的标准化、自动化和状态化管理。

## 2. 核心成果
- **WorkflowManager**: 实现了基于文件系统的状态机。
- **MCP Server**: 提供了完整的工具链（Init, GetState, Advance, SaveDoc）。
- **Prompt Engineering**: 通过 `review_assistant` 动态注入上下文，增强了 LLM 的依从性。
- **Build Success**: 成功构建为独立 EXE (`dist/review_workflow_mcp.exe`)，并通过了自动化冒烟测试。

## 3. 遗留风险
- 目前状态流转仅做软限制，未强制检查特定文件内容。
- 并发写文件可能存在冲突（但在单人评审场景下风险较低）。

## 4. 交付物
- 源代码: `src/apps/review_workflow_mcp/`
- 文档: `docs/评审工作流MCP/` (已合并旧 `ReviewFlow` 目录，统一使用中文命名)
- 用户手册: `docs/评审工作流MCP/UserManual.md`
- 发布包: `dist/review_workflow_mcp_vlatest.zip`

## 5. 结论
项目已达到交付标准，可投入使用。


---

### File: TODO_评审工作流MCP.md

# TODO_评审工作流MCP

## 1. 待办事项
- [ ] **增强校验**: 在 `advance_stage` 中增加对关键文档（如 ALIGNMENT, DESIGN）的强制存在性检查。
- [ ] **动态规则**: 解析 `评审工作流原文.md`，自动提取每个阶段的 Prompt 规则，而不是硬编码。
- [ ] **多项目支持**: 优化文件存储结构，支持子目录隔离更彻底。
- [ ] **Web UI**: 提供一个简单的可视化界面查看状态（虽然 MCP Client 也可以）。

## 2. 建议
- 建议在下一版本中优先实现“动态规则解析”，以提高系统的灵活性。


---

## Stage: Others


### File: Readme.md

# 评审工作流MCP

## 简介
这是基于 6A 评审工作流规范构建的 MCP Server。

## 6A 工作流
- [x] 01_Align
- [x] 02_Architect
- [x] 03_Atomize
- [x] 04_Approve
- [x] 05_Automate
- [x] 06_Assess

## 资源
- [原文规范](评审工作流原文.md)
- [使用手册](UserManual.md)


---

### File: UserManual.md

# 评审工作流MCP 用户手册

## 1. 简介
ReviewFlow 是一个基于 MCP 的状态机服务，用于强制引导大模型按照 6A 工作流执行方案评审。它不直接生成文档，而是作为“导航员”和“检查员”，确保大模型（执行者）不偏离航线。

## 2. 安装与配置 (Trae)

请在 Trae 的 MCP 配置文件中添加以下内容：

### 方式 A: 使用源码 (推荐开发调试)
```json
{
  "mcpServers": {
    "review-workflow": {
      "command": "c:\\Users\\Administrator\\Documents\\trae_projects\\Try_make_mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "c:\\Users\\Administrator\\Documents\\trae_projects\\Try_make_mcp\\src\\apps\\review_workflow_mcp\\server.py"
      ]
    }
  }
}
```

### 方式 B: 使用 EXE (推荐离线部署)
```json
{
  "mcpServers": {
    "review-workflow": {
      "command": "c:\\Users\\Administrator\\Documents\\trae_projects\\Try_make_mcp\\dist\\review_workflow_mcp.exe",
      "args": []
    }
  }
}
```

## 3. 使用指南

### 第一步：启动
在对话框中输入：
> 请启动评审工作流，项目名称为 "用户中心重构"

### 第二步：执行循环
大模型会自动执行以下循环：
1. 调用 `get_current_state` 获取当前阶段状态。
2. 调用 `review_assistant` 获取当前阶段的执行指令（Prompt）。
3. 大模型利用自身能力读取需求、分析、调用 `save_review_document` 写入文件。
4. 大模型调用 `advance_stage` 推进到下一阶段。

### 第三步：人工介入
当流程需要人工确认时（如 Approve 阶段）：
1. 用户检查生成的文档。
2. 用户在对话中给予反馈或确认。
3. 大模型根据反馈修改或调用 `advance_stage` 继续。

## 4. 状态流转图
`INIT` -> `ALIGN` -> `ARCHITECT` -> `ATOMIZE` -> `APPROVE` -> `AUTOMATE` -> `ASSESS` -> `EXTEND` -> `DONE`


---

### File: config.json

{
    "log_level": "INFO",
    "custom_message": "Hello from config.json!"
}

---

### File: UserManual.md

# 评审工作流MCP (Review Workflow MCP) 使用手册

## 1. 简介
本 MCP Server 旨在强制执行 6A 评审工作流，帮助大模型稳定可靠地完成任务。

## 2. 快速开始

### 2.1 安装
确保已安装 Python 3.10+。
运行发布包中的 EXE 或通过源码运行：
```bash
python -m src.apps.review_workflow_mcp.server
```

### 2.2 Client 配置 (Claude Desktop / Trae)
```json
{
  "mcpServers": {
    "review_workflow": {
      "command": "python",
      "args": ["-m", "src.apps.review_workflow_mcp.server"]
    }
  }
}
```

## 3. 使用指南

### 3.1 启动新评审
在对话中告诉 AI：“初始化评审项目 [项目名称]”。
AI 将调用 `init_review`。

### 3.2 执行流程
1.  **激活角色**: AI 会调用 `review_assistant` Prompt 获取当前状态和规则。
2.  **创建文档**: AI 根据规则调用 `save_review_document` 创建 `ALIGNMENT` 等文档。
3.  **流转状态**: 当文档齐备，AI 调用 `advance_stage` 进入下一阶段。

### 3.3 常用指令
- "检查当前状态" -> `get_current_state`
- "列出所有文件" -> `list_project_files`

## 4. 故障排查
- 如果提示“项目不存在”，请先运行初始化。
- 如果文件保存失败，检查路径是否包含非法字符。


---
