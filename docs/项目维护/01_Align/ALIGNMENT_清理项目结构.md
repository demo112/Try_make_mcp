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
