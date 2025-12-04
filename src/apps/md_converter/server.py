import sys
import os
import logging
import traceback

# 配置日志记录，以便在打包为 EXE 后排查启动错误
# 仅在 frozen (打包) 模式下，或显式请求调试时启用文件日志
if getattr(sys, 'frozen', False) or os.environ.get("MCP_DEBUG"):
    # 获取 EXE 所在目录
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.getcwd()
        
    log_file = os.path.join(application_path, 'server_debug.log')
    
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 捕获未处理的异常
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception
    logging.info("Starting MDConverter Server...")

try:
    from mcp.server.fastmcp import FastMCP
    
    # 尝试多种导入方式
    try:
        # 1. 相对导入 (IDE/源码环境)
        from .converters import md_to_word, md_to_pdf, md_to_excel
        logging.info("Imported via relative import")
    except ImportError:
        try:
            # 2. 绝对导入 (打包后，如果 converters 在根目录)
            import converters
            from converters import md_to_word, md_to_pdf, md_to_excel
            logging.info("Imported via absolute import 'converters'")
        except ImportError:
            try:
                # 3. 完整包路径导入 (如果保留了包结构)
                from src.apps.md_converter import converters
                from src.apps.md_converter.converters import md_to_word, md_to_pdf, md_to_excel
                logging.info("Imported via full package path")
            except ImportError as e:
                logging.critical(f"All import attempts failed. Last error: {e}")
                # 打印 sys.path 和 sys.modules keys 以便调试
                logging.debug(f"sys.path: {sys.path}")
                logging.debug(f"sys.modules keys containing 'converter': {[k for k in sys.modules.keys() if 'converter' in k]}")
                raise
except ImportError as e:
    logging.critical(f"Import error: {e}")
    raise

# 初始化 MCP Server
__version__ = "1.1.0"
# FastMCP(name, instructions=None, dependencies=None, **kwargs)
# 如果 FastMCP 不支持 version 参数，这里会报错。暂时移除 version 参数传递，但保留变量供构建脚本读取
mcp = FastMCP("MDConverter")

@mcp.tool()
def convert_to_word(source_path: str, output_path: str) -> str:
    """
    将 Markdown 文件转换为 Word (.docx) 文件。
    
    Args:
        source_path: 源 Markdown 文件的绝对路径。
        output_path: 目标 Word 文件的绝对路径 (需以 .docx 结尾)。
        
    Returns:
        转换结果信息。
    """
    try:
        # 简单的输入校验
        if not source_path.endswith(('.md', '.markdown')):
            return "Error: Source file must be a Markdown file."
        if not output_path.endswith('.docx'):
            return "Error: Output file must have .docx extension."
            
        return md_to_word(source_path, output_path)
    except Exception as e:
        return f"Error during conversion: {str(e)}"

@mcp.tool()
def convert_to_pdf(source_path: str, output_path: str) -> str:
    """
    将 Markdown 文件转换为 PDF 文件。
    注意：需要系统安装有支持中文的字体 (如 SimHei)。
    
    Args:
        source_path: 源 Markdown 文件的绝对路径。
        output_path: 目标 PDF 文件的绝对路径 (需以 .pdf 结尾)。
        
    Returns:
        转换结果信息。
    """
    try:
        if not source_path.endswith(('.md', '.markdown')):
            return "Error: Source file must be a Markdown file."
        if not output_path.endswith('.pdf'):
            return "Error: Output file must have .pdf extension."
            
        return md_to_pdf(source_path, output_path)
    except Exception as e:
        return f"Error during conversion: {str(e)}"

@mcp.tool()
def convert_to_excel(source_path: str, output_path: str) -> str:
    """
    提取 Markdown 文件中的表格并保存为 Excel (.xlsx) 文件。
    如果文件中有多个表格，将保存为不同的 Sheet。
    
    Args:
        source_path: 源 Markdown 文件的绝对路径。
        output_path: 目标 Excel 文件的绝对路径 (需以 .xlsx 结尾)。
        
    Returns:
        转换结果信息。
    """
    try:
        if not source_path.endswith(('.md', '.markdown')):
            return "Error: Source file must be a Markdown file."
        if not output_path.endswith('.xlsx'):
            return "Error: Output file must have .xlsx extension."
            
        return md_to_excel(source_path, output_path)
    except Exception as e:
        return f"Error during conversion: {str(e)}"

if __name__ == "__main__":
    mcp.run()
