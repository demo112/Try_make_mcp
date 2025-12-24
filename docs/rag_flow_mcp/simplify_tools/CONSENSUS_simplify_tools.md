# 共识：精简 RAG Flow MCP 工具 (Simplify Tools)

## 1. 核心决策 (Core Decisions)
*   **采纳策略**: 全面执行“合并 CRUD”与“隐藏原子工具”策略。
*   **工具数量目标**: 控制在 15 个以内。
*   **兼容性**: 不保留旧工具名，这是一次 Breaking Change，需同步更新文档。

## 2. 新工具定义 (New Tool Definitions)

### 2.1 mcp_rag_base_dataset_manage
*   **Action**: `create`, `delete`, `update`, `list`
*   **Args**:
    *   `action`: required, enum.
    *   `id`: optional (for delete/update).
    *   `name`: optional (for create/update).
    *   `description`: optional (for create/update).
    *   `avatar`: optional (for create).
    *   `page`, `page_size`: optional (for list).

### 2.2 mcp_rag_base_document_manage
*   **Action**: `upload`, `delete`, `update`, `list`, `get_content`
*   **Args**:
    *   `action`: required, enum.
    *   `dataset_id`: required (for all).
    *   `document_id`: optional (for delete/update/get_content).
    *   `file_path`: optional (for upload).
    *   `name`: optional (for update).
    *   `enabled`: optional (for update).
    *   `keywords`: optional (for list).
    *   `page`, `page_size`: optional (for list).

### 2.3 mcp_rag_base_file_manage
*   **Action**: `read`, `list`
*   **Args**:
    *   `action`: required, enum.
    *   `path`: required (file path or dir path).
    *   `pattern`: optional (for list).

## 3. 移除列表 (Removal List)
*   `mcp_rag_base_create_dataset` ... (等 4 个)
*   `mcp_rag_base_upload_document` ... (等 5 个)
*   `mcp_rag_base_read_file`, `mcp_rag_base_list_files`
*   `mcp_rag_base_fill_clarification_suggestions_controller`
*   `mcp_rag_base_create_shadow_file`
*   `mcp_rag_base_extract_questions_from_doc`
*   `mcp_rag_base_retrieve_rag_suggestion`
*   `mcp_rag_base_apply_suggestions_to_doc`

## 4. 验收标准 (Acceptance Criteria)
1.  `server.py` 中注册的工具数量大幅减少。
2.  使用 MCP Inspector 验证新合并的工具 (`dataset_manage`, `document_manage`, `file_manage`) 功能正常。
3.  业务流程（如“填充澄清建议”）不受影响（因为它们使用 `mcp_rag_flow_*`）。
