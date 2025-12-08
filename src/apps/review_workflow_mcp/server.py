from mcp.server.fastmcp import FastMCP, Context
from src.common import get_app_logger, load_config
import sys
import os

# Add current directory to sys.path to allow imports from core when running as script (e.g. in PyInstaller)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.workflow_manager import WorkflowManager, StageEnum
except ImportError:
    from .core.workflow_manager import WorkflowManager, StageEnum

import json

# Initialize Config & Logger
config = load_config()
logger = get_app_logger("review_workflow_mcp")

# Initialize Manager
manager = WorkflowManager()

# Initialize MCP
mcp = FastMCP("review_workflow_mcp")

@mcp.tool()
def init_review(project_name: str) -> str:
    """
    Initialize a new review workflow project.
    Creates necessary directory structure and state file.
    """
    try:
        result = manager.init_project(project_name)
        logger.info(f"Initialized project: {project_name}")
        return result
    except Exception as e:
        logger.error(f"Error initializing project: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def get_current_state(project_name: str) -> str:
    """
    Get the current state of the workflow for a project.
    Returns JSON string with stage and documents.
    """
    try:
        state = manager.get_state(project_name)
        return state.model_dump_json(indent=2)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def advance_stage(project_name: str) -> str:
    """
    Move the workflow to the next stage.
    """
    try:
        result = manager.advance_stage(project_name)
        logger.info(f"Advanced stage for {project_name}: {result}")
        return result
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def save_review_document(project_name: str, filename: str, content: str) -> str:
    """
    Save a markdown document for the review.
    filename should be relative to project root, e.g., '01_Align/ALIGNMENT_Proj.md'.
    """
    try:
        result = manager.save_document(project_name, filename, content)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_project_files(project_name: str) -> str:
    """
    List all files in the project directory.
    """
    try:
        files = manager.list_files(project_name)
        return "\n".join(files)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.prompt()
def review_assistant(project_name: str) -> str:
    """
    Returns the system prompt for the Review Assistant role, 
    contextualized with the current project state.
    """
    try:
        state = manager.get_state(project_name)
        current_stage = state.current_stage.value
        
        prompt = f"""You are a 6A Workflow Review Assistant.
Current Project: {project_name}
Current Stage: {current_stage}

Your goal is to guide the user through the 6A Review Workflow.
Do not proceed to the next stage until all requirements for {current_stage} are met.

Workflow Stages:
1. Align: Analyze requirements, create ALIGNMENT and CONSENSUS docs.
2. Architect: Design system, create DESIGN doc.
3. Atomize: Break down tasks, create TASK doc.
4. Approve: Verify checklist, create CHECKLIST doc.
5. Automate: Implement and build.
6. Assess: Verify and deliver.

Current Documents:
{json.dumps(state.documents, indent=2)}

Instructions:
- Check if necessary documents for {current_stage} exist.
- If not, help the user create them using `save_review_document`.
- If satisfied, allow the user to call `advance_stage`.
"""
        return prompt
    except Exception as e:
        return f"Error loading state for {project_name}: {e}. Please ensure project is initialized."

if __name__ == "__main__":
    mcp.run()
