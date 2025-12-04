import os
import sys
import logging
import asyncio
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Add project root to sys.path to import src.common
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.common.config import load_config
except ImportError:
    # Fallback if running from installed package or different structure
    # This simple fallback mimics the behavior of load_config but without reading the file
    def load_config(default=None):
        return default or {}

try:
    from .path_utils import map_path_to_container
    from .converter import convert_file_sync
except ImportError:
    # For direct execution
    from path_utils import map_path_to_container
    from converter import convert_file_sync

# Load config
config = load_config({
    "mcp_debug": False,
    "host_root": "",
    "container_root": "",
    "log_level": "INFO"
})

# Set env vars from config if present (Config.json takes precedence over defaults, but .env might override if loaded after? 
# Usually we want Config.json to be the way for EXE users to configure without Env vars.)
if config.get("host_root"):
    os.environ["HOST_ROOT"] = config["host_root"]
if config.get("container_root"):
    os.environ["CONTAINER_ROOT"] = config["container_root"]
if config.get("mcp_debug"):
    os.environ["MCP_DEBUG"] = "1"

# Load .env (for development or overrides)
load_dotenv()
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# Configure logging
log_level_name = config.get("log_level", "INFO").upper()
log_level = getattr(logging, log_level_name, logging.INFO)

# Force DEBUG if MCP_DEBUG is set
if getattr(sys, 'frozen', False) or os.environ.get("MCP_DEBUG"):
    log_level = logging.DEBUG

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 初始化 MCP Server
mcp = FastMCP("Everything2MD")

@mcp.tool()
async def convert_to_markdown(source_path: str, output_path: str) -> str:
    """
    将各种文档格式转换为 Markdown (异步)。
    支持格式: 
    - Office: .docx, .doc, .xlsx, .xls, .pptx, .ppt
    - PDF: .pdf
    - Images (OCR): .png, .jpg, .jpeg, .tiff, .bmp

    Args:
        source_path: 源文件的绝对路径。
        output_path: 目标 Markdown 文件的绝对路径。

    Returns:
        转换结果信息，成功返回 "Conversion successful"，失败返回错误详情。
    """
    # 路径映射 (Docker Support)
    source_path = map_path_to_container(source_path)
    output_path = map_path_to_container(output_path)
    
    logging.info(f"Converting (Async): {source_path} -> {output_path}")

    if not os.path.exists(source_path):
        return f"Error: Source file not found: {source_path}"
    
    try:
        # 使用 converter 模块的同步转换函数，并在线程池中运行
        await asyncio.to_thread(convert_file_sync, source_path, output_path)
        return "Conversion successful"

    except Exception as e:
        logging.error(f"Conversion failed: {e}")
        return f"Error: Conversion failed: {e}"

if __name__ == "__main__":
    mcp.run()
