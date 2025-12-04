import os
import sys
import shutil
import subprocess
from pathlib import Path
try:
    from .verify_mcp import verify_mcp_exe
except ImportError:
    # Fallback for direct script execution
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.factory.verify_mcp import verify_mcp_exe

def build_app(app_name: str, display_name: str = None):
    root_dir = Path(os.getcwd())
    app_dir = root_dir / "src" / "apps" / app_name
    server_script = app_dir / "server.py"
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    
    # 如果未提供 display_name，尝试从目录结构推断（这里简化处理，如果不传则需手动处理文档路径）
    # 为了兼容性，这里尝试去 docs 目录查找匹配的 display_name
    docs_root = root_dir / "docs"
    doc_dir = None
    if display_name:
        doc_dir = docs_root / display_name
    
    if not server_script.exists():
        print(f"❌ 错误: 找不到应用脚本: {server_script}")
        return

    print(f"🚀 开始构建应用: {app_name}")

    # 1. 清理旧构建
    if build_dir.exists():
        shutil.rmtree(build_dir)
        
    # 注意：我们不完全删除 dist，因为可能包含其他应用的构建。
    # 但我们会删除当前应用的旧 release 文件夹
    release_dir_name = f"{app_name}_release"
    release_dir = dist_dir / release_dir_name
    if release_dir.exists():
        shutil.rmtree(release_dir)

    # 2. 执行 PyInstaller
    # 使用 --hidden-import 确保 fastmcp 和 common 被正确打包
    cmd = [
        "pyinstaller",
        "--name", app_name,
        "--onefile",
        "--clean",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--paths", str(root_dir),
        "--hidden-import", "mcp.server.fastmcp",
        "--hidden-import", "src.common",
        # 显式包含 converters 模块
        "--hidden-import", "src.apps.md_converter.converters",
        # 添加更多潜在的隐式依赖
        "--hidden-import", "uvicorn",
        "--hidden-import", "starlette",
        "--hidden-import", "sse_starlette",
        "--hidden-import", "pydantic",
        "--hidden-import", "anyio",
        "--collect-all", "xhtml2pdf",
        "--collect-all", "reportlab",
        "--hidden-import", "html5lib",
        "--hidden-import", "openpyxl",
        "--hidden-import", "docx",
        "--hidden-import", "markdown",
        "--hidden-import", "bs4",
        str(server_script)
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        print(f"✅ EXE 打包成功: {dist_dir / (app_name + '.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        return

    # 2.5 验证 EXE
    exe_path = dist_dir / f"{app_name}.exe"
    print(f"\n🕵️ 开始自动化验证: {exe_path}")
    if not verify_mcp_exe(str(exe_path)):
        print(f"❌ 验证失败！EXE 无法正常启动或响应 MCP 协议。")
        print("⚠️ 跳过发布包组装。请检查日志或代码。")
        return
    print("✅ 验证通过！应用功能正常。")

    # 3. 创建 Release 目录并组装交付物
    try:
        release_dir.mkdir(parents=True, exist_ok=True)
        print(f"📦 组装交付物至: {release_dir}")
        
        # 3.1 移动 EXE
        exe_path = dist_dir / f"{app_name}.exe"
        if exe_path.exists():
            shutil.move(str(exe_path), str(release_dir / f"{app_name}.exe"))
        else:
            print(f"⚠️ 警告: 未找到生成的 EXE 文件: {exe_path}")

        # 3.2 复制配置文件 (如果存在)
        config_src = app_dir / "config.json"
        if config_src.exists():
            shutil.copy(str(config_src), str(release_dir / "config.json"))
            print("  - 已复制 config.json")
        else:
            print("  - (无 config.json，跳过)")

        # 3.3 复制说明文档
        # 优先级: UserManual.md > Readme.md
        manual_src = None
        if doc_dir and (doc_dir / "UserManual.md").exists():
            manual_src = doc_dir / "UserManual.md"
        elif doc_dir and (doc_dir / "Readme.md").exists():
            manual_src = doc_dir / "Readme.md"
        
        if manual_src:
            shutil.copy(str(manual_src), str(release_dir / "README.md"))
            print(f"  - 已复制文档 ({manual_src.name} -> README.md)")
        else:
            print("⚠️ 警告: 未找到文档 (UserManual.md 或 Readme.md)")

        print(f"\n🎉 构建完成！发布包位置: {release_dir}")

    except Exception as e:
        print(f"❌ 组装交付物失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.factory.build_app <app_name> [display_name]")
        print("Example: python -m src.factory.build_app todo_list 待办清单")
    else:
        display_name = sys.argv[2] if len(sys.argv) > 2 else None
        build_app(sys.argv[1], display_name)
