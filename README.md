# MCP 工厂 (MCP Factory)

这是一个基于 Model Context Protocol (MCP) 的服务生产工厂。本项目旨在标准化、流水线化地生产高质量的 MCP 服务。

## 核心文档

*   **[MCP 工厂工作流规范 (Rules)](docs/MCP_FACTORY_RULES.md)**: 详细的开发指南，包含从需求分析到交付的完整 6A 工作流。
*   **[6A 评审工作流](6a.md)**: 测试用例评审工作流规范。

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
- `docs/我的工具/`: 标准化的文档结构。

### 3. 开发与验证

请参考 [MCP 工厂工作流规范](docs/MCP_FACTORY_RULES.md) 进行开发。

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
- `docs/`: 项目文档。

## 现有应用示例

- **math_time**: 简单的加法和时间查询服务。
- **everything2md**: 多格式转 Markdown 服务。
- **review_flow**: 代码审查流服务。
