# 任务分解文档：RAG基础服务 (Atomize)

## 1. 基础建设 (Infrastructure)
- [x] **Task 1.1**: 配置与日志模块
  - 输入: `.env` 模板
  - 输出: `config.py` (配置加载), `src/common/logger.py` (日志复用)
  - 依赖: 无

## 2. 核心功能 (Core Logic)
- [x] **Task 2.1**: RAG 客户端 - 知识库管理
  - 输入: RAGFlow API 文档
  - 输出: `rag_client.py` (Create/Delete/List/Update Dataset)
  - 依赖: Task 1.1
- [x] **Task 2.2**: RAG 客户端 - 文档管理
  - 输入: RAGFlow API 文档
  - 输出: `rag_client.py` (Upload/Delete/List Document)
  - 依赖: Task 2.1
- [x] **Task 2.3**: 影子文件管理器
  - 输入: 需求说明
  - 输出: `shadow_file_manager.py` (create_shadow_copy, apply_diff)
  - 依赖: 无

## 3. 业务场景 (Business Logic)
- [x] **Task 3.1**: 场景一处理器 (逻辑实现)
  - 输入: Markdown 解析需求
  - 输出: `scenario_processor.py` (process_clarification_suggestions)
  - 依赖: Task 2.1 (Retrieval), Task 2.3
- [x] **Task 3.2**: 场景一性能与体验优化 (v1.1)
  - 输入: 优化需求 (并行检索, 智能解析, 格式优化)
  - 输出: 
    - `scenario_processor.py`: 引入 ThreadPoolExecutor, 优化 Header Regex, 忽略 Code Block
    - `rag_client.py`: 增强 retrieve_and_answer 返回 references
  - 依赖: Task 3.1
- [ ] **Task 3.3**: 场景一工具解耦 (Decoupling)
  - 输入: 解耦需求
  - 输出:
    - `scenario_processor.py`: 重构为 extract_questions, apply_suggestions 等原子方法
    - `server.py`: 注册 create_shadow_file, extract_questions, apply_suggestions, retrieve_rag_suggestion
  - 依赖: Task 3.2
- [x] **Task 3.4**: 移除 Server 端 LLM 改写逻辑 (Revert)
  - 输入: 设计文档 v1.1
  - 输出:
    - `rag_client.py`: 移除 `call_llm` 和 `rewrite_query`
    - `scenario_processor.py`: 回退为正则清洗 (作为保底)
  - 依赖: Task 3.2

## 4. 服务集成 (Integration)
- [x] **Task 4.1**: MCP Server 路由实现
  - 输入: `server.py` 骨架
  - 输出: 完整的 `server.py`，注册所有 Tool
  - 依赖: Task 2.x, Task 3.1

## 5. 验证与交付 (Verification)
- [x] **Task 5.1**: 编写验证脚本
  - 输入: 测试用例
  - 输出: `tests/run_verification.py` (及 pytest 测试用例)
  - 依赖: Task 4.1
