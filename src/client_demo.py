import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(current_dir, "server.py")

    # 配置服务器参数
    # 我们使用当前环境的 python 解释器来启动 server.py
    server_params = StdioServerParameters(
        command=sys.executable, 
        args=[server_script],
        env=os.environ.copy() # 传递环境变量
    )

    print("🔵正在连接到 MCP Server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. 初始化连接
            await session.initialize()
            print("🟢 连接成功！")

            # 2. 列出可用工具
            tools = await session.list_tools()
            print(f"\n🔍 发现 {len(tools.tools)} 个工具:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # 3. 调用 'add' 工具
            print("\n⚡ 正在调用工具 'add' (计算 10 + 20)...")
            result = await session.call_tool("add", arguments={"a": 10, "b": 20})
            # 结果通常是一个文本内容的列表
            print(f"✅ 计算结果: {result.content[0].text}")

            # 4. 列出可用资源
            resources = await session.list_resources()
            print(f"\n🔍 发现 {len(resources.resources)} 个资源:")
            for resource in resources.resources:
                print(f"  - {resource.uri}: {resource.name}")

            # 5. 调用 'get_current_time' 工具
            print("\n⚡ 正在调用工具 'get_current_time'...")
            # 注意：现在时间获取变成了一个工具
            time_result = await session.call_tool("get_current_time")
            print(f"✅ 当前时间: {time_result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run())
