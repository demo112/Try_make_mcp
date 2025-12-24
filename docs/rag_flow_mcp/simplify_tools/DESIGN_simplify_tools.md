# 设计：精简 RAG Flow MCP 工具 (Simplify Tools)

## 1. 架构变更 (Architecture Changes)

### 1.1 server.py 重构
*   **移除**: 大量细粒度的 `@mcp.tool` 装饰器。
*   **新增**: 3 个聚合工具的装饰器和函数实现。
*   **保留**: 业务逻辑工具 (`mcp_rag_flow_*`) 和高频基础工具 (`retrieve_chunks`, `rewrite_query`, `inspect_config`).

### 1.2 base_tools.py 重构
*   **现状**: `base_tools.py` 包含具体的实现函数，如 `create_dataset`, `delete_dataset` 等。
*   **变更**: 
    *   保持 `base_tools.py` 中的现有函数不变，作为原子实现。
    *   在 `server.py` 中编写聚合逻辑，调用 `base_tools.py` 中的原子函数。
    *   或者，在 `base_tools.py` 中添加 `manage_dataset` 等聚合函数，`server.py` 只做透传。
    *   **决策**: 在 `server.py` 中实现聚合逻辑，保持 `base_tools.py` 纯净（每个函数做一件事）。这样 `base_tools` 依然可以被其他模块（如 Engine）细粒度调用。

## 2. 接口设计 (Interface Design)

### 2.1 mcp_rag_base_dataset_manage
```python
@mcp.tool(name="mcp_rag_base_dataset_manage")
@log_tool_call
def dataset_manage(
    action: str, 
    id: str = None, 
    name: str = None, 
    description: str = None, 
    avatar: str = "",
    page: int = 1,
    page_size: int = 30
) -> str:
    """
    Manage Knowledge Bases (Datasets).
    
    Args:
        action: One of ['create', 'delete', 'update', 'list'].
        id: Dataset ID (required for delete/update).
        name: Dataset Name (required for create, optional for update).
        description: Description (optional for create/update).
        avatar: Avatar (optional for create).
        page: Page number (for list).
        page_size: Page size (for list).
    """
    if action == 'create':
        if not name: return error("name is required for create")
        return base_tools.create_dataset(name, avatar, description)
    elif action == 'delete':
        if not id: return error("id is required for delete")
        return base_tools.delete_dataset(id)
    elif action == 'update':
        if not id: return error("id is required for update")
        return base_tools.update_dataset(id, name, description)
    elif action == 'list':
        return base_tools.list_datasets(page, page_size)
    else:
        return error(f"Unknown action: {action}")
```

### 2.2 mcp_rag_base_document_manage
```python
@mcp.tool(name="mcp_rag_base_document_manage")
@log_tool_call
def document_manage(
    action: str,
    dataset_id: str,
    document_id: str = None,
    file_path: str = None,
    name: str = None,
    enabled: bool = None,
    keywords: str = "",
    page: int = 1,
    page_size: int = 30
) -> str:
    """
    Manage Documents in a Knowledge Base.
    
    Args:
        action: One of ['upload', 'delete', 'update', 'list', 'get_content'].
        dataset_id: Target Dataset ID (required for all).
        document_id: Document ID (required for delete/update/get_content).
        file_path: Local file path (required for upload).
        name: New name (optional for update).
        enabled: Enable/Disable (optional for update).
        keywords: Search keywords (optional for list).
        page: Page number (for list).
        page_size: Page size (for list).
    """
    # ... dispatch logic similar to dataset_manage ...
```

### 2.3 mcp_rag_base_file_manage
```python
@mcp.tool(name="mcp_rag_base_file_manage")
@log_tool_call
def file_manage(
    action: str,
    path: str,
    pattern: str = "*"
) -> str:
    """
    Local File System Operations.
    
    Args:
        action: One of ['read', 'list'].
        path: File path (for read) or Directory path (for list).
        pattern: Glob pattern (only for list).
    """
    # ... dispatch logic ...
```

## 3. 依赖关系
*   无新增依赖。
*   需要修改 `server.py` 的导入和注册部分。

