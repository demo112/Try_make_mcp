# 遗留问题与行动项：MCP生产工厂

## 1. 待办事项
- [ ] **Common 库增强**: 实现 `load_dotenv` 封装，使新应用默认支持环境变量。
- [ ] **ReviewFlow 路径优化**: 优化 `review_flow` 的状态文件存储路径，使其不依赖于运行目录（考虑使用 `appdirs` 库）。
- [ ] **文档补全**: 为迁移后的 `math_time` 和 `review_flow` 补充详细的 6A 文档。

## 2. 长期规划
- [ ] **CI/CD 集成**: 编写 GitHub Actions workflow，在提交时自动运行 `build_app`。
- [ ] **模板多样化**: 在 `init_app` 中支持多种模板选择（如：基础版、数据库版、Web版）。
