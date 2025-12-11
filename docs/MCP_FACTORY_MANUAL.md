# MCP 制作工厂使用手册

本文档详细介绍了如何使用 MCP 制作工厂（MCP Factory）来开发、构建和交付 Model Context Protocol (MCP) 服务。本流程深度融合了 **6A 工作流**，确保从需求分析到最终交付的高质量。

## 🚀 快速开始 (Quick Start)

### 1. 准备环境
确保你已经安装了 Python 3.10+ 和 Node.js (用于 Inspector 调试)。

```powershell
# 1. 创建并激活虚拟环境
py -3 -m venv .venv
.\.venv\Scripts\activate

# 2. 安装依赖
python -m pip install -r requirements.txt
```

### 2. 初始化应用
使用 `mcp_manager.py` 初始化一个新的 MCP 应用。

```powershell
# 语法: python mcp_manager.py init <app_name> "<中文名称>"
python mcp_manager.py init weather_tool "天气助手"
```
这将自动生成：
- 代码目录: `src/apps/weather_tool/`
- 文档目录: `docs/天气助手/` (包含 6A 各阶段模板)

### 3. 开发与调试
编写代码并使用 Inspector 进行实时调试。

```powershell
# 启动调试器 (会自动打开浏览器)
python mcp_manager.py inspect weather_tool
```

### 4. 构建交付
生成独立的 EXE 文件。

```powershell
python mcp_manager.py build weather_tool
```
构建完成后，EXE 文件位于 `dist/weather_tool/weather_tool.exe`。

---

## 🛠️ 6A 工作流详细指南

### 阶段 0: 初始化 (Init)
- **动作**: 运行 `init` 命令。
- **产出**: 基础代码骨架和文档结构。

### 阶段 1: 对齐 (Align)
- **目标**: 明确需求，消除歧义。
- **操作**:
  1. 打开 `docs/<中文名称>/01_Align/ALIGNMENT_<中文名称>.md`。
  2. 填写目标用户、核心能力和依赖系统。
  3. 确认后填写 `CONSENSUS_<中文名称>.md`，明确输入输出和鉴权方式。

### 阶段 2: 架构 (Architect)
- **目标**: 设计技术方案。
- **操作**:
  1. 打开 `docs/<中文名称>/02_Architect/DESIGN_<中文名称>.md`。
  2. 设计 Mermaid 架构图。
  3. 定义 Tool 接口 (函数名、参数) 和 Resource URI。

### 阶段 3: 原子化 (Atomize)
- **目标**: 拆解开发任务。
- **操作**:
  1. 打开 `docs/<中文名称>/03_Atomize/TASK_<中文名称>.md`。
  2. 将开发工作拆解为 Task 1, Task 2 等原子任务。
  3. 确保每个任务都有明确的完成标准。

### 阶段 4: 审批 (Approve)
- **目标**: 执行前检查。
- **操作**:
  1. 打开 `docs/<中文名称>/04_Approve/CHECKLIST_<中文名称>.md`。
  2. 逐项检查：敏感信息是否隔离？异常处理是否完善？
  3. 只有全选通过后，才能进入编码阶段。

### 阶段 5: 自动化执行 (Automate)
- **目标**: 编写代码。
- **操作**:
  1. 在 `src/apps/<app_name>/server.py` 中实现逻辑。
  2. 使用 `python mcp_manager.py inspect <app_name>` 进行单元测试。
  3. 运行 `python mcp_manager.py build <app_name>` 生成交付物。

### 阶段 6: 评估 (Assess)
- **目标**: 验收交付。
- **操作**:
  1. 运行 `python mcp_manager.py verify --app-name <app_name>` 验证 EXE。
  2. 在 `docs/<中文名称>/06_Assess/ACCEPTANCE_<中文名称>.md` 记录测试结果。
  3. 确认 `UserManual.md` 已更新。

---

## 📚 常用命令参考

| 命令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `init` | 初始化新应用 | `python mcp_manager.py init my_app "我的应用"` |
| `inspect` | 启动 MCP Inspector 调试 | `python mcp_manager.py inspect my_app` |
| `build` | 构建 EXE 文件 | `python mcp_manager.py build my_app` |
| `verify` | 验证 EXE 文件 | `python mcp_manager.py verify --app-name my_app` |

## 💡 最佳实践

1.  **日志规范**: 始终使用 `logger.info()` 或 `logger.error()`，严禁使用 `print()`，因为 `print` 会破坏 MCP 的 Stdio 通信协议。
2.  **依赖管理**: 如果构建 EXE 时提示缺包，请在 `src/factory/build_app.py` 的 `hiddenimports` 列表中添加缺失的模块。
3.  **配置管理**: 敏感信息（如 API Key）必须通过环境变量或 `.env` 文件加载，**绝不能**硬编码在代码中。
4.  **资源路径**: 读取本地文件时，请使用 `pathlib` 并考虑打包后的路径差异（参考 `src.common.path_utils`）。
