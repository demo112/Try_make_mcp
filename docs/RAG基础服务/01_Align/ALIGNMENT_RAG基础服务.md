# 需求对齐文档：RAG基础服务 (Alignment)

## 1. 项目背景
用户需要构建一个基础的 RAG (Retrieval-Augmented Generation) 服务 MCP，旨在提供通用的知识库管理能力，并专门支持"场景一"（智能澄清建议填充）的业务需求。该服务将作为底层基础设施，为上层工作流提供知识检索和处理能力。

## 2. 目标用户
- **MCP 客户端用户**: 通过 Chat 界面管理知识库。
- **自动化工作流**: 如"评审工作流"等需要自动从知识库获取信息的 Agent。
- **系统管理员**: 维护和治理企业知识资产。

## 3. 核心能力 (Core Capabilities)

### 3.1 知识库基础管理 (KB Management)
必须提供对 RAGFlow 知识库 (Dataset) 的完整 CRUD 操作：
- **创建知识库 (Create)**: 初始化新的知识分区。
- **删除知识库 (Delete)**: 清理不再需要的知识库。
- **更新知识库 (Update)**: 修改知识库元数据。
- **查询知识库 (List/Get)**: 查看现有知识库列表及详情。

### 3.2 文件管理 (File Management)
支持对知识库内的文档进行管理：
- **上传文件 (Upload)**: 支持多种格式 (PDF, Markdown, Excel 等) 上传并解析。
- **删除文件 (Delete)**: 移除过时文档。
- **文件列表 (List)**: 查看知识库内的文件状态（解析中、成功、失败）。

### 3.3 场景一支持：智能澄清建议 (Scenario 1 Support)
复刻并优化原 `rag_flow_mcp` 中的核心功能：
- **功能名**: `fill_clarification_suggestions`
- **逻辑**:
  1. 读取指定的 Markdown 文档（如评审记录）。
  2. 提取文档中的问题（Headers）。
  3. 针对每个问题，在指定知识库中进行检索。
  4. 基于检索结果生成回答。
  5. 以"影子文件"或直接修改的方式（需确认）回填建议。
  *(注：根据之前经验，推荐使用影子文件机制以保护原数据)*

### 3.4 工具解耦 (Decoupling)
为了提高灵活性，将场景一的内部逻辑解耦为独立原子工具：
- **影子文件生成**: 独立暴露 `create_shadow_file` 能力。
- **问题提取**: 独立暴露 `extract_questions_from_doc` 能力。
- **建议应用**: 独立暴露 `apply_suggestions_to_doc` 能力。
- **控制器**: `fill_clarification_suggestions` 将作为控制器，编排上述原子工具完成任务。

## 4. 依赖系统
- **RAG 引擎**: RAGFlow (部署在 `192.168.150.76:8081` 或其他地址)。
- **配置**: 需要通过 `.env` 管理 `RAGFLOW_API_KEY`, `RAGFLOW_HOST` 等敏感信息。

## 5. 待确认事项 (Clarifications)
1. **鉴权**: 是否沿用 API Key 方式？(假设：是)
2. **影子文件**: 场景一是否继续采用"影子文件"机制？(建议：是，安全且非侵入)
3. **API 兼容性**: 是否需要适配 RAGFlow 的特定版本 API？(假设：适配 v1 API)
