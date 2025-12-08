# 6A测试工作流助手 (six_a_test_workflow) 使用手册

## 1. 简介
本应用是一个 Model Context Protocol (MCP) Server，专为“6A工作流（测试用例编写版）”设计。它协助测试架构师和 AI 助手自动化管理测试文档、目录结构和测试用例。

## 2. 安装与运行
### 2.1 获取应用
请使用发布的 `six_a_test_workflow.exe`。

### 2.2 配置 MCP Client
在您的 Client 配置 (e.g. `claude_desktop_config.json`) 中添加：

```json
{
  "mcpServers": {
    "six_a_test_workflow": {
      "command": "D:/path/to/six_a_test_workflow.exe",
      "args": []
    }
  }
}
```

## 3. 功能列表 (Tools)

### 3.1 工作流管理
- **`init_feature_workflow(feature_name)`**: 初始化新特性的文档目录。
  - 示例: `init_feature_workflow("用户登录")`
- **`get_workflow_status(feature_name)`**: 检查各阶段文档状态。

### 3.2 文档操作
- **`save_stage_doc(feature_name, stage, doc_type, content)`**: 保存文档。
  - 示例: `save_stage_doc("用户登录", "01_Align", "ALIGNMENT", "# 需求...")`
- **`read_stage_doc(feature_name, stage, doc_type)`**: 读取文档。

### 3.3 测试用例
- **`append_test_case(...)`**: 追加测试用例到表格。
  - 参数: `module`, `sub_module`, `test_type`, `title`, `precondition`, `steps`, `expected_result`, `priority`
  - 结果: 自动写入 `docs/.../用例表格.md`。

## 4. 常见问题
- **目录在哪？**: 默认在 EXE 运行目录下的 `docs/` 文件夹中。请确保 EXE 有写入权限。
- **乱码？**: 所有文件使用 UTF-8 编码。
