# TASK: 清理项目结构

## 任务列表 (Tasks)

### Task 1: 修改构建脚本
*   **文件**: `src/factory/build_app.py`
*   **动作**: 修改 PyInstaller 命令，添加 `--specpath` 指向 `build` 目录。
*   **验证**: 代码审查。

### Task 2: 迁移脚本
*   **动作**: 创建 `scripts/` 目录。
*   **动作**: 将 `check_env.py` 移动到 `scripts/debug_env.py`。

### Task 3: 清理根目录
*   **动作**: 删除根目录下所有 `.spec` 文件。

### Task 4: 验证构建
*   **动作**: 运行 `python -m src.factory.build_app everything2md`。
*   **验证**: 构建成功，且根目录未生成 `.spec` 文件。
