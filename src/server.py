from mcp.server.fastmcp import FastMCP
from datetime import datetime

# 1. 初始化 MCP Server
# 使用 FastMCP 可以快速创建一个 MCP 服务
mcp = FastMCP("MathTime")

# 2. 定义 Tool: 加法
# 工具是可以被模型调用的函数，用于执行具体操作
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    执行两个整数的加法。
    
    Args:
        a: 第一个整数
        b: 第二个整数
        
    Returns:
        两个数的和
    """
    return a + b

# 3. 定义 Resource: 时间
# 资源是类似于文件的只读数据，用于提供上下文信息
@mcp.resource("time://now")
def get_time() -> str:
    """
    获取当前系统时间。
    
    Returns:
        ISO 8601 格式的时间字符串
    """
    return datetime.now().isoformat()

if __name__ == "__main__":
    # 启动服务，默认使用 stdio 传输协议
    mcp.run()
