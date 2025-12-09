# FINAL PROJECT SUMMARY: GetInRAGFlow

## 1. 项目概览 (Project Overview)
**GetInRAGFlow** 是一个基于 MCP (Model Context Protocol) 的智能文档工作流工具，旨在通过 RAG (Retrieval-Augmented Generation) 技术，辅助软件架构设计过程中的**方案澄清**、**文档进化**与**知识沉淀**。

它不仅是一个简单的问答助手，更是一个深度集成到 6A 工作流中的**进化引擎**，能够基于人工决策自动迭代设计文档，实现“文档即代码”的持续集成。

## 2. 核心成果 (Key Deliverables)

### 2.1 四核引擎架构
- **Inference Engine (推理引擎)**: 负责理解评审问题，检索 L1/L2 知识库，提供智能建议。
- **Evolution Engine (进化引擎)**: **[v2.0 核心]** 负责将澄清后的结论反向合入方案文档，生成 v1.1 版本，实现自我进化。
- **Governance Engine (治理引擎)**: 负责文档元数据合规检查及红蓝对抗（冲突检测）。
- **Lifecycle Engine (生命周期引擎)**: 负责从项目中收割新知识，并晋升至企业/产品知识库。

### 2.2 MCP 工具集
- `fill_clarification_suggestions`: 自动填充评审问题建议。
- `evolve_scheme_document`: 自动进化方案文档。
- `check_metadata_compliance`: 元数据校验。
- `harvest_knowledge_candidates`: 知识收割。
- `promote_knowledge`: 知识晋升。

### 2.3 关键特性
- **任务解耦**: 主线任务（进化）与支线任务（沉淀）分离，互不阻塞。
- **分层知识**: 支持 L1 (企业级)、L2 (产品族)、L3 (项目级) 知识库隔离与复用。
- **状态持久化**: 基于 Markdown 的原生状态管理，无需外部数据库。

## 3. 技术栈 (Tech Stack)
- **Framework**: Python `fastmcp`
- **LLM/RAG**: RAGFlow (Client Integration)
- **Format**: Markdown, JSON-RPC
- **Process**: 6A Workflow (Align -> Assess)

## 4. 后续建议 (Recommendations)
- 建议在真实 RAGFlow 环境中进行大规模压力测试，优化 Prompt 以提高进化引擎的修改精度。
- 考虑开发 VS Code 插件，进一步简化 MCP 工具的调用体验。
