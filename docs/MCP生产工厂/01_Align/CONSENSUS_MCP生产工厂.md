# MCP生产工厂 - 达成共识 (Consensus)

## 1. 输入/输出规范

### 1.1 `init_project`
*   **输入**:
    *   `app_name` (str): 应用英文名 (snake_case)，如 `todo_list`。
    *   `display_name` (str): 应用中文显示名，如 `待办清单`。
*   **输出**:
    *   Success message string with paths to created files.

### 1.2 `build_project`
*   **输入**:
    *   `app_name` (str): 应用英文名。
*   **输出**:
    *   Success message string with path to generated EXE and ZIP.

### 1.3 `verify_project`
*   **输入**:
    *   `app_name` (str): 应用英文名。
*   **输出**:
    *   Verification result string (Pass/Fail logs).

### 1.4 `list_projects`
*   **输入**: 无
*   **输出**:
    *   JSON-formatted string listing all apps in `src/apps`.

## 2. 鉴权方式
*   [ ] API Key
*   [ ] OAuth
*   [x] 无需鉴权 (本地运行，通过 Stdio 通信)

## 3. 部署方式
*   [x] 独立 EXE (自身也可被构建)
*   [ ] Docker 镜像
*   [x] 源码运行 (推荐，因为需要操作源码目录)

## 4. 特殊说明
*   由于该 MCP 需要操作文件系统和执行构建命令，**强烈建议**在源码环境下运行，而不是作为打包后的 EXE 运行（尽管也可以，但路径处理会更复杂）。
*   本 MCP 本质上是 `mcp_manager.py` 的远程/协议化接口。
