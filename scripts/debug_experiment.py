import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure the src module is in path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

# Load env vars
load_dotenv(project_root / "src/apps/rag_flow_mcp/.env")

from src.apps.rag_flow_mcp.server import fill_clarification_suggestions

# Target file
target_file = r"c:\Users\Administrator\Documents\trae_projects\use_rag_mcp\docs\AI智能服务评审工作流\06_方案业务评审问题_AI智能服务.md"
# target_file = r"c:\Users\Administrator\Documents\trae_projects\use_rag_mcp\docs\test_q.md"

print(f"Processing file: {target_file}")

try:
    result = fill_clarification_suggestions(target_file)
    print("Success!")
    print(result)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
