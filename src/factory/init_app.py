import os
import sys
from pathlib import Path

# 定义模板
SERVER_TEMPLATE = """from mcp.server.fastmcp import FastMCP
from src.common import get_app_logger

# 1. 初始化
# {display_name}
mcp = FastMCP("{app_name}")
logger = get_app_logger("{app_name}")

@mcp.tool()
def hello_world() -> str:
    \"\"\"
    测试工具
    \"\"\"
    logger.info("Hello world tool called")
    return "Hello from {display_name}!"

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
        
        server_code = SERVER_TEMPLATE.format(app_name=app_name, display_name=display_name)
        with open(target_app_dir / "server.py", "w", encoding="utf-8") as f:
            f.write(server_code)
            
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
