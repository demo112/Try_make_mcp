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
