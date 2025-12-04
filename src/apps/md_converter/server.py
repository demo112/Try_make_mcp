from mcp.server.fastmcp import FastMCP
import os
from .converters import md_to_word, md_to_pdf, md_to_excel

# 初始化 MCP Server
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
