# 任务：MCP 可用性检查 - 共识文档 (CONSENSUS)

## 1. 核心共识
- **现状确认**: `rag_flow_mcp_release` 目录为空，缺失关键的可执行文件 `rag_flow_mcp.exe`，导致无法进行可用性检查。
- **任务目标调整**: 任务从单纯的“检查可用性”调整为“**修复构建并检查可用性**”。
- **执行路径**:
    1. 检查并安装构建依赖 (PyInstaller)。
    2. 使用项目自带的构建脚本 `src/factory/build_app.py` 重新构建 `rag_flow_mcp`。
    3. 验证构建产物是否存在。
    4. 运行构建产物进行基本可用性测试。

## 2. 验收标准
1. `dist/rag_flow_mcp_release` 目录下必须包含 `rag_flow_mcp.exe`。
2. `rag_flow_mcp.exe` 能够成功启动（或响应版本查询/帮助指令），无立即崩溃。
3. 相关的文档 (`README.md`, `.env` 等) 完整存在。

## 3. 风险控制
- 如果构建失败，需分析错误日志并尝试修复依赖或配置问题。
- 构建环境需确保 Python 环境配置正确。
