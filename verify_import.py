import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

try:
    from src.apps.rag_flow_mcp import server
    print("Server module imported successfully.")
    print("Tools registered:")
    # FastMCP doesn't easily expose a list of tools without running, 
    # but successful import means decorators ran.
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
