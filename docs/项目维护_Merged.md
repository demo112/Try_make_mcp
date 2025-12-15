# 项目维护 Documentation


# Module: 项目维护


## Stage: 01_Align


### File: ALIGNMENT_清理项目结构.md

# ALIGNMENT: 清理项目结构

## 1. 背景 (Context)
项目根目录存在大量生成的 `.spec` 文件和临时脚本，导致结构混乱。需要根据 6A 工作流规范进行整理。

## 2. 需求 (Requirements)
*   **清理根目录**: 移除 `.spec` 文件，将它们移至构建目录或临时目录。
*   **归档脚本**: 将 `check_env.py` 等辅助脚本移至 `scripts/` 目录。
*   **优化构建流程**: 修改 `src/factory/build_app.py`，使其将生成的 spec 文件放置在 `build/` 目录中，避免污染根目录。

## 3. 约束 (Constraints)
*   不得破坏现有的构建流程。
*   不得删除必要的配置文件（如 `.gitignore`, `requirements.txt`）。

## 4. 疑问 (Questions)
*   无。


---

### File: CONSENSUS_清理项目结构.md

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


---

## Stage: 03_Atomize


### File: TASK_清理项目结构.md

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


---

## Stage: 05_Automate


### File: ACCEPTANCE_清理项目结构.md

# ACCEPTANCE: 清理项目结构

## 验证结果 (Verification Results)

| 检查项 | 结果 | 备注 |
| :--- | :--- | :--- |
| 根目录无 `.spec` 文件 | ✅ Pass | 已清理 |
| 根目录无 `check_env.py` | ✅ Pass | 已迁移至 `scripts/debug_env.py` |
| `src/factory/build_app.py` 配置正确 | ✅ Pass | 添加了 `--specpath specs/` |
| 构建过程正常 | ✅ Pass | `math_time` 构建成功 |
| spec 文件生成在 `specs/` | ✅ Pass | 验证 `specs/math_time.spec` 存在 |

## 遗留问题 (Issues)
*   无。

## 结论 (Conclusion)
项目结构清理完成，构建流程已优化，符合 6A 工作流规范。


---

## Stage: 06_Assess


### File: FINAL_清理项目结构.md

# FINAL: 清理项目结构

## 项目摘要
本次维护任务旨在清理项目根目录的冗余文件，并优化构建流程以防止未来再次污染。

## 主要变更
1.  **构建脚本优化**: 修改了 `src/factory/build_app.py`，将 PyInstaller 生成的 spec 文件重定向至 `specs/` 目录。
2.  **文件归档**:
    *   移除了根目录下的所有 `.spec` 文件。
    *   将 `check_env.py` 移动至 `scripts/debug_env.py`。
3.  **目录结构更新**:
    *   新增 `scripts/`: 用于存放辅助脚本。
    *   新增 `specs/`: 用于存放构建生成的 spec 文件（由构建脚本自动创建）。

## 后续建议
*   定期检查根目录，保持整洁。
*   新添加的辅助脚本应直接放入 `scripts/` 目录。


---
