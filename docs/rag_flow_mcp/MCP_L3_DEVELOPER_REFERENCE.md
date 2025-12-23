# RAG Flow MCP 开发参考手册 (L3 - 代码细节级)

本文档面向 **核心开发者** 和 **维护者**，提供详细的代码结构、API 签名、配置说明及开发规范。

> **注意**: 标记为 `[Disabled]` 的模块在当前版本（聚焦场景一）中不应被调用或修改，除非是进行修复性维护。

---

## 1. 代码目录结构

```text
src/apps/rag_flow_mcp/
├── core/                   # 核心通用组件
│   ├── doc_processor.py    # 文档处理工具 (旧版，部分逻辑迁移至 Engines)
│   ├── evaluator.py        # QualityEvaluator: 质量评估与门控
│   ├── markdown_ast.py     # MarkdownASTManager: 基于 AST 的文档修改 [Disabled]
│   ├── rag_client.py       # RAGClient: RAGFlow API 客户端 [Core]
│   └── shadow_file_manager.py # ShadowFileManager: 影子副本管理 [Core]
├── engines/                # 业务逻辑引擎
│   ├── base.py             # BaseEngine: 引擎基类
│   ├── evolution.py        # EvolutionEngine: 方案进化逻辑 [Disabled]
│   ├── governance.py       # GovernanceEngine: 合规与治理逻辑
│   ├── inference.py        # InferenceEngine: 问答与推理逻辑 [Active]
│   └── lifecycle.py        # LifecycleEngine: 知识生命周期逻辑 [Disabled]
├── tools/                  # 辅助工具 (可视化等)
├── .env                    # 环境变量配置
├── config.py               # 配置加载模块
├── server.py               # MCP Server 入口，工具注册
└── requirements.txt        # 依赖列表
```

---

## 2. 核心类 API 详解

### 2.1 `InferenceEngine` (`engines/inference.py`) - [Active]

继承自 `BaseEngine`。

*   `initialize() -> bool`: 初始化 RAG 客户端和评估器。
*   `fill_clarification_suggestions(doc_path: str) -> Dict[str, Any]`:
    *   读取文档，解析问题块。
    *   调用 `_safe_rag_search` 获取答案。
    *   调用 `_verify_truthfulness` 校验质量。
    *   生成影子副本。
*   `_safe_rag_search(global_ctx, local_ctx, question, dataset_ids, retries=3)`: 带重试的 RAG 搜索。

### 2.2 `RAGClient` (`core/rag_client.py`) - [Core]

*   `__init__(api_key, base_url, chat_id, ...)`: 初始化 HTTP Session。
*   `agentic_search(global_ctx, local_ctx, question, dataset_ids) -> Dict`: 执行代理式搜索（含查询重写、重试）。
*   `retrieve_and_answer(query, dataset_ids) -> Dict`: 底层 API 调用 (`/api/v1/chats_openai/...`)。

### 2.3 [Disabled] `EvolutionEngine` (`engines/evolution.py`)
*(暂停维护)*

*   `evolve_scheme_document(...)`: 基于决策修改文档。

### 2.4 [Disabled] `MarkdownASTManager` (`core/markdown_ast.py`)
*(暂停维护)*

*   `replace_section(...)`: AST 级替换。

---

## 3. 配置项说明 (.env)

项目使用 `python-dotenv` 加载配置。

| 变量名 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `RAGFLOW_API_KEY` | 是 | - | RAGFlow 系统 API Key |
| `RAGFLOW_HOST` | 是 | - | RAGFlow 服务地址 (e.g., `http://192.168.1.100`) |
| `RAGFLOW_CHAT_ID` | 是 | - | 用于对话的 Chat Assistant ID |
| `RAGFLOW_TIMEOUT` | 否 | `120` | 请求超时时间 (秒) |
| `RAGFLOW_TOP_K` | 否 | `10` | 检索切片数量 |
| `RAGFLOW_SIMILARITY_THRESHOLD` | 否 | `0.2` | 相似度阈值 |
| `RAG_DATASET_IDS` | 否 | - | 默认检索的数据集 ID 列表 (逗号分隔) |

---

## 4. 开发规范

### 4.1 日志
*   **必须**使用 `src.common.get_app_logger`。
*   **严禁**使用 `print()`，因为标准输出 (Stdio) 被 MCP 协议占用。
*   在 `server.py` 中使用 `@log_tool_call` 装饰器记录工具调用的输入输出。

### 4.2 异常处理
*   **工具层 (`server.py`)**: 捕获所有异常，记录堆栈信息，并返回 JSON 格式的错误信息 `{"status": "error", "message": ...}`，**不可让 Server 崩溃**。
*   **引擎层**: 捕获业务逻辑异常，尽可能降级处理（如跳过某条目的处理），并记录 Warning 日志。

### 4.3 类型提示
*   所有函数参数和返回值必须包含 Python Type Hints。

### 4.4 依赖管理
*   新增依赖需写入 `requirements.txt`。
*   构建 EXE 时若缺少模块，需在 `build_app.py` 中添加 `--hidden-import`。

---

## 5. 测试方法

### 5.1 单元测试
位于 `src/apps/rag_flow_mcp/tests/`。

```powershell
# 运行所有测试
pytest src/apps/rag_flow_mcp/tests/
```

### 5.2 MCP Inspector 调试
使用官方 Inspector 调试 Server 接口。

```powershell
npx @modelcontextprotocol/inspector py src/apps/rag_flow_mcp/server.py
```

### 5.3 构建验证
验证打包后的 EXE 是否正常工作。

```powershell
python -m src.factory.build_app rag_flow_mcp
```
