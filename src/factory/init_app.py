import os
import sys
from pathlib import Path
import json

# 定义模板
SERVER_TEMPLATE = """from mcp.server.fastmcp import FastMCP
from src.common import get_app_logger, load_config
import logging

# 1. 加载配置
# 默认配置
default_config = {{
    "log_level": "INFO",
    "custom_message": "Hello from default config!"
}}
config = load_config(default_config)

# 2. 初始化日志
logger = get_app_logger("{app_name}")
log_level = getattr(logging, config.get("log_level", "INFO").upper(), logging.INFO)
logger.setLevel(log_level)

logger.info(f"App started with config: {{config}}")

# 3. 初始化 MCP Server
# {display_name}
mcp = FastMCP("{app_name}")

@mcp.tool()
def hello_world() -> str:
    \"\"\"
    测试工具
    \"\"\"
    message = config.get("custom_message", "Hello default!")
    logger.info(f"Hello world tool called. Returning: {{message}}")
    return f"{{message}} (from {display_name})"

if __name__ == "__main__":
    mcp.run()
"""

TEST_TEMPLATE = """import pytest
from src.testing.client import McpTestClient

def test_tool_list(mcp_client: McpTestClient):
    \"\"\"测试工具列表是否包含 hello_world\"\"\"
    tools = mcp_client.list_tools()
    names = [t["name"] for t in tools]
    assert "hello_world" in names

def test_hello_world(mcp_client: McpTestClient):
    \"\"\"测试 hello_world 工具调用\"\"\"
    result = mcp_client.call_tool("hello_world")
    assert len(result) > 0
    text_content = result[0]["text"]
    assert "Hello" in text_content
    assert "{display_name}" in text_content
"""

CONFTEST_TEMPLATE = """from src.testing.fixtures import mcp_server_path, mcp_client
"""

README_TEMPLATE = """# {display_name}

## 简介
这是由 MCP Factory 自动生成的 MCP 应用程序。

## 6A 工作流
- [ ] 01_Align
- [ ] 02_Architect
- [ ] 03_Atomize
- [ ] 04_Approve
- [ ] 05_Automate
- [ ] 06_Assess
"""

CONFIG_TEMPLATE = {
    "log_level": "INFO",
    "custom_message": "Hello from config.json!"
}

MANUAL_TEMPLATE = """# {display_name} 使用手册

## 1. 简介
本应用提供 MCP 服务，支持通过 Stdio 进行交互。

## 2. 安装与运行
无需安装，直接运行发布包中的 `{app_name}.exe` 即可。通常需要配合 MCP Client (如 Claude Desktop, Trae 等) 使用。

### 2.1 Client 配置
请在您的 MCP Client 配置文件（例如 Claude Desktop 的配置）中添加以下内容。
**注意**：请将 `command` 中的路径替换为 `{app_name}.exe` 的实际绝对路径。

```json
{{
  "mcpServers": {{
    "{app_name}": {{
      "command": "D:/path/to/{app_name}.exe",
      "args": []
    }}
  }}
}}
```

### 2.2 应用配置
在 EXE 同级目录下存在 `config.json` 文件，您可以修改它来调整应用行为。

```json
{{
    "log_level": "INFO",
    "custom_message": "Hello from config.json!"
}}
```

- `log_level`: 日志级别 (DEBUG, INFO, WARNING, ERROR)
- `custom_message`: `hello_world` 工具返回的自定义消息

## 3. 故障排查
如果应用无法启动，请尝试在命令行中运行 EXE，查看输出日志。
"""

# 6A 文档模板
ALIGNMENT_TEMPLATE = """# {display_name} - 需求对齐 (Align)

## 1. 项目背景
> 简要描述项目的背景和目标。

## 2. 目标用户
> 谁会使用这个 MCP Server？

## 3. 核心能力
> 提供哪些 Tools（工具）、Resources（资源）或 Prompts（提示词）？

## 4. 依赖系统
> 需要连接哪些外部 API、数据库或本地文件？

## 5. 核心约束
- 必须遵循 6A 工作流。
- 必须使用 Python 编写。
- 必须支持通过 Stdio 通信。
"""

CONSENSUS_TEMPLATE = """# {display_name} - 达成共识 (Consensus)

## 1. 输入/输出规范
- **输入**:
- **输出**:

## 2. 鉴权方式
- [ ] API Key
- [ ] OAuth
- [ ] 无需鉴权 (本地运行)

## 3. 部署方式
- [x] 独立 EXE
- [ ] Docker 镜像
"""

DESIGN_TEMPLATE = """# {display_name} - 架构设计 (Architect)

## 1. 整体架构
```mermaid
graph TD
    Client[MCP Client] <--> |Stdio| Server[MCP Server]
    Server --> |Call| Core[Core Logic]
    Core --> |Use| Utils[Utilities]
```

## 2. 接口定义 (Tools)
| 工具名称 | 描述 | 参数 | 返回值 |
| :--- | :--- | :--- | :--- |
| `hello_world` | 测试工具 | 无 | 欢迎消息字符串 |

## 3. 资源定义 (Resources)
> 如果有资源 (Resources)，请在此定义 URI Scheme。

## 4. 提示词定义 (Prompts)
> 如果有提示词 (Prompts)，请在此定义。
"""

TASK_TEMPLATE = """# {display_name} - 任务拆解 (Atomize)

## 1. 任务清单
- [ ] **Task 1**: 初始化项目结构 (已由工厂完成)
- [ ] **Task 2**: 实现核心逻辑
- [ ] **Task 3**: 实现 MCP Tools 接口
- [ ] **Task 4**: 编写单元测试
- [ ] **Task 5**: 编写集成测试 (使用 Inspector)
- [ ] **Task 6**: 构建 EXE 并验证

## 2. 依赖关系
Task 1 -> Task 2 -> Task 3 -> Task 4 -> Task 5 -> Task 6
"""

CHECKLIST_TEMPLATE = """# {display_name} - 审批清单 (Approve)

## 1. 代码质量
- [ ] 所有 Tool 参数均有 Type Hint 和 Docstring。
- [ ] 敏感信息（API Key）未硬编码 (使用 .env)。
- [ ] 异常处理机制已定义。
- [ ] 日志使用 `logger` 而非 `print`。

## 2. 功能完整性
- [ ] 所有核心功能已实现。
- [ ] 单元测试通过。

## 3. 构建准备
- [ ] `requirements.txt` 已更新。
- [ ] Docker 容器（如果存在）已停止并删除。
"""

ACCEPTANCE_TEMPLATE = """# {display_name} - 验收测试 (Assess)

## 1. 测试结果
| 测试项 | 预期结果 | 实际结果 | 状态 |
| :--- | :--- | :--- | :--- |
| EXE 启动 | 正常启动，无报错 | | 待测 |
| Tool 调用 | 返回预期结果 | | 待测 |
| 资源读取 | 正常读取内容 | | 待测 |

## 2. 遗留问题
> 记录已知但暂未修复的非阻塞性问题。

## 3. 交付确认
- [ ] EXE 可运行
- [ ] 文档齐全
"""

def create_app(app_name: str, display_name: str):
    # 1. 路径计算
    root_dir = Path(os.getcwd())
    apps_dir = root_dir / "src" / "apps"
    docs_dir = root_dir / "docs"
    
    target_app_dir = apps_dir / app_name
    target_doc_dir = docs_dir / display_name
    
    # 2. 检查冲突
    if target_app_dir.exists():
        print(f"❌ 错误: 应用目录已存在: {target_app_dir}")
        return
    if target_doc_dir.exists():
        print(f"❌ 错误: 文档目录已存在: {target_doc_dir}")
        return
        
    print(f"🚀 开始创建应用: {display_name} ({app_name})")
    
    # 3. 创建代码结构
    try:
        target_app_dir.mkdir(parents=True)
        (target_app_dir / "__init__.py").touch()
        
        # 生成 server.py
        server_code = SERVER_TEMPLATE.format(app_name=app_name, display_name=display_name)
        with open(target_app_dir / "server.py", "w", encoding="utf-8") as f:
            f.write(server_code)
            
        # 生成 config.json
        with open(target_app_dir / "config.json", "w", encoding="utf-8") as f:
            json.dump(CONFIG_TEMPLATE, f, indent=4)

        # 生成测试目录
        tests_dir = target_app_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "__init__.py").touch()

        # 生成 test_server.py
        test_code = TEST_TEMPLATE.format(app_name=app_name, display_name=display_name)
        with open(tests_dir / "test_server.py", "w", encoding="utf-8") as f:
            f.write(test_code)

        # 生成 conftest.py
        with open(tests_dir / "conftest.py", "w", encoding="utf-8") as f:
            f.write(CONFTEST_TEMPLATE)
            
        print(f"✅ 代码目录创建完成: {target_app_dir}")
    except Exception as e:
        print(f"❌ 创建代码目录失败: {e}")
        return

    # 4. 创建文档结构 (6A)
    try:
        target_doc_dir.mkdir(parents=True)
        
        # 定义子目录和对应的文件
        structure = {
            "01_Align": [
                (f"ALIGNMENT_{display_name}.md", ALIGNMENT_TEMPLATE),
                (f"CONSENSUS_{display_name}.md", CONSENSUS_TEMPLATE)
            ],
            "02_Architect": [
                (f"DESIGN_{display_name}.md", DESIGN_TEMPLATE)
            ],
            "03_Atomize": [
                (f"TASK_{display_name}.md", TASK_TEMPLATE)
            ],
            "04_Approve": [
                (f"CHECKLIST_{display_name}.md", CHECKLIST_TEMPLATE)
            ],
            "05_Automate": [], # 自动化阶段通常是产出代码，暂无特定文档模板
            "06_Assess": [
                (f"ACCEPTANCE_{display_name}.md", ACCEPTANCE_TEMPLATE)
            ]
        }
        
        for subdir, files in structure.items():
            subdir_path = target_doc_dir / subdir
            subdir_path.mkdir()
            
            for filename, content in files:
                formatted_content = content.format(display_name=display_name)
                with open(subdir_path / filename, "w", encoding="utf-8") as f:
                    f.write(formatted_content)
            
        readme_content = README_TEMPLATE.format(display_name=display_name)
        with open(target_doc_dir / "Readme.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
            
        # 生成 UserManual.md
        manual_content = MANUAL_TEMPLATE.format(app_name=app_name, display_name=display_name)
        with open(target_doc_dir / "UserManual.md", "w", encoding="utf-8") as f:
            f.write(manual_content)
            
        print(f"✅ 文档目录创建完成: {target_doc_dir}")
    except Exception as e:
        print(f"❌ 创建文档目录失败: {e}")
        return
        
    print("\n🎉 应用创建成功！")
    print(f"👉 运行: python -m src.apps.{app_name}.server")
    print(f"🧪 测试: pytest src/apps/{app_name}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m src.factory.init_app <app_name_en> <display_name_cn>")
        print("Example: python -m src.factory.init_app todo_list 待办清单")
    else:
        create_app(sys.argv[1], sys.argv[2])
