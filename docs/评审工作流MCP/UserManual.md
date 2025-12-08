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
