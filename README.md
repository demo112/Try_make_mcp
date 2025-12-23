# MCP 工厂 (MCP Factory)

这是一个基于 Model Context Protocol (MCP) 的服务生产工厂。本项目旨在标准化、流水线化地生产高质量的 MCP 服务。

## 核心文档

*   **[MCP 工厂工作流规范 (Rules)](.trae/rules/project_rules.md)**: 详细的开发指南，包含从需求分析到交付的完整 6A 工作流。
*   **[项目编年史](docs/PROJECT_CHRONICLE.md)**: 项目演进历史与变更日志。

## 项目索引 (Project Index)

### 核心应用 (Core Apps)

| 应用名称 (App Name) | 源码目录 (Source) | 文档入口 (Docs) | 描述 |
| :--- | :--- | :--- | :--- |
| **mcp_factory** | `src/apps/mcp_factory` | [docs/mcp_factory](docs/mcp_factory/01_Align/ALIGNMENT_MCP生产工厂.md) | 生产 MCP 的 MCP，提供项目初始化、构建和验证能力。 |
| **everything2md** | `src/apps/everything2md` | [docs/everything2md](docs/everything2md/Readme.md) | 强大的文档转换工具，支持 PDF/Office/OCR 转 Markdown。 |
| **rag_flow_mcp** | `src/apps/rag_flow_mcp` | [docs/rag_flow_mcp](docs/rag_flow_mcp/Readme.md) | 集成 RAGFlow 的知识检索与管理服务。 |
| **rag_eval_flow** | `src/apps/rag_eval_flow` | [docs/rag_eval_flow](docs/rag_eval_flow/01_Align/ALIGNMENT_RAG评估工作流.md) | RAG 效果评估与测试数据集生成工具。 |
| **md_converter** | `src/apps/md_converter` | [docs/md_converter](docs/md_converter/01_Align/ALIGNMENT_MD转多格式MCP.md) | Markdown 转多格式 (Word/PDF/Excel) 工具。 |
| **test_auto_generated_app** | `src/apps/test_auto_generated_app` | [docs/test_auto_generated_app](docs/test_auto_generated_app/Readme.md) | 自动化测试生成的示例应用。 |

### 任务与归档 (Tasks & Archive)

*   **[Git 推送修复](docs/tasks/Git_Push_Fix)**: 解决 Git SSL/TLS 连接问题。
*   **[项目维护](docs/tasks/项目维护)**: 项目结构清理与维护记录。
*   **[测试体系建设](docs/tasks/测试体系建设)**: 工厂与应用测试框架的设计与实施。
*   **[教程：构建 MCP 服务](docs/tutorials/构建MCP服务)**: MCP 开发入门教程。

---

## 快速开始

### 1. 环境配置

确保已安装 Python 3.10+。

```powershell
# 1. 创建虚拟环境
py -3 -m venv .venv

# 2. 激活环境
.\.venv\Scripts\activate

# 3. 安装依赖
python -m pip install -r requirements.txt
```

### 2. 创建新应用

使用工厂工具快速初始化一个新的 MCP 服务：

```powershell
# 语法: python -m src.factory.init_app <app_name> "<Display Name>"
python -m src.factory.init_app my_tool "我的工具"
```

这将自动创建：
- `src/apps/my_tool/`: 源码目录（包含示例代码）。
- `docs/my_tool/`: 标准化的文档结构（与 App 名称一致）。

### 3. 开发与验证

请参考 [MCP 工厂工作流规范](.trae/rules/project_rules.md) 进行开发。

验证源码：
```powershell
npx @modelcontextprotocol/inspector py src/apps/my_tool/server.py
```

### 4. 构建交付

打包为独立 EXE：
```powershell
python -m src.factory.build_app my_tool
```

构建产物位于 `dist/` 目录下。

## 目录结构

- `src/apps/`: 所有 MCP 服务的源代码。
- `src/factory/`: 工厂工具链（初始化、构建、验证脚本）。
- `src/common/`: 公共库（日志、配置等）。
- `docs/`: 项目文档，一级目录与 `src/apps/` 保持同名。
