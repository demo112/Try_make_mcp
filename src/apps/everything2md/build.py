import sys
import shutil
from pathlib import Path
import PyInstaller.__main__
from src.common import get_app_logger

# Initialize logger
logger = get_app_logger("build_everything2md")

def clean_artifacts():
    """Clean up build and dist directories."""
    # Assuming we run from project root or this script is in src/apps/everything2md
    # We want to clean the project root's build/dist folders
    
    # Determine project root based on this file's location
    # this file: src/apps/everything2md/build.py
    # root: this file.parent.parent.parent.parent
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    logger.info(f"Cleaning artifacts in {project_root}...")
    
    if dist_dir.exists():
        try:
            shutil.rmtree(dist_dir)
            logger.info(f"Removed {dist_dir}")
        except Exception as e:
            logger.warning(f"Could not remove {dist_dir}: {e}")

    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
            logger.info(f"Removed {build_dir}")
        except Exception as e:
            logger.warning(f"Could not remove {build_dir}: {e}")
    
    # Also clean .spec files in the project root
    for spec in project_root.glob("*.spec"):
        try:
            spec.unlink()
            logger.info(f"Removed {spec}")
        except Exception as e:
            logger.warning(f"Could not remove {spec}: {e}")

def build_executable(script_name: str, exe_name: str, hidden_imports: list):
    """
    Build a single executable using PyInstaller.
    
    Args:
        script_name: The name of the python script in src/apps/everything2md/ (e.g. "server.py")
        exe_name: The output executable name (e.g. "everything2md-mcp")
        hidden_imports: List of hidden imports
    """
    logger.info(f"Building {exe_name}.exe from {script_name}...")
    
    app_dir = Path(__file__).resolve().parent
    script_path = app_dir / script_name
    project_root = app_dir.parent.parent.parent
    
    if not script_path.exists():
        logger.error(f"Script not found at {script_path}")
        return False

    # Prepare arguments
    args = [
        str(script_path),
        f'--name={exe_name}',
        '--onefile',
        '--clean',
        '--noconfirm',
        # We need to add the project root to PYTHONPATH so src. imports work
        f'--paths={project_root}',
    ]
    
    # Add hidden imports
    for imp in hidden_imports:
        args.append(f'--hidden-import={imp}')
        
    # Execute PyInstaller
    try:
        PyInstaller.__main__.run(args)
        
        # Check if output exists
        # PyInstaller by default puts output in dist/ in CWD
        # If we run from project root, it should be in dist/
        dist_exe = project_root / "dist" / f"{exe_name}.exe"
        if dist_exe.exists():
            logger.info(f"Successfully created {dist_exe}")
            return True
        else:
            logger.error(f"Build finished but {dist_exe} not found.")
            return False
            
    except Exception as e:
        logger.error(f"Failed to build {exe_name}: {e}")
        return False

def main():
    clean_artifacts()
    
    # Common hidden imports
    common_hidden = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'pymupdf4llm',
        'pptx2md',
        'pytesseract',
        'PIL',
        'dotenv'
    ]
    
    # Build MCP Server
    mcp_hidden = common_hidden + ['mcp', 'mcp.server.fastmcp']
    success_mcp = build_executable("server.py", "everything2md-mcp", mcp_hidden)
    
    # Build Web App
    web_hidden = common_hidden + ['jinja2', 'python-multipart']
    success_web = build_executable("web_app.py", "everything2md-web", web_hidden)
    
    if success_mcp and success_web:
        logger.info("All builds completed successfully!")
        sys.exit(0)
    else:
        logger.error("One or more builds failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
