# 共识文档：MCP生产工厂

## 1. 需求概述
建立一套标准化的工程体系（“工厂”），用于在本项目（`Try_make_mcp`）中高效、规范地生产和管理多个 MCP (Model Context Protocol) 应用程序。

## 2. 核心决策：Monorepo 架构
为了便于复用代码和统一管理，项目将采用 Monorepo（单体仓库）结构。

### 2.1 目录结构重构目标
```text
Try_make_mcp/
├── docs/                   # 项目级文档
│   ├── MCP生产工厂/        # 本次任务的6A文档
│   └── apps/               # 各个具体 App 的文档链接或归档
├── src/
│   ├── common/             # 公共组件库 (FastMCP封装, 通用Tools, 6A状态机等)
│   ├── factory/            # 工厂流水线工具 (CLI脚本)
│   │   ├── init.py         # 初始化新应用
│   │   └── build.py        # 打包应用
│   └── apps/               # 应用集合
│       ├── math_time/      # 原 math-time-server
│       └── review_flow/    # 原 review-flow-server
├── scripts/                # 便捷入口脚本 (PowerShell/Batch)
├── requirements.txt        # 统一依赖
└── README.md
```

## 3. 交付物 (Deliverables)

### 3.1 基础设施代码
1.  **`src/factory/init_app.py`**:
    -   功能：交互式输入应用名称（中文+英文）。
    -   输出：自动创建 `src/apps/{app_name}` 和 `docs/{app_name_cn}`。
    -   包含：预置的 `server.py` 模板，预置的 6A 文档空模板。
2.  **`src/factory/build_app.py`**:
    -   功能：扫描 `src/apps` 下的应用，支持选择性打包。
    -   输出：生成独立的 `.spec` 并调用 PyInstaller，产物存入 `dist/`。

### 3.2 现有项目迁移
- 将 `src/server.py` 迁移至 `src/apps/math_time/server.py`。
- 将 `src/review_flow.py` 迁移至 `src/apps/review_flow/server.py`。
- 调整现有打包脚本以适配新结构。

## 4. 验收标准 (Acceptance Criteria)
1.  **结构清晰**：项目根目录干净，所有源码归位。
2.  **一键创建**：运行 `python -m src.factory.init_app` 能成功创建一个包含完整 6A 文档结构和代码模板的新 MCP 应用。
3.  **一键打包**：运行构建脚本能成功打包迁移后的 `math_time` 和 `review_flow`，且生成的 EXE 可运行。
4.  **无缝运行**：迁移后的旧服务功能不受影响。

## 5. 约束与规范
- **编码规范**：所有新代码必须有类型标注和中文文档字符串。
- **路径处理**：工厂脚本必须兼容 Windows 路径分隔符，并处理好相对路径导入问题。
- **依赖管理**：所有应用共用根目录的 `.venv` 和 `requirements.txt`，除非特殊情况。
