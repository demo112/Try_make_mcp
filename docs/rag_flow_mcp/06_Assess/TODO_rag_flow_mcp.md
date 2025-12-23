# 待办事项 (TODO List)

## 1. 策略调整与未来规划 (Strategy & Roadmap)
> **决策记录 (2025-02-18)**: 
> 当前项目策略调整为 **“聚焦场景一：智能澄清与建议填充”**。
> 暂时搁置“方案进化”、“知识收割”等复杂流程，集中资源打磨核心体验。

### 1.1 核心体验打磨 (P0 - Focus)
- [ ] **可视化增强**: 在文档中使用图标 (🔴/🟡/🟢) 直观展示置信度。
- [ ] **交互优化**: 增加自然语言指令支持，使用户无需记忆工具名。
- [ ] **文档模板约束**: 提供标准 Markdown 模板，降低解析失败率。
- [ ] **环境检查**: 增加启动前检查（Pre-flight Check），确保 `.env` 配置正确。

### 1.2 待实现功能 (Backlog - Future)
以下功能点来自用户反馈与架构审视，暂时搁置，待场景一成熟后启动。

#### 工具链完善
- [ ] **Apply/Merge 工具**: 提供指令（如 `apply_shadow_changes`），允许用户一键合并 AI 生成的影子副本，打通“最后一步”。
- [ ] **多源知识收割**: 扩展 `harvest_knowledge_candidates`，支持从代码注释 (`TODO`)、Commit Message、`DECISION_LOG.md` 中提取知识。
- [ ] **交互式澄清**: 对于低置信度问题，MCP 应反向提问或提供选项，而非强行填充。
- [ ] **审批流集成**: 在 `promote_knowledge` 环节增加鉴权（如 Leader Key）或审批人记录字段。

---

## 2. 环境配置
- [x] **API Key 配置**: 请在 `.env` 文件中配置 `RAGFLOW_API_KEY`, `RAGFLOW_HOST`。
- [x] **依赖安装**: 运行 `python -m pip install -r requirements.txt`。

## 3. 测试与验证
- [ ] **真实环境验证**: 配置真实 API Key 后，运行针对 `InferenceEngine` 的集成测试，验证 RAG 检索效果。
- [ ] **CRUD 接口测试**: 编写针对新 CRUD 工具 (`create_dataset` 等) 的集成测试脚本，验证与 RAGFlow 服务的交互。
