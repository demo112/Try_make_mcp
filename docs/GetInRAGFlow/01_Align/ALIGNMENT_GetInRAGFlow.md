# ALIGNMENT: GetInRAGFlow

## 1. 原始需求与背景
**用户输入**：
> 在执行评审工作流的过程中，会产生很多的待澄清点... 需要从原有的资料中找到这部分内容来解答新方案的待澄清点。此时就需要调用ragflow平台的知识库来查询相关的信息以做出澄清。同时，需要对检索以及回答的质量要有个评估和规范。
> 1、在查询前不仅携带该澄清点的所有内容，也要大模型总结上下文信息一起携带查询 
> 2、给这种由RAG提供信息，大模型回答的答案以独立的回答字段。与人工回答的信息不冲突。且以人工回答的信息为优先。
> 3、保证流程可靠执行而不是虚设流程。

**核心痛点**：
1.  **效率瓶颈**: 评审过程中产生的“待澄清点”依赖人工检索，效率低下且易遗漏。
2.  **知识污染 (Knowledge Pollution)**: 如果 RAG 检索了错误的上下文（如跨模块引用），会导致“幻觉”并在后续流程中污染新知识库。
3.  **流程虚设 (Process Formality)**: 传统的 checklist 往往流于形式，缺乏强制性的技术卡点（Technical Gates）来确保执行质量。
4.  **上下文丢失 (Context Loss)**: 简单的关键词搜索往往丢失了项目背景（Global Context）和局部上下文（Local Context），导致回答不准确。

**业务目标**：
- **深度集成 (Deep Integration)**: 将 RAGFlow 深度整合进 6A 工作流，使其成为“评审即知识管理”的核心引擎。
- **治理管控 (Governance)**: 通过强制元数据（Metadata）和红蓝对抗（Red Teaming）机制，确保知识的纯净性。
- **知识闭环 (Knowledge Loop)**: 实现从“检索旧知识”到“沉淀新知识”的完整闭环，并具备晋升（Promotion）机制。

## 2. 业务上下文分析
### 2.1 6A 工作流的演进
- **原状**: 线性流程，文档流转，人工评审。
- **目标状态**: 
    - **Stage 1 (Align)**: 强制锚定知识边界（Product/Module Scope）。
    - **Stage 3 (Atomize)**: Agentic RAG 主动介入，提供基于上下文的建议。
    - **Stage 5 (Automate)**: 自动收割（Harvest）人工决策产生的新知识。
    - **Stage 6 (Assess)**: 引入“红蓝对抗”和“架构师审批”作为强制卡点，决定知识是否晋升。

### 2.2 风险与缓解 (Risk & Mitigation)
- **幻觉风险**: 
    - *缓解*: 引入 **Metadata Anchoring**，强制检索时携带 Product/Module 标签，物理隔离无关知识。
- **文件覆盖风险**:
    - *缓解*: 设立独立字段 `**AI 参考建议**`，严禁覆盖 `**回答**` 字段（该字段仅限人工填写）。
- **知识冲突风险**:
    - *缓解*: 在入库前执行 **Red Teaming**，用新知识去攻击旧知识，若发现矛盾，必须人工介入解决。

## 3. 核心能力定义
1.  **Inference Engine (智能检索)**: 
    - 支持 Global + Local 上下文融合。
    - 支持 Agentic Search (Query Rewriting + Self-Correction)。
2.  **Governance Engine (治理管控)**:
    - 强制检查 `ALIGNMENT` 文档的 YAML 元数据。
    - 执行知识冲突检测。
3.  **Lifecycle Engine (生命周期)**:
    - 自动提取评审结论。
    - 生成晋升审批单（Promotion Request）。
    - 执行跨库同步（Project KB -> Golden KB）。

## 4. 决策点
- **架构模式**: 采用“三引擎”架构 (`Inference`, `Governance`, `Lifecycle`) 替代单一的 Client 模式。
- **卡点策略**: 
    - **Hard Gate**: 无元数据不启动，无验证不入库。
    - **Soft Gate**: 低置信度回答仅做标记，不阻断流程。
