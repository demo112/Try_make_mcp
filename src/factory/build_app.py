import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_app(app_name: str):
    root_dir = Path(os.getcwd())
    apps_dir = root_dir / "src" / "apps"
    target_app_dir = apps_dir / app_name
    server_script = target_app_dir / "server.py"
    
    if not target_app_dir.exists():
        print(f"❌ 错误: 应用不存在: {app_name}")
        return
    
    if not server_script.exists():
        print(f"❌ 错误: 找不到入口文件: {server_script}")
        return

    print(f"🚀 开始打包应用: {app_name}")
    
    # 构造 PyInstaller 命令
    # 注意：我们需要包含 src 目录以确保 import src.common 正常工作
    # hidden-import 也是必须的，因为 fastmcp 可能使用了动态加载
    
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build" / app_name
    
    cmd = [
        "pyinstaller",
        "--name", app_name,
        "--onefile",
        "--clean",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--paths", str(root_dir),  # 将根目录加入路径，以便能找到 src
        "--hidden-import", "mcp.server.fastmcp",
        "--hidden-import", "src.common",
        str(server_script)
    ]
    
    print(f"📦 执行命令: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd, shell=True)
        print(f"\n✅ 打包成功！")
        print(f"👉 产物路径: {dist_dir / (app_name + '.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.factory.build_app <app_name>")
        
        # 列出可用应用
        root_dir = Path(os.getcwd())
        apps_dir = root_dir / "src" / "apps"
        if apps_dir.exists():
            print("\n可用应用:")
            for item in apps_dir.iterdir():
                if item.is_dir() and (item / "server.py").exists():
                    print(f"  - {item.name}")
    else:
        build_app(sys.argv[1])
