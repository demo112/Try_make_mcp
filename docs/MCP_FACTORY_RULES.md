# MCP 工厂工作流规范 (MCP Factory Rules)

本文档定义了使用 MCP 工厂模式开发 Model Context Protocol (MCP) 服务的标准工作流。本规范深度融合 **6A 工作流** 理念，确保从需求到交付的每个环节都具备高质量、高可靠性和可维护性。

## 0. 核心原则 (Core Principles)

1.  **规范驱动 (Specification-Driven)**: 文档先行，代码后行。所有开发活动必须基于已确认的文档。
2.  **环境隔离 (Environment Isolation)**: 所有项目必须使用 `.venv` 虚拟环境，严禁污染全局环境。
3.  **协议合规 (Protocol Compliance)**: 严格遵守 MCP 协议规范（JSON-RPC 2.0, Stdio/SSE 传输）。
4.  **可交付性 (Deliverability)**: 产出物不仅是代码，还包括可执行文件（EXE）、Docker 镜像和完整的使用文档。
5.  **中文优先**: 项目名称、文档、注释等尽可能使用中文，确保团队沟通无障碍。

---

## 1. 阶段 0: 初始化 (Stage 0: Initialization)

**目标**: 准备开发环境，初始化项目骨架。

### 1.1 环境准备
*   确保 Python 3.10+ 已安装。
*   **必须**使用虚拟环境 `.venv`：
    ```powershell
    # 如果 python 命令不可用，始终使用 py -3
    py -3 -m venv .venv
    .\.venv\Scripts\activate
    ```
*   使用 `python -m pip` 安装依赖：
    ```powershell
    python -m pip install -r requirements.txt
    ```

### 1.2 项目初始化
*   使用工厂工具初始化新应用：
    ```powershell
    # 语法: python -m src.factory.init_app <app_name_snake_case> "<Display Name>"
    python -m src.factory.init_app my_new_tool "我的新工具"
    ```
*   **产出物**:
    *   `src/apps/my_new_tool/`: 源代码目录。
    *   `docs/我的新工具/`: 包含 6A 各阶段子目录的文档结构。

---

## 2. 阶段 1: 对齐 (Stage 1: Align)

**目标**: 明确 MCP Server 的功能边界和业务目标。

### 2.1 需求分析
*   在 `docs/<Display Name>/01_Align/ALIGNMENT_<名称>.md` 中记录：
    *   **目标用户**: 谁会使用这个 MCP Server？
    *   **核心能力**: 提供哪些 Tools（工具）、Resources（资源）或 Prompts（提示词）？
    *   **依赖系统**: 需要连接哪些外部 API、数据库或本地文件？

### 2.2 达成共识
*   生成 `CONSENSUS_<名称>.md`，明确：
    *   输入/输出规范。
    *   鉴权方式（API Key, OAuth 等）。
    *   是否需要 Docker 部署或独立 EXE 封装。

---

## 3. 阶段 2: 架构 (Stage 2: Architect)

**目标**: 设计 MCP Server 的技术实现方案。

### 3.1 协议设计
*   在 `docs/<Display Name>/02_Architect/DESIGN_<名称>.md` 中定义：
    *   **Tools 定义**: 函数名、参数 Schema、返回格式。
    *   **Resources 定义**: URI Scheme (e.g., `file://`, `postgres://`)。
    *   **Prompts 定义**: 预设的 Prompt 模板。
    *   **Mermaid 图**: 使用 `<br/>` 替代 `\n` 以确保兼容性。

### 3.2 系统设计
*   **技术栈**: 默认使用 Python `fastmcp` 框架。
*   **模块划分**:
    *   `server.py`: MCP 入口，定义 Tools/Resources 路由。
    *   `core/`: 核心业务逻辑。
    *   `utils/`: 通用工具（如 HTTP 请求封装）。
*   **配置管理**: 必须支持 `.env` 文件和环境变量注入。

---

## 4. 阶段 3: 原子化 (Stage 3: Atomize)

**目标**: 将开发任务拆解为独立可测试的单元。

### 4.1 任务拆解
*   在 `docs/<Display Name>/03_Atomize/TASK_<名称>.md` 中列出原子任务。
*   每个任务应包含：输入、输出、依赖关系。

---

## 5. 阶段 4: 审批 (Stage 4: Approve)

**目标**: 执行前的最后质量门控。

### 5.1 检查清单
*   在 `docs/<Display Name>/04_Approve/CHECKLIST_<名称>.md` 中确认：
    *   [ ] 所有 Tool 参数均有 Type Hint 和 Docstring。
    *   [ ] 敏感信息（API Key）未硬编码。
    *   [ ] 异常处理机制已定义。
    *   [ ] Docker 容器（如果存在）已停止并删除，准备重新构建。

---

## 6. 阶段 5: 自动化执行 (Stage 5: Automate)

**目标**: 编写代码，构建交付物。

### 6.1 编码规范
*   **日志**: 使用 `src.common.get_app_logger`。**严禁**使用 `print()`，因为标准输出（Stdio）用于 MCP 协议通信。
*   **类型**: 严格使用 Python 类型提示。

### 6.2 验证与测试
*   **源码验证**: 使用 MCP Inspector (需要 Node.js):
    ```powershell
    npx @modelcontextprotocol/inspector py src/apps/<app_name>/server.py
    ```
*   **构建 EXE**:
    ```powershell
    python -m src.factory.build_app <app_name>
    ```
    *构建过程会自动运行 `verify_mcp` 对 EXE 进行冒烟测试。*

### 6.3 Docker 构建规范 (如需)
*   **国内镜像**: 配置阿里云/腾讯云镜像源。
*   **时区设置**: `ENV TZ=Asia/Shanghai`。
*   **字符集**: `ENV LANG=C.UTF-8`。
*   **构建前清理**: 必须先停止并删除旧容器。

---

## 7. 阶段 6: 评估 (Stage 6: Assess)

**目标**: 最终验收与交付。

### 7.1 验收测试
*   在 `docs/<Display Name>/06_Assess/ACCEPTANCE_<名称>.md` 中记录测试结果。
*   **验证工具**: 使用 `src.factory.verify_mcp` 验证最终 EXE：
    ```powershell
    python -m src.factory.verify_mcp dist/<app_name>/<app_name>.exe
    ```

### 7.2 交付物整理
*   **User Manual**: 确保 `docs/<Display Name>/UserManual.md` 包含 Client 配置示例。
*   **同步**: 更新项目里程碑，同步所有文档状态。

---

## 8. 常见问题与最佳实践

### 8.1 避免 Stdio 污染
*   **问题**: 代码中使用 `print()` 导致 MCP 连接断开。
*   **解决**: 始终使用 `logger`，输出到文件或 stderr。

### 8.2 依赖管理
*   构建 EXE 时，如果遇到 `ModuleNotFoundError`，需要在 `src/factory/build_app.py` 的 `--hidden-import` 列表中添加缺失模块。

### 8.3 路径问题
*   使用 `pathlib` 处理路径。
*   打包后资源路径需特殊处理（使用 `sys._MEIPASS`）。
