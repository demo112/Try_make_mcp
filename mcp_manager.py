import sys
import argparse
from pathlib import Path
import subprocess

# 添加 src 到 sys.path
sys.path.append(str(Path(__file__).parent))

from src.factory.init_app import create_app

def run_init(args):
    """初始化新应用"""
    create_app(args.app_name, args.display_name)

def run_build(args):
    """构建应用"""
    cmd = [sys.executable, "-m", "src.factory.build_app", args.app_name]
    subprocess.run(cmd)

def run_verify(args):
    """验证应用"""
    # 如果指定了路径，直接验证
    if args.path:
        target = args.path
    else:
        # 否则默认验证 dist 下的 exe
        target = f"dist/{args.app_name}/{args.app_name}.exe"
    
    cmd = [sys.executable, "-m", "src.factory.verify_mcp", target]
    subprocess.run(cmd)

def run_inspect(args):
    """调试应用 (使用 MCP Inspector)"""
    # 检查 npx 是否可用
    try:
        subprocess.run(["npx", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)
    except subprocess.CalledProcessError:
        print("❌ 错误: 未找到 npx 命令，请先安装 Node.js。")
        return

    target_file = f"src/apps/{args.app_name}/server.py"
    if not Path(target_file).exists():
        print(f"❌ 错误: 未找到文件 {target_file}")
        return

    print(f"🚀 启动 MCP Inspector 调试: {args.app_name}")
    cmd = f"npx @modelcontextprotocol/inspector py {target_file}"
    # 使用 shell=True 以便在 Windows 上正确解析 npx
    subprocess.run(cmd, shell=True)

def main():
    parser = argparse.ArgumentParser(description="MCP 工厂管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化新应用")
    init_parser.add_argument("app_name", help="应用名称 (英文 snake_case)")
    init_parser.add_argument("display_name", help="显示名称 (中文)")
    init_parser.set_defaults(func=run_init)

    # build 命令
    build_parser = subparsers.add_parser("build", help="构建应用 (生成 EXE)")
    build_parser.add_argument("app_name", help="应用名称")
    build_parser.set_defaults(func=run_build)

    # verify 命令
    verify_parser = subparsers.add_parser("verify", help="验证应用 (冒烟测试)")
    verify_parser.add_argument("--app-name", "-n", help="应用名称 (自动查找 dist 下的 exe)")
    verify_parser.add_argument("--path", "-p", help="直接指定 EXE 路径")
    verify_parser.set_defaults(func=run_verify)

    # inspect 命令
    inspect_parser = subparsers.add_parser("inspect", help="调试应用 (使用 MCP Inspector)")
    inspect_parser.add_argument("app_name", help="应用名称")
    inspect_parser.set_defaults(func=run_inspect)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
