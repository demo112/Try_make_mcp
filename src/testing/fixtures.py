import pytest
import sys
import os
from pathlib import Path
from .client import McpTestClient

@pytest.fixture
def mcp_server_path(request):
    """
    默认查找当前测试文件所在目录或父目录下的 server.py。
    假设结构为:
    apps/my_app/
      server.py
      tests/
        test_server.py
    """
    # 获取测试文件所在目录
    test_dir = Path(request.fspath).parent
    
    # 尝试 1: 父目录 (如果测试在 tests/ 下)
    if (test_dir.parent / "server.py").exists():
        return str(test_dir.parent / "server.py")

    # 尝试 2: 同级目录
    if (test_dir / "server.py").exists():
        return str(test_dir / "server.py")
        
    return None

@pytest.fixture
def mcp_client(mcp_server_path):
    """
    启动 MCP Server 并返回 Client。
    自动将项目根目录添加到 PYTHONPATH，确保 server.py 能导入 src 模块。
    """
    if not mcp_server_path:
        pytest.skip("server.py not found")
        
    # 计算项目根目录 (假设当前在 src/testing/fixtures.py，向上 3 层是根目录)
    # src/testing/fixtures.py -> src/testing -> src -> root
    root_dir = Path(__file__).parent.parent.parent.absolute()
    
    # 设置环境变量
    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{root_dir}{os.pathsep}{current_pythonpath}"
    
    # 使用当前 python 环境
    python_exe = sys.executable
    cmd = [python_exe, mcp_server_path]
    
    client = McpTestClient(cmd, env=env)
    client.start()
    try:
        client.initialize()
        yield client
    finally:
        client.stop()
