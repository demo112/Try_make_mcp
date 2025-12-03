# ReviewFlow: 状态机驱动的评审工作流

## 项目简介
本项目实现一个基于 MCP (Model Context Protocol) 的状态机服务 `ReviewFlow`，用于强制大模型（LLM）严格按照预定义的 6A 工作流执行方案评审任务。

## 核心理念
通过 MCP Tool 暴露状态机的“导航”和“验收”能力，将 LLM 从“自由发挥”的执行者转变为“受控”的执行者。

## 目录结构
- `src/review_flow.py`: MCP Server 核心实现
- `docs/`: 6A 工作流文档
