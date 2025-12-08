# 审批检查清单

- [ ] **Core Logic**:
    - [ ] `workflow.py`: 能够正确处理中文特性名。
    - [ ] `document.py`: 能够正确写入文件，无编码问题。
    - [ ] `test_case.py`: 表格格式正确。
- [ ] **Server**:
    - [ ] 所有 Tool 参数均有 Type Hint。
    - [ ] 所有 Tool 均有 Docstring。
    - [ ] 错误处理完善（e.g., 文件无法写入）。
- [ ] **Environment**:
    - [ ] 依赖已安装 (`mcp`).
- [ ] **Build**:
    - [ ] `build_app.py` 配置正确（如果需要 hidden imports）。
