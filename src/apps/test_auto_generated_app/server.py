from mcp.server.fastmcp import FastMCP
from src.common import get_app_logger, load_config
import logging

# 1. 加载配置
# 默认配置
default_config = {
    "log_level": "INFO",
    "custom_message": "Hello from default config!"
}
config = load_config(default_config)

# 2. 初始化日志
logger = get_app_logger("test_auto_generated_app")
log_level = getattr(logging, config.get("log_level", "INFO").upper(), logging.INFO)
logger.setLevel(log_level)

logger.info(f"App started with config: {config}")

# 3. 初始化 MCP Server
# 自动生成测试
mcp = FastMCP("test_auto_generated_app")

@mcp.tool()
def hello_world() -> str:
    """
    测试工具
    """
    message = config.get("custom_message", "Hello default!")
    logger.info(f"Hello world tool called. Returning: {message}")
    return f"{message} (from 自动生成测试)"

if __name__ == "__main__":
    mcp.run()
