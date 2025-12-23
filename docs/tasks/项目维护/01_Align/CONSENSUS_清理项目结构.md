# CONSENSUS: 清理项目结构

## 1. 目标 (Goal)
保持项目根目录整洁，规范化构建产物和脚本存放位置。

## 2. 变更范围 (Scope)
1.  **修改 `src/factory/build_app.py`**:
    *   在调用 PyInstaller 时添加 `--specpath` 参数，指向 `build` 目录。
2.  **创建 `scripts/` 目录**:
    *   用于存放辅助脚本。
3.  **文件迁移**:
    *   `check_env.py` -> `scripts/debug_env.py`
4.  **清理**:
    *   删除根目录下现有的 `*.spec` 文件。

## 3. 验收标准 (Acceptance Criteria)
*   根目录无 `.spec` 文件。
*   根目录无 `check_env.py`。
*   执行 `python -m src.factory.build_app everything2md` 能成功构建，且 spec 文件生成在 `build/` 目录中。
