# 需求对齐：精简 RAG Flow MCP 工具 (Simplify Tools)

## 1. 背景与目标 (Context & Goal)
*   **背景**: 用户反馈 `rag_flow_mcp` 暴露的工具数量过多 (约 25+)，导致 Agent 选择困难，且存在功能重叠和颗粒度过细的问题。
*   **目标**: 在不影响现有业务功能的前提下，通过合并、隐藏、重构等手段，大幅减少暴露给 MCP Client 的工具数量，提升可用性。
*   **约束**: 必须保留核心业务能力 (6A 流程支持) 和基础管理能力 (CRUD)。

## 2. 现状分析 (Current State Analysis)
当前 `server.py` 注册了以下几类工具：

### 2.1 逻辑工具 (Logic Tools - High Level)
*   `mcp_rag_flow_fill_clarification_suggestions`: 核心主线。
*   `mcp_rag_flow_evolve_scheme_document`: 核心主线。
*   `mcp_rag_flow_check_metadata_compliance`: 治理 (暂未完全启用)。
*   `mcp_rag_flow_validate_knowledge_conflict`: 治理 (暂未完全启用)。
*   `mcp_rag_flow_harvest_knowledge_candidates`: 生命周期 (暂未完全启用)。
*   `mcp_rag_flow_promote_knowledge`: 生命周期 (暂未完全启用)。
*   `mcp_rag_flow_view_diff`: 辅助工具。
*   `mcp_rag_flow_add_test_case`: 辅助工具。

### 2.2 实施工具 (Implementation Tools - Low Level)
*   **Dataset CRUD**: `create`, `delete`, `list`, `update` (4个工具)。
*   **Document CRUD**: `upload`, `delete`, `update`, `get_content`, `list` (5个工具)。
*   **Retrieval**: `retrieve_chunks`, `rewrite_query` (2个工具)。
*   **File Ops**: `read_file`, `list_files` (2个工具)。
*   **System**: `inspect_config` (1个工具)。

### 2.3 原子工具 (Atomic Tools - Internal Details)
*   `mcp_rag_base_fill_clarification_suggestions_controller`: 与 Logic 工具重复。
*   `mcp_rag_base_create_shadow_file`: 内部步骤。
*   `mcp_rag_base_extract_questions_from_doc`: 内部步骤。
*   `mcp_rag_base_retrieve_rag_suggestion`: 内部步骤。
*   `mcp_rag_base_apply_suggestions_to_doc`: 内部步骤。

**总计**: 约 25 个工具。

## 3. 优化策略 (Optimization Strategy)

### 3.1 策略一：合并 CRUD 工具 (Consolidation)
将 CRUD 操作合并为单一入口工具，通过 `action` 参数区分。
*   **Dataset Management**: 合并 `create/delete/update/list` -> `mcp_rag_base_dataset_manage(action, ...)`。
*   **Document Management**: 合并 `upload/delete/update/list/get` -> `mcp_rag_base_document_manage(action, ...)`。
*   **File Operations**: 合并 `read/list` -> `mcp_rag_base_file_manage(action, ...)`。

### 3.2 策略二：隐藏原子工具 (Hide Internals)
原子工具主要用于 Logic 工具的内部步骤或开发调试，普通用户/Agent 无需直接调用。
*   **移除注册**: 在 `server.py` 中移除以下工具的注册：
    *   `mcp_rag_base_fill_clarification_suggestions_controller` (完全冗余)。
    *   `mcp_rag_base_create_shadow_file`
    *   `mcp_rag_base_extract_questions_from_doc`
    *   `mcp_rag_base_retrieve_rag_suggestion`
    *   `mcp_rag_base_apply_suggestions_to_doc`

### 3.3 策略三：保留核心与高频工具
*   保留所有 `mcp_rag_flow_*` 工具（业务主入口）。
*   保留 `mcp_rag_base_retrieve_chunks` (高频检索)。
*   保留 `mcp_rag_base_rewrite_query` (辅助检索)。
*   保留 `mcp_rag_base_inspect_config` (系统诊断)。

## 4. 预期效果 (Expected Outcome)
优化后工具列表将精简至 **10-12** 个左右：
1.  `mcp_rag_flow_fill_clarification_suggestions`
2.  `mcp_rag_flow_evolve_scheme_document`
3.  `mcp_rag_flow_check_metadata_compliance`
4.  `mcp_rag_flow_validate_knowledge_conflict`
5.  `mcp_rag_flow_harvest_knowledge_candidates`
6.  `mcp_rag_flow_promote_knowledge`
7.  `mcp_rag_flow_view_diff`
8.  `mcp_rag_flow_add_test_case`
9.  `mcp_rag_base_dataset_manage` (Consolidated)
10. `mcp_rag_base_document_manage` (Consolidated)
11. `mcp_rag_base_file_manage` (Consolidated)
12. `mcp_rag_base_retrieve_chunks`
13. `mcp_rag_base_rewrite_query`
14. `mcp_rag_base_inspect_config`

**减少幅度**: 约 50%。

## 5. 疑问与决策 (Questions & Decisions)
*   **Q1**: 合并后的工具参数 Schema 是否会过于复杂？
    *   **Decision**: 使用 Optional 参数。例如 `dataset_manage(action, name=None, description=None, id=None)`. 如果 LLM 难以处理，可保持高频工具独立。但现在的 LLM (Gemini/GPT-4) 处理这种 Dispatch 模式通常没问题。
*   **Q2**: 是否需要兼容旧的工具名？
    *   **Decision**: 不兼容。这是一次重构，直接更新 `server.py`。
