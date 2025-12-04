import os
import subprocess
import shutil
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import pymupdf4llm
try:
    import pymupdf4llm
except ImportError:
    logger.warning("pymupdf4llm not installed. PDF conversion will fail.")
    pymupdf4llm = None

# Try to import pytesseract and Pillow
try:
    import pytesseract
    from PIL import Image
except ImportError:
    logger.warning("pytesseract or Pillow not installed. OCR conversion will fail.")
    pytesseract = None
    Image = None

# Load environment variables
load_dotenv()
# Try loading from script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

def find_executable(name: str, default_paths: list[str], env_var: str = None) -> str:
    """
    查找可执行文件的路径。
    优先级:
    1. 环境变量 (如果提供了 env_var)
    2. 系统 PATH
    3. 默认路径
    """
    # 1. 检查环境变量
    if env_var:
        custom_path = os.getenv(env_var)
        if custom_path:
            if os.path.exists(custom_path):
                return custom_path
            else:
                # 如果显式配置了环境变量但路径无效，抛出异常以提醒用户
                raise FileNotFoundError(f"Configured {env_var} path not found: {custom_path}")

    # 2. 检查 PATH
    path = shutil.which(name)
    if path:
        return path
    
    # 3. 检查默认路径
    for p in default_paths:
        if os.path.exists(p):
            return p
            
    # 4. 如果都找不到，返回原始名称
    return name

# Define tool paths
try:
    SOFFICE_PATH = find_executable("soffice", [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
    ], "LIBREOFFICE_PATH")

    PANDOC_PATH = find_executable("pandoc", [
        r"C:\Program Files\Pandoc\pandoc.exe",
        r"C:\Users\Administrator\AppData\Local\Pandoc\pandoc.exe"
    ], "PANDOC_PATH")
    
    # Tesseract Path Configuration
    try:
        TESSERACT_PATH = find_executable("tesseract", [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract"
        ], "TESSERACT_PATH")
        
        # Configure pytesseract if found and module is available
        if pytesseract and os.path.exists(TESSERACT_PATH) and os.path.isfile(TESSERACT_PATH):
             pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
             
    except Exception as e:
        logger.warning(f"Tesseract not found: {e}. OCR will not work.")
        TESSERACT_PATH = None

except FileNotFoundError as e:
    logger.error(f"Critical Error: {e}")
    # We don't exit here to avoid killing the importing process, but conversion will fail
    SOFFICE_PATH = None
    PANDOC_PATH = None

def _convert_office_to_md(source_path: str, output_path: str, file_extension: str) -> None:
    """同步处理 Office 文档转换 (DOCX, DOC, XLSX, XLS)"""
    if not SOFFICE_PATH or not PANDOC_PATH:
        raise RuntimeError("LibreOffice or Pandoc not found.")

    if file_extension in ['.docx', '.doc']:
        # DOCX/DOC -> HTML (LibreOffice) -> MD (Pandoc)
        html_output_path = output_path + ".html"
        subprocess.run([SOFFICE_PATH, "--headless", "--convert-to", "html", source_path, "--outdir", os.path.dirname(html_output_path) or "."], check=True, capture_output=True)
        
        source_filename = os.path.splitext(os.path.basename(source_path))[0]
        generated_html = os.path.join(os.path.dirname(html_output_path) or ".", source_filename + ".html")
        
        if not os.path.exists(generated_html):
             raise FileNotFoundError(f"Intermediate HTML file not found: {generated_html}")
        
        subprocess.run([PANDOC_PATH, "-f", "html", "-t", "markdown", generated_html, "-o", output_path], check=True, capture_output=True)
        
        if os.path.exists(generated_html):
            os.remove(generated_html)
            
    elif file_extension in ['.xlsx', '.xls']:
        # XLSX/XLS -> CSV (LibreOffice) -> MD (Pandoc)
        csv_output_path = output_path + ".csv"
        subprocess.run([SOFFICE_PATH, "--headless", "--convert-to", "csv", source_path, "--outdir", os.path.dirname(csv_output_path) or "."], check=True, capture_output=True)
        
        source_filename = os.path.splitext(os.path.basename(source_path))[0]
        generated_csv = os.path.join(os.path.dirname(csv_output_path) or ".", source_filename + ".csv")
        
        if not os.path.exists(generated_csv):
             raise FileNotFoundError(f"Intermediate CSV file not found: {generated_csv}")

        subprocess.run([PANDOC_PATH, "-f", "csv", "-t", "markdown", generated_csv, "-o", output_path], check=True, capture_output=True)
        
        if os.path.exists(generated_csv):
            os.remove(generated_csv)

def _convert_pptx_to_md(source_path: str, output_path: str, file_extension: str) -> None:
    """同步处理 PPT/PPTX 转换"""
    if file_extension == '.pptx':
        subprocess.run(["pptx2md", source_path, "-o", output_path], check=True, capture_output=True)

    elif file_extension == '.ppt':
        if not SOFFICE_PATH:
            raise RuntimeError("LibreOffice not found for PPT conversion.")

        pptx_temp_path = os.path.join(os.path.dirname(output_path) or ".", os.path.splitext(os.path.basename(source_path))[0] + ".pptx")
        
        subprocess.run([SOFFICE_PATH, "--headless", "--convert-to", "pptx", source_path, "--outdir", os.path.dirname(pptx_temp_path) or "."], check=True, capture_output=True)
        
        if not os.path.exists(pptx_temp_path):
             raise FileNotFoundError(f"Intermediate PPTX file not found: {pptx_temp_path}")

        subprocess.run(["pptx2md", pptx_temp_path, "-o", output_path], check=True, capture_output=True)
        
        if os.path.exists(pptx_temp_path):
            os.remove(pptx_temp_path)

def _convert_pdf_to_md(source_path: str, output_path: str) -> None:
    """同步处理 PDF 转换"""
    if pymupdf4llm is None:
         raise ImportError("pymupdf4llm module not found. Please install it to convert PDFs.")

    md_text = pymupdf4llm.to_markdown(source_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_text)

def _convert_image_to_md(source_path: str, output_path: str) -> None:
    """同步处理图片 OCR 转换"""
    if pytesseract is None or Image is None:
        raise ImportError("pytesseract or Pillow not installed. Please install them to convert images.")
    
    # Check if Tesseract path is valid/set in pytesseract
    try:
        # Attempt to get version to check if binary works
        pytesseract.get_tesseract_version()
    except Exception:
        raise RuntimeError("Tesseract-OCR executable not found or not working. Please install Tesseract and set TESSERACT_PATH.")

    try:
        image = Image.open(source_path)
        # Perform OCR
        # lang='chi_sim+eng' could be used if we want chinese support by default, 
        # but let's stick to default (eng) or whatever is installed/default for now to avoid errors if chi_sim missing.
        # We can improve this later to be configurable.
        text = pytesseract.image_to_string(image)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception as e:
        raise RuntimeError(f"OCR conversion failed: {e}")

def convert_file_sync(source_path: str, output_path: str) -> None:
    """
    Synchronously convert a file to Markdown.
    Dispatcher for different file types.
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file not found: {source_path}")

    file_extension = os.path.splitext(source_path)[1].lower()
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if file_extension in ['.docx', '.doc', '.xlsx', '.xls']:
        _convert_office_to_md(source_path, output_path, file_extension)
            
    elif file_extension in ['.pptx', '.ppt']:
        _convert_pptx_to_md(source_path, output_path, file_extension)

    elif file_extension == '.pdf':
        _convert_pdf_to_md(source_path, output_path)
        
    elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        _convert_image_to_md(source_path, output_path)

    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
