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
            
        print(f"✅ 代码目录创建完成: {target_app_dir}")
    except Exception as e:
        print(f"❌ 创建代码目录失败: {e}")
        return

    # 4. 创建文档结构 (6A)
    try:
        target_doc_dir.mkdir(parents=True)
        
        subdirs = [
            "01_Align",
            "02_Architect",
            "03_Atomize",
            "04_Approve",
            "05_Automate",
            "06_Assess"
        ]
        
        for subdir in subdirs:
            (target_doc_dir / subdir).mkdir()
            
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

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m src.factory.init_app <app_name_en> <display_name_cn>")
        print("Example: python -m src.factory.init_app todo_list 待办清单")
    else:
        create_app(sys.argv[1], sys.argv[2])
