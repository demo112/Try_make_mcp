# 待办事项：MCP交付规范升级后续

## 建议任务

- [ ] **Update Legacy Apps**: 为 `math_time` 和 `review_flow` 添加 `config.json` 和 `UserManual.md`。
- [ ] **Config Validation**: 在 `src.common.config` 中增加 JSON Schema 校验，确保用户配置格式正确。
- [ ] **Auto-Zip**: 修改 `build_app.py`，在生成 release 文件夹后自动将其压缩为 `.zip` 文件，方便分发。
