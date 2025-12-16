# 待办事项 (TODO List)

## 1. 环境配置
- [ ] **API Key 配置**: 请在 `.env` 文件中配置 `RAGFLOW_API_KEY`, `RAGFLOW_HOST`。
- [ ] **依赖安装**: 运行 `python -m pip install -r requirements.txt` (已完成，请确认)。

## 2. 测试运行
- [x] **运行质量回归测试**:
  ```powershell
  python -m pytest tests/test_inference_quality.py
  ```
  状态：已验证 (Mock 模式通过)。需在 `.env` 配置真实 Key 后移除 Mock 验证真实效果。

## 3. 功能体验
- [ ] **体验影子副本**:
  1. 准备一个 Markdown 文档。
  2. 调用 `evolve_scheme_document`。
  3. 观察生成的 `_ai_revision.md` 和 `_diff_report.md`。
