# CHECKLIST: GetInRAGFlow v2.0

## 1. 完整性检查 (Completeness)
- [x] **四核引擎**: `UNIFIED_DESIGN.md` 已包含 **Evolution Engine (进化引擎)** 及其职责定义。
- [x] **分层架构**: L1 (企业)/L2 (产品族)/L3 (项目) 知识库分层结构已在设计中明确。
- [x] **任务解耦**: 主线 (澄清+进化) 与 支线 (收割+晋升) 已在 MCP 工具链中物理解耦。
- [x] **状态持久化**: 基于 Markdown 的状态管理 (Checkboxes, Revision Logs) 已定义。

## 2. 一致性检查 (Consistency)
- [x] **5W1H**: 所有核心节点 (Node) 和原子任务 (Task) 已补充 5W1H 定义。
- [x] **MCP 接口**: `TASK_GetInRAGFlow.md` 中的 MCP 工具列表已包含 `evolve_scheme_document`。
- [x] **流程闭环**: 进化引擎输出的 `v1.1` 文档设计为可作为新一轮循环的输入。

## 3. 可行性检查 (Feasibility)
- [x] **进化逻辑**: `evolve_scheme` 已规划基于 LLM 分析问答对并应用 Diff/Patch 的策略。
- [x] **元数据锚点**: `check_metadata_compliance` 已设计支持 Family/Product/Module 多层级校验。
- [x] **红蓝对抗**: 冲突检测逻辑已定义为基于 LLM 的观点比对步骤。

## 4. 风险控制 (Risk Control)
- [x] **死循环风险**: 进化触发依赖人工确认 (Human-in-the-loop)，避免自动无限循环。
- [x] **知识覆盖**: L1/L2/L3 分层策略已针对“相似但有细微差异”场景优化。
- [x] **数据安全**: 敏感信息 (API Keys) 严格遵循 `.env` 隔离规范。

## 5. 结论
- [x] **READY TO AUTOMATE**: 确认所有 v2.0 变更已就绪，可以进入 Stage 5: Automate。
