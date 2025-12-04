# 对齐文档 (ALIGNMENT) - Everything2MD 配置增强

## 1. 背景与目标
### 1.1 背景
当前 `Everything2MD` 服务中，LibreOffice 和 Pandoc 的路径检测依赖于系统 PATH 或硬编码的默认路径。在不同用户的 Windows 环境下（特别是便携版或非标准安装路径），这种方式可能失效，导致服务无法启动或转换失败。

### 1.2 目标
- 引入 `.env` 环境变量支持。
- 允许用户通过配置 `LIBREOFFICE_PATH` 和 `PANDOC_PATH` 显式指定工具路径。
- 优先级逻辑：环境变量 > 系统 PATH > 默认硬编码路径。

## 2. 现有架构分析
- **代码位置**: `src/apps/everything2md/server.py`
- **当前逻辑**: `find_executable` 函数依次检查 `shutil.which` 和 `default_paths`。
- **依赖管理**: `src/apps/everything2md/requirements.txt` (需新增 `python-dotenv`)。

## 3. 需求澄清 (Q&A)
- **Q**: 是否需要支持 `.env` 文件热重载？
  - **A**: 不需要，MCP 服务通常作为长运行进程，重启生效即可。
- **Q**: 默认的 `.env` 文件放在哪里？
  - **A**: 建议放在 `src/apps/everything2md/.env`，或者项目根目录。考虑到这是独立 app，优先支持 app 目录下的 `.env`。
- **Q**: 如果配置的路径无效怎么办？
  - **A**: 应记录警告日志，并回退到后续的查找逻辑（系统 PATH 等），或者直接报错（如果用户显式配置了但无效，通常应报错提示）。**决策**: 如果用户显式配置了环境变量，但路径不存在，应报错并阻止服务启动，避免静默失败。

## 4. 交付物
- 更新后的 `requirements.txt` (添加 `python-dotenv`)
- 更新后的 `server.py` (集成配置加载逻辑)
- 示例配置文件 `.env.example`
- 验证测试脚本
