# 1. 系统架构

本服务基于 `mcp` Python SDK (FastMCP) 构建，采用分层架构。

```mermaid
graph TD
    Client[MCP Client] -->|JSON-RPC| Server[Server Entry (server.py)]
    Server -->|Calls| Core[Core Logic]
    
    subgraph Core
        Workflow[Workflow Manager]
        Doc[Document Handler]
        TestCase[Test Case Manager]
    end
    
    Core -->|Read/Write| FS[File System]
```

# 2. 模块设计

## 2.1 Server (`server.py`)
- **职责**: 注册 MCP Tools，处理请求参数校验，调用 Core 层逻辑，处理异常并返回标准化错误。
- **依赖**: `fastmcp`, `src.common.logger`

## 2.2 Core Layer
### `core/workflow.py`
- **`init_workflow(feature_name: str)`**:
    - 校验 `feature_name` 合法性（避免非法字符）。
    - 构建路径 `docs/{feature_name}用例编写工作流/`。
    - 循环创建 `01_Align` 到 `06_Assess` 目录。
- **`get_status(feature_name: str)`**:
    - 遍历各阶段目录，检查关键文件是否存在。
    - 返回 Dict: `{ "01_Align": true, ... }`。

### `core/document.py`
- **`save_doc(feature_name, stage, doc_type, content)`**:
    - 映射 `stage` 到具体目录名（需处理 `01_Align` 等前缀）。
    - 构造文件名 `{doc_type}_{feature_name}.md`。
    - 写入文件。
- **`read_doc(...)`**: 读取文件内容。

### `core/test_case.py`
- **`append_case(feature_name, case_data)`**:
    - 定位 `docs/.../用例表格.md`。
    - 如果文件不存在，写入表头：`| 一级模块 | 二级模块 | ... |`。
    - 格式化 `case_data` 为 Markdown 表格行。
    - 追加写入。

# 3. 数据流
1. **初始化**: Client -> `init_feature_workflow` -> Workflow Manager -> Create Dirs -> Return Success.
2. **写用例**: Client -> `append_test_case` -> Test Case Manager -> Append File -> Return Success.

# 4. 异常处理
- **文件已存在**: `init` 时忽略或提示。
- **文件不存在**: 读取时抛出明确错误。
- **路径非法**: 试图访问 `docs/` 以外路径时拦截。
