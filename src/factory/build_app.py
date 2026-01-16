import os
import sys
import shutil
import subprocess
import re
from pathlib import Path
try:
    from .verify_mcp import verify_mcp_exe
except ImportError:
    # Fallback for direct script execution
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.factory.verify_mcp import verify_mcp_exe

def get_app_version(server_script_path):
    """Extract version from server.py using regex to avoid import errors"""
    try:
        content = server_script_path.read_text(encoding='utf-8')
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    except Exception:
        pass
    return "latest"

def get_pyinstaller_cmd(app_name: str, root_dir: Path, app_dir: Path, dist_dir: Path, build_dir: Path, specs_dir: Path, server_script: Path):
    """Generate the PyInstaller command arguments"""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", app_name,
        "--onefile",
        "--clean",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--specpath", str(specs_dir),
        "--paths", str(root_dir),
        "--hidden-import", "mcp.server.fastmcp",
        "--hidden-import", "fastmcp",  # Add explicit fastmcp
        "--hidden-import", "src.common",
        # 添加更多潜在的隐式依赖
        "--hidden-import", "uvicorn",
        "--hidden-import", "starlette",
        "--hidden-import", "sse_starlette",
        "--hidden-import", "pydantic",
        "--hidden-import", "anyio",
        "--hidden-import", "beartype",
        "--collect-all", "beartype",
        "--hidden-import", "pickletools",
    ]


    # Special handling for everything2md dependencies
    if app_name == "everything2md" or app_name == "md_converter":
        cmd.extend([
            "--hidden-import", "src.apps.md_converter.converters",
            "--collect-all", "xhtml2pdf",
            "--collect-all", "reportlab",
            "--hidden-import", "html5lib",
            "--hidden-import", "openpyxl",
            "--hidden-import", "docx",
            "--hidden-import", "markdown",
            "--hidden-import", "bs4",
        ])
    
    # Special handling for rag_eval_flow dependencies
    if app_name == "rag_eval_flow":
        # 关键修改：将 logic.py 所在目录加入 paths，以便 PyInstaller 能将其作为模块分析
        # 这样 import logic 就能被解析，并且 logic.py 内部的 import 也能被分析
        cmd.extend(["--paths", str(app_dir)])
        
        # 强制添加 logic.py 作为数据文件，防止模块分析失败
        logic_file = app_dir / "logic.py"
        if logic_file.exists():
            print(f"📦 Forcing inclusion of logic.py from {logic_file}")
            cmd.extend(["--add-data", f"{logic_file}{os.pathsep}."])

        cmd.extend([
            # 强制分析 logic 模块，而不是仅仅作为文件复制
            "--hidden-import", "logic",
            
            # 显式依赖
            "--hidden-import", "pandas",
            "--hidden-import", "litellm",
            "--hidden-import", "numpy",
            "--hidden-import", "pickletools",
            "--hidden-import", "csv",
            "--hidden-import", "json",
            
            # FastMCP 生态的隐式依赖
            "--collect-all", "litellm",
            "--collect-all", "fastmcp",
            "--collect-all", "diskcache",
            "--collect-all", "key_value",
            "--collect-all", "beartype",
            "--collect-all", "pydantic",
            "--collect-all", "starlette",
            "--collect-all", "uvicorn",
            "--collect-all", "mcp",
            
            # Pandas 及其依赖通常需要完整收集
            "--collect-all", "pandas",
            
            # Tiktoken 数据文件 (Litellm 依赖)
            "--collect-all", "tiktoken",
            "--collect-all", "tiktoken_ext",
        ])

    # Check for 'core' directory in the app and add it as data
    core_dir = app_dir / "core"
    if core_dir.exists():
        print(f"📦 Including 'core' package from {core_dir}")
        cmd.extend(["--add-data", f"{core_dir}{os.pathsep}core"])
        # Also try to import it as hidden import to ensure python modules are analyzed
        cmd.extend(["--hidden-import", f"src.apps.{app_name}.core"])

    # Include engines if exists
    engines_dir = app_dir / "engines"
    if engines_dir.exists():
        print(f"📦 Including 'engines' package from {engines_dir}")
        cmd.extend(["--add-data", f"{engines_dir}{os.pathsep}engines"])
        cmd.extend(["--hidden-import", f"src.apps.{app_name}.engines"])

    # Explicitly include config module
    config_file = app_dir / "config.py"
    if config_file.exists():
        print(f"📦 Including 'config' module from {config_file}")
        cmd.extend(["--hidden-import", f"src.apps.{app_name}.config"])

    # Special handling for rag_flow_mcp dependencies
    if app_name == "rag_flow_mcp":
        cmd.extend([
            "--hidden-import", "src.apps.rag_flow_mcp.core.evaluator",
            "--hidden-import", "markdown_it",
            "--hidden-import", "pandas",
            "--hidden-import", "requests",
            "--collect-all", "markdown_it",
            "--collect-all", "pandas"
        ])

    cmd.append(str(server_script))
    return cmd

def build_app(app_name: str, display_name: str = None):
    root_dir = Path(os.getcwd())
    app_dir = root_dir / "src" / "apps" / app_name
    server_script = app_dir / "server.py"
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    
    # 获取版本号
    app_version = get_app_version(server_script)
    print(f"📌 检测到应用版本: {app_version}")
    
    # 确定文档目录 (doc_dir)
    docs_root = root_dir / "docs"
    doc_dir = None
    
    if display_name:
        doc_dir = docs_root / display_name
    else:
        # 尝试自动推断: 
        # 1. 检查是否存在 docs/<app_name>
        if (docs_root / app_name).exists():
            doc_dir = docs_root / app_name
        # 2. (可选) 可以在这里添加更复杂的逻辑，比如遍历 docs 子目录寻找匹配的配置文件
    
    if doc_dir and doc_dir.exists():
        print(f"📂 定位到文档目录: {doc_dir}")
    else:
        print(f"⚠️ 警告: 未能自动定位到文档目录 (docs/{display_name or app_name})，交付物将仅保存在 dist 目录。")

    if not server_script.exists():
        print(f"❌ 错误: 找不到应用脚本: {server_script}")
        return

    print(f"🚀 开始构建应用: {app_name}")

    # 1. 清理旧构建
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    specs_dir = root_dir / "specs"
    if not specs_dir.exists():
        specs_dir.mkdir(exist_ok=True)
        
    # 确定发布目录 (release_dir)
    # 规则变更: 必须archives在 dist/<app_name>_release/ 目录下
    release_dir = dist_dir / f"{app_name}_release"

    # 清理旧 release
    if release_dir.exists():
        try:
            shutil.rmtree(release_dir)
        except Exception as e:
            print(f"⚠️ Warning: Failed to clean release dir: {e}")
            # Try to clean contents at least
            for item in release_dir.iterdir():
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                except Exception:
                    pass

    release_dir.mkdir(parents=True, exist_ok=True)

    # 2. 执行 PyInstaller
    # PyInstaller 依然输出到 root/dist 作为中间产物，后续再复制到 release_dir
    cmd = get_pyinstaller_cmd(app_name, root_dir, app_dir, dist_dir, build_dir, specs_dir, server_script)
    
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
        
        # 3.1 复制 EXE (改为 copy 而不是 move，以便保留 dist 中的原始文件用于调试)
        exe_path = dist_dir / f"{app_name}.exe"
        target_exe = release_dir / f"{app_name}.exe"
        if exe_path.exists():
            shutil.copy(str(exe_path), str(target_exe))
            print(f"  - 已复制 EXE: {target_exe}")
        else:
            print(f"⚠️ 警告: 未找到生成的 EXE 文件: {exe_path}")

        # 3.2 复制配置文件 (如果存在)
        config_src = app_dir / "config.json"
        if config_src.exists():
            shutil.copy(str(config_src), str(release_dir / "config.json"))
            print("  - 已复制 config.json")
        else:
            print("  - (无 config.json，跳过)")

        # 3.2.1 复制 .env (如果存在)
        # 优先复制真实的 .env (用于内部交付)，如果没有再找 .env.example
        env_src = app_dir / ".env"
        env_example_src = app_dir / ".env.example"
        
        if env_src.exists():
            shutil.copy(str(env_src), str(release_dir / ".env"))
            print("  - 已复制 .env (包含真实配置)")
        elif env_example_src.exists():
            shutil.copy(str(env_example_src), str(release_dir / ".env.example"))
            print("  - 已复制 .env.example (请重命名为 .env 并配置)")
        else:
            print("  - (无 .env 或 .env.example，建议创建)")

        # 3.3 复制说明文档
        # 优先级: UserManual.md > Readme.md
        manual_src = None
        if doc_dir and (doc_dir / "UserManual.md").exists():
            manual_src = doc_dir / "UserManual.md"
            # 显式复制 UserManual.md 以满足工厂规范
            shutil.copy(str(manual_src), str(release_dir / "UserManual.md"))
            print(f"  - 已复制文档 (UserManual.md)")
        elif doc_dir and (doc_dir / "Readme.md").exists():
            manual_src = doc_dir / "Readme.md"
        
        if manual_src:
            shutil.copy(str(manual_src), str(release_dir / "README.md"))
            print(f"  - 已生成 README.md (源自 {manual_src.name})")
        else:
            print("⚠️ 警告: 未找到文档 (UserManual.md 或 Readme.md)")

        # 3.4 复制变更日志 (CHANGELOG.md)
        if doc_dir and (doc_dir / "CHANGELOG.md").exists():
            changelog_src = doc_dir / "CHANGELOG.md"
            shutil.copy(str(changelog_src), str(release_dir / "CHANGELOG.md"))
            print(f"  - 已复制变更日志 (CHANGELOG.md)")
        else:
            print("  - (无 CHANGELOG.md，跳过)")

        print(f"\n🎉 构建完成！发布包位置: {release_dir}")

        # 4. 自动压缩发布包
        try:
            # 使用从源码提取的版本号
            zip_base_name = dist_dir / f"{app_name}_v{app_version}"
            # 这里的 zip_base_name 不需要 .zip 后缀，make_archive 会自动添加
            zip_file = shutil.make_archive(str(zip_base_name), 'zip', str(release_dir))
            print(f"🤐 已生成压缩包: {zip_file}")
        except Exception as e:
            print(f"⚠️ 压缩失败: {e}")

    except Exception as e:
        print(f"❌ 组装交付物失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.factory.build_app <app_name> [display_name]")
        print("Example: python -m src.factory.build_app todo_list 待办清单")
    else:
        display_name = sys.argv[2] if len(sys.argv) > 2 else None
        build_app(sys.argv[1], display_name)
