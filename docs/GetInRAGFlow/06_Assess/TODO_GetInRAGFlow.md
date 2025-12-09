# TODO: GetInRAGFlow Future Improvements

## 1. High Priority (高优先级)
- [ ] **Prompt 优化**: 优化 `EvolutionEngine` 中的 Rewrite Prompt，支持更精细的 "Diff/Patch" 模式，而不仅仅是 "Append" 或 "Replace Section"。
- [ ] **RAGFlow 深度集成**: 对接 RAGFlow 的 Dataset Management API，实现知识库的自动创建与索引更新（目前仅支持文件级存储）。
- [ ] **红蓝对抗实装**: 实现 `validate_knowledge_conflict` 的真实逻辑，调用 LLM 对比新旧知识点。

## 2. Medium Priority (中优先级)
- [ ] **UI 插件化**: 开发 VS Code 插件，右键点击 `.md` 文件即可触发 "Evolve" 或 "Harvest" 操作。
- [ ] **多模态支持**: 支持从架构图 (Mermaid/Image) 中提取知识。

## 3. Low Priority (低优先级)
- [ ] **性能优化**: 对超大文档进行分块处理，避免 Context Window 溢出。
- [ ] **统计大屏**: 生成知识库贡献度与文档进化频率的统计报表。
