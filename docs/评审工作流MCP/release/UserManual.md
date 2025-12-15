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
