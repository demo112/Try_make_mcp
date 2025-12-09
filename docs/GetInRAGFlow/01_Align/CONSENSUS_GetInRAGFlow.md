# CONSENSUS: GetInRAGFlow

## 1. 需求定义 (Requirement Definition)
构建一个深度集成于 6A 工作流的 **智能知识治理系统 (Intelligent Knowledge Governance System)**。
不仅仅是回答问题，更是管理评审过程中知识的流动、验证与沉淀。

## 2. 核心共识 (Core Consensus)

### 2.1 知识分层与隔离 (Knowledge Layering)
必须严格遵守以下分层，防止知识污染：
- **L1 Global (Golden)**: 全企业通用的规范（如安全红线、编码规范）。**[Read-Only for Project]**
- **L2 Product (Golden)**: 特定产品线的稳定知识（如支付网关接口定义）。**[Read-Only for Project]**
- **L3 Project (Transient)**: 当前评审项目产生的临时知识。**[Read-Write]**

### 2.2 强制技术卡点 (Mandatory Technical Gates)
系统必须在代码层面强制执行以下检查，**不允许绕过**：
1.  **Gate 1: Initialization Check**
    - `init_review` 时，必须检测 `ALIGNMENT` 文档是否存在合法的 YAML Frontmatter (Product/Module)。
    - **Fail Action**: 报错并拒绝初始化后续文档。
2.  **Gate 2: Validation Check**
    - `harvest_knowledge` 后，必须自动触发 `GovernanceEngine.validate_conflict`。
    - **Fail Action**: 标记冲突条目，禁止自动入库。
3.  **Gate 3: Promotion Check**
    - `promote_knowledge` 时，必须检测 `Promotion_Request.md` 是否包含有效的架构师签名 (`[Approved by: ...]`)。
    - **Fail Action**: 拒绝写入 L1/L2 知识库。

### 2.3 交互规范 (Interaction Specs)
- **文档优先**: 所有的输入（问题）和输出（答案、审批单）必须以 Markdown 文档为载体，不依赖即时通讯软件。
- **独立字段**: AI 生成的内容必须写入 `**AI 参考建议**`，严禁触碰 `**回答**` 字段。
- **人工最终决策**: 只有 `**回答**` 字段的内容会被 Harvest 进知识库。

## 3. 技术实现边界 (Technical Boundaries)
- **协议**: MCP (Model Context Protocol) over Stdio。
- **核心依赖**: 
    - RAGFlow API (提供向量检索与 LLM 能力)。
    - Python 3.10+ (Logic Layer)。
- **交付物**: 
    - `rag_flow_mcp` (包含 Inference, Governance, Lifecycle 三大引擎)。
    - 预置的 MCP Tools (`agentic_search`, `check_metadata`, `promote_knowledge` 等)。

## 4. 验收标准 (Acceptance Criteria)
1.  **流程阻断测试**: 故意删除元数据，系统应拒绝工作；故意不签名，系统应拒绝晋升。
2.  **知识隔离测试**: 在 Payment 项目中提问，不应检索到 Logistics 项目的私有知识（除非标记为 Global）。
3.  **红蓝对抗测试**: 故意录入与旧知识矛盾的结论，系统应发出冲突警报。
