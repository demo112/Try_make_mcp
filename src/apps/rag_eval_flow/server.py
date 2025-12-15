import sys
import os

# 1. 显式导入标准库，确保 PyInstaller 分析时能捕获这些依赖
# 这些库在 logic.py 或 fastmcp 依赖链中被使用，但在静态分析中可能丢失
import csv
import json
import logging
import pickletools
import webbrowser
import typing

# 2. 显式导入第三方库
try:
    import diskcache
    import pathvalidate
    import exceptiongroup
    import cachetools
    import pandas  # logic.py 强依赖
    import litellm # logic.py 强依赖
except ImportError as e:
    # 在开发环境如果没有安装某些库，可能不需要立即报错，但在打包环境这是致命的
    print(f"Warning: Failed to import dependency: {e}")

from fastmcp import FastMCP

# 3. 导入业务逻辑
# 强制将当前目录加入 sys.path，确保能找到同级模块 logic.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from logic import generate_qa_pairs, run_rag_simulation, evaluate_results
except ImportError as e:
    # 打印关键错误信息
    import sys
    print(f"Critical Error: Could not import 'logic' module: {e}")
    # 在打包环境中，logic.py 应该作为数据文件存在于当前目录
    print(f"Current dir: {current_dir}")
    try:
        print(f"Directory listing: {os.listdir(current_dir)}")
    except:
        pass
    raise e


# Initialize MCP Server
mcp = FastMCP("RAG评估工作流")
logger = logging.getLogger(__name__)

@mcp.tool()
async def generate_test_dataset(source_path: str, output_path: str, num_pairs: int = 20) -> str:
    """
    生成测试问答对 (Step 1 & 2)
    
    Args:
        source_path: 知识库文件绝对路径 (支持 Markdown/Txt)
        output_path: 输出 CSV 文件绝对路径
        num_pairs: 生成问答对数量 (默认 20)
    """
    logger.info(f"Generating {num_pairs} pairs from {source_path}")
    return generate_qa_pairs(source_path, output_path, num_pairs)

@mcp.tool()
async def run_qa_test(dataset_path: str, knowledge_base_path: str, output_path: str) -> str:
    """
    基于知识库执行问答测试 (Step 3)
    
    Args:
        dataset_path: 包含问题的 CSV 文件路径
        knowledge_base_path: 知识库文件路径 (作为上下文)
        output_path: 输出结果 CSV 路径
    """
    logger.info(f"Running QA test using {dataset_path} against {knowledge_base_path}")
    return run_rag_simulation(dataset_path, knowledge_base_path, output_path)

@mcp.tool()
async def evaluate_answers(qa_result_path: str, standard_dataset_path: str, output_path: str) -> str:
    """
    评估回答质量 (Step 4)
    
    Args:
        qa_result_path: 包含生成回答的 CSV 路径
        standard_dataset_path: 包含标准答案的 CSV 路径
        output_path: 最终评分报告 CSV 路径
    """
    logger.info(f"Evaluating results from {qa_result_path}")
    return evaluate_results(qa_result_path, standard_dataset_path, output_path)

if __name__ == "__main__":
    mcp.run()
