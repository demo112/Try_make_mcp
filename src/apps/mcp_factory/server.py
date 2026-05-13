import sys
import io
import json
import logging
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from mcp.server.fastmcp import FastMCP
from src.common import get_app_logger

# Ensure project root is in sys.path
# This assumes the file is at src/apps/mcp_factory/server.py
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.factory.init_app import create_app
from src.factory.build_app import build_app as run_build_app, get_pyinstaller_cmd, get_app_version
import subprocess
import os
import shutil
from mcp.server.fastmcp import FastMCP, Context

# Initialize Logger
logger = get_app_logger("mcp_factory")
logger.setLevel(logging.INFO)

# Initialize MCP Server
mcp = FastMCP("mcp_factory")

def _capture_output(func, *args, **kwargs):
    """Helper to capture stdout/stderr from a function"""
    f = io.StringIO()
    # We capture both stdout and stderr
    # Note: If the function calls subprocess (like build_app does for pyinstaller), 
    # the subprocess output might NOT be captured if it writes directly to system file descriptors
    # unless subprocess.run is used with capture_output=True inside the called function.
    # src.factory.build_app uses subprocess.check_call without capturing, so its output goes to real stdout.
    # To fix this, we might need to modify build_app or accept that some logs won't be returned in the string
    # but will appear in the MCP server's stderr.
    # However, create_app uses print(), so that will be captured.
    
    with redirect_stdout(f), redirect_stderr(f):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    return f.getvalue()

@mcp.tool()
def list_projects() -> str:
    """
    List all existing MCP projects in the factory.
    Returns a JSON string list of project names.
    """
    apps_dir = project_root / "src" / "apps"
    projects = []
    if apps_dir.exists():
        for item in apps_dir.iterdir():
            if item.is_dir() and not item.name.startswith("__") and not item.name.startswith("."):
                projects.append(item.name)
    return json.dumps(projects, indent=2)

@mcp.tool()
def init_project(app_name: str, display_name: str) -> str:
    """
    Initialize a new MCP project with 6A workflow structure.
    
    Args:
        app_name: English name (snake_case), e.g., 'todo_list'
        display_name: Chinese display name, e.g., '待办清单'
    """
    logger.info(f"Initializing project: {app_name} ({display_name})")
    output = _capture_output(create_app, app_name, display_name)
    return output

@mcp.tool()
async def build_project(app_name: str, ctx: Context) -> str:
    """
    Build an existing MCP project into a standalone EXE with real-time progress.
    
    Args:
        app_name: The name of the app to build.
    """
    logger.info(f"Building project: {app_name}")
    ctx.info(f"Starting build for {app_name}...")
    
    root_dir = project_root
    app_dir = root_dir / "src" / "apps" / app_name
    server_script = app_dir / "server.py"
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    specs_dir = root_dir / "specs"

    if not server_script.exists():
        return f"Error: App '{app_name}' does not exist or missing server.py."

    # 1. Clean up (Sync)
    ctx.info("Cleaning up previous builds...")
    if build_dir.exists(): shutil.rmtree(build_dir)
    if not specs_dir.exists(): specs_dir.mkdir(exist_ok=True)
    release_dir = dist_dir / f"{app_name}_release"
    if release_dir.exists(): shutil.rmtree(release_dir)

    # 2. Generate Command
    cmd = get_pyinstaller_cmd(app_name, root_dir, app_dir, dist_dir, build_dir, specs_dir, server_script)
    ctx.info(f"Executing: {' '.join(cmd)}")

    # 3. Run with real-time output capture
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        cwd=str(root_dir) # Ensure cwd is project root for correct path resolution
    )

    full_log = []
    
    # Simple progress estimation (PyInstaller has many steps, hard to map exactly to %)
    # We will just report activity
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            stripped = line.strip()
            full_log.append(stripped)
            # Log to MCP Logger (visible in Inspector Console)
            ctx.info(stripped)
            # Report progress if meaningful keywords found
            if "Analysis" in stripped:
                await ctx.report_progress(10, 100)
            elif "PYZ" in stripped:
                await ctx.report_progress(40, 100)
            elif "PKG" in stripped:
                await ctx.report_progress(60, 100)
            elif "EXE" in stripped:
                await ctx.report_progress(80, 100)
    
    return_code = process.poll()
    
    if return_code != 0:
        error_msg = f"Build failed with code {return_code}. Check logs."
        ctx.error(error_msg)
        return error_msg

    ctx.info("Build successful! Packaging...")
    await ctx.report_progress(90, 100)
    
    # 4. Post-processing (Verify & Package)
    # We reuse verify_mcp logic but need to run it
    exe_path = dist_dir / f"{app_name}.exe"
    
    # Run verify
    verify_cmd = [sys.executable, "-m", "src.factory.verify_mcp", str(exe_path)]
    verify_res = subprocess.run(verify_cmd, capture_output=True, text=True, cwd=str(root_dir))
    
    if verify_res.returncode != 0:
        ctx.error(f"Verification failed:\n{verify_res.stdout}\n{verify_res.stderr}")
        return "Build succeeded but verification failed."
    
    ctx.info("Verification passed.")
    await ctx.report_progress(100, 100)
    
    return f"Build and Verification Successful!\nEXE: {exe_path}"

@mcp.tool()
def verify_project(app_name: str) -> str:
    """
    Verify the built EXE of a project using smoke tests.
    
    Args:
        app_name: The name of the app to verify.
    """
    logger.info(f"Verifying project: {app_name}")
    
    # Check distinct locations: dist/app_name.exe OR dist/app_name/app_name.exe
    # build_app puts it in dist/app_name.exe first (onefile), then copies to dist/app_name_release/...
    # Let's check the one in dist/
    
    # Actually build_app logic:
    # dist_dir = root / "dist"
    # output = dist_dir / (app_name + '.exe')
    
    exe_path = project_root / "dist" / f"{app_name}.exe"
    if not exe_path.exists():
        # Try release dir
        # release_dir = dist_dir / f"{app_name}_release"
        exe_path_release = project_root / "dist" / f"{app_name}_release" / f"{app_name}.exe"
        if exe_path_release.exists():
            exe_path = exe_path_release
        else:
            return f"Error: EXE not found at {exe_path}. Please build it first."
    
    # Run verify_mcp as subprocess
    import subprocess
    cmd = [sys.executable, "-m", "src.factory.verify_mcp", str(exe_path)]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"Error running verification: {e}"

if __name__ == "__main__":
    mcp.run()
