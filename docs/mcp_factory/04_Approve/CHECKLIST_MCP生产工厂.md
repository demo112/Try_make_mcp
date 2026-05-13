# MCP生产工厂 - 审批清单 (Approve)

## 1. 代码质量
- [ ] 所有 Tool 参数均有 Type Hint 和 Docstring。
- [ ] 路径操作使用 `pathlib`，兼容 Windows/Linux。
- [ ] 异常处理完善，不会因为构建失败导致 MCP Server 崩溃。
- [ ] 日志输出清晰。

## 2. 功能完整性
- [ ] `init_project` 能成功创建新项目。
- [ ] `build_project` 能成功构建 EXE。
- [ ] `verify_project` 能正确检测 EXE 状态。
- [ ] `list_projects` 能列出所有项目。

## 3. 安全性
- [ ] 不允许操作项目根目录以外的文件。
