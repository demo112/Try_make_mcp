# PROPOSAL: Structured Knowledge Approval & Consolidation (结构化审批与聚合)

## 1. 核心挑战
1.  **审批刚需**: 无论是 RAG 给出的建议，还是从回答中收割的新知识，都必须经过 "Review & Approve" 才能生效。AI 不能越权。
2.  **碎片化危机**: 评审问答天然是碎片化的（Q&A 形式）。如果直接将这些 Q&A 扔进知识库，知识库会变成“垃圾场”，充满重复、冲突和缺乏上下文的片段。

## 2. 解决方案架构

我们引入两个新环节来解决上述问题：**Knowledge Staging (知识暂存区)** 和 **Knowledge Consolidation (知识聚合)**。

### 2.1 流程图
```mermaid
graph TD
    subgraph Stage A: 澄清阶段
        Q[待澄清点] -->|RAG Agent| Suggestion[AI建议]
        Suggestion -->|Human Review| Answer[人工确认/修正的回答]
    end
    
    Answer -->|Harvest| Fragments[碎片化知识点]
    
    subgraph Stage B: 审批与聚合 (新设计)
        Fragments --> Staging[暂存区 (JSON/MD)]
        
        Staging -->|LLM Consolidator| TopicDraft[主题式知识草稿]
        note right of TopicDraft: 将10个关于"超时"的碎片<br/>聚合为一篇"超时配置规范"
        
        TopicDraft -->|Human Approval| ApprovedDoc[已审批文档]
        
        ApprovedDoc -->|Update| RAGFlow[知识库]
    end
```

## 3. 关键机制设计

### 机制一：Human-in-the-loop Approval (人在回路审批)
- **AI 建议的审批**: 现有的 `06_方案业务评审问题.md` 本身就是审批载体。只有当用户在 `**回答**` 字段签字确认（填写内容）后，该信息才被视为有效。
- **新知识的审批**: `harvest_knowledge_candidates` 生成的报告不仅仅是报告，它应该是一个 **可交互的审批表单**（Pull Request 概念）。
  - 生成 `KNOWLEDGE_STAGING.md`，每条新知识前有 `[ ] Approve` 复选框。

### 机制二：Semantic Consolidation (语义聚合) - 解决碎片化
- **原理**: 不直接存储 Q&A。而是定期（或按项目结束时）运行聚合任务。
- **Prompt**: "请阅读以下 20 个关于支付模块的问答碎片，识别出其中的核心概念，将其重写为一份结构化的《支付模块业务规范》文档。合并重复项，解决冲突。"
- **产出**: 从 **碎片 (Fragments)** 变为 **结构化文档 (Structured Document)**。

## 4. 实施变更 (Action Items)

1.  **升级 Harvester**: 
    - 输出不只是列表，而是分类的、带上下文的 JSON 数据，存储于 `docs/KnowledgeStaging/`。
2.  **新增 Consolidator 工具**:
    - `consolidate_knowledge(topic="Payment")`: 读取暂存区所有相关碎片，调用 LLM 生成一篇完整的 Markdown 文档。
3.  **审批工作流集成**:
    - 在 `Stage 6 (Assess)` 增加步骤：`Review Consolidated Knowledge`。

## 5. 示例：从碎片到文档
**碎片输入**:
- Q1: 超时是多久？ A1: 45秒。
- Q2: 为什么改45秒？ A2: 因为旧渠道不稳定。
- Q3: 只有支付接口是45秒吗？ A3: 是的，查询接口还是10秒。

**聚合输出 (Consolidated Doc)**:
```markdown
# 支付模块超时配置规范
## 1. 核心策略
为应对渠道不稳定性，支付模块采用差异化超时策略。

## 2. 具体配置
- **交易接口**: 45秒 (自 2024-05 更新，原为 30秒)。
- **查询接口**: 10秒 (保持不变)。
```
*(解决了碎片化，建立了完整的知识上下文)*
