# 1. 需求概述
构建 `six_a_test_workflow` MCP Server，作为测试架构师的智能助手，辅助执行 6A 测试用例编写工作流。

# 2. 交付物清单
1.  **源代码**: `src/apps/six_a_test_workflow/`
2.  **可执行文件**: `dist/six_a_test_workflow/six_a_test_workflow.exe`
3.  **文档**: 用户手册、配置说明。

# 3. 接口定义 (MCP Tools)

## 3.1 工作流管理
- **`init_feature_workflow`**
    - **描述**: 初始化指定特性的测试工作流目录结构。
    - **参数**:
        - `feature_name` (string): 特性名称，例如 "用户登录"。
    - **行为**: 创建 `docs/【feature_name】用例编写工作流/` 及 6A 子目录。

- **`get_workflow_status`**
    - **描述**: 获取指定特性工作流的执行状态（各阶段文档是否存在）。
    - **参数**:
        - `feature_name` (string): 特性名称。

## 3.2 文档操作
- **`save_stage_doc`**
    - **描述**: 保存指定阶段的标准文档。
    - **参数**:
        - `feature_name` (string): 特性名称。
        - `stage` (string): 阶段目录名 (e.g., "01_Align", "02_Architect").
        - `doc_type` (string): 文档类型前缀 (e.g., "ALIGNMENT", "DESIGN", "TASK").
        - `content` (string): Markdown 内容。
    - **行为**: 写入 `docs/.../{stage}/{doc_type}_{feature_name}.md`。

- **`read_stage_doc`**
    - **描述**: 读取指定阶段的文档。
    - **参数**:
        - `feature_name` (string)
        - `stage` (string)
        - `doc_type` (string)

## 3.3 测试用例管理
- **`append_test_case`**
    - **描述**: 向用例表格追加一条测试用例。
    - **参数**:
        - `feature_name` (string)
        - `test_case` (object): 包含以下字段:
            - `module` (一级模块)
            - `sub_module` (二级模块)
            - `test_type` (测试类型)
            - `title` (测试点标题)
            - `precondition` (前置条件)
            - `steps` (操作步骤)
            - `expected_result` (预期结果)
            - `priority` (重要性)
    - **行为**: 格式化为 Markdown 表格行，追加到 `docs/.../用例表格.md`。

# 4. 鉴权与安全
- 本地运行，无需额外鉴权。
- 路径限制：仅允许操作 `docs/` 目录下的文件，防止越权访问。

# 5. 技术栈
- Python 3.10+
- `mcp[cli]` (FastMCP)
- `pathlib` 用于路径操作
