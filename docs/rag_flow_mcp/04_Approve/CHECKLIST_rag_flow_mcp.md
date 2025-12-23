# CHECKLIST: RAG Flow MCP v2.1

## 1. 核心约束检查 (Core Constraints) - **NEW**
- [ ] **全中文环境**: 确认文档、日志、提示词 (Prompts)、注释均为中文。
- [ ] **真实性校验**: 确认 RAG 检索已包含 `_verify_truthfulness` 逻辑 (Threshold=0.6)，严禁捏造。
- [ ] **鲁棒性设计**: 确认 `_safe_rag_search` 包含指数退避重试 (Max=3) 和服务降级策略。
- [ ] **环境隔离**: 确认敏感配置 (API Keys) 仅通过环境变量/`.env` 加载，无硬编码。
- [ ] **稳健性升级 (P0)**: 确认已引入 Markdown AST 解析，严禁使用正则表达式修改文档结构。
- [ ] **协作升级 (P0)**: 确认已采用 **Shadow Copy (影子副本)** 机制，严禁直接覆盖用户原文件。
- [ ] **质量升级 (P0)**: 确认已规划 Golden Dataset 和推理质量回归测试。
- [ ] **配置管理 (v2.2)**: 确认已实现 `.env` 加载，并正确处理了打包场景。
- [ ] **工具解耦 (v2.2)**: 确认工具已正确划分为 `mcp_rag_base_` (实施) 和 `mcp_rag_flow_` (逻辑)。
- [ ] **CRUD 完备 (v2.2)**: 确认基础工具已覆盖 Dataset/Document 的增删改查。

## 2. 完整性检查 (Completeness)
- [x] **四核引擎**: `UNIFIED_DESIGN.md` 已包含 **Evolution Engine (进化引擎)** 及其职责定义。
- [x] **分层架构**: L1 (企业)/L2 (产品族)/L3 (项目) 知识库分层结构已在设计中明确。
- [x] **任务解耦**: 主线 (澄清+进化) 与 支线 (收割+晋升) 已在 MCP 工具链中物理解耦。
- [x] **状态持久化**: 基于 Markdown 的状态管理 (Checkboxes, Revision Logs) 已定义。

## 3. 一致性检查 (Consistency)
- [x] **5W1H**: 所有核心节点 (Node) 和原子任务 (Task) 已补充 5W1H 定义。
- [x] **MCP 接口**: `TASK_RAG Flow MCP.md` 中的 MCP 工具列表已包含 `evolve_scheme_document`。
- [x] **流程闭环**: 进化引擎输出的 `v1.1` 文档设计为可作为新一轮循环的输入。

## 4. 可行性检查 (Feasibility)
- [x] **进化逻辑**: `evolve_scheme` 已规划基于 LLM 分析问答对并应用 Diff/Patch 的策略。
- [x] **元数据锚点**: `check_metadata_compliance` 已设计支持 Family/Product/Module 多层级校验。
- [x] **红蓝对抗**: 冲突检测逻辑已定义为基于 LLM 的观点比对步骤。

## 5. 结论
- [x] **READY TO AUTOMATE**: 确认所有 v2.1 变更已就绪，准许进入 Stage 5: Automate。
