import sys
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
# This script is at src/apps/rag_flow_mcp/tests/run_test_with_material.py
project_root = Path(__file__).resolve().parents[4]
sys.path.append(str(project_root))

# Load env
env_path = project_root / "src/apps/rag_flow_mcp/.env"
load_dotenv(env_path)

from src.apps.rag_flow_mcp.core.rag_client import RAGClient
from src.apps.rag_flow_mcp.server import fill_clarification_suggestions

def run_test():
    # Config
    api_key = os.getenv("RAGFLOW_API_KEY")
    base_url = os.getenv("RAGFLOW_HOST")
    dataset_ids = os.getenv("RAG_DATASET_IDS")
    
    if not dataset_ids:
        print("Error: RAG_DATASET_IDS not found in env")
        return

    dataset_id = dataset_ids.split(",")[0].strip()
    
    # Files
    # Expecting material in the same directory under 'materials' folder
    current_dir = Path(__file__).parent
    test_material_path = str(current_dir / "materials" / "Answer_Source_01.md")
    target_doc_path = r"c:\Users\Administrator\Documents\trae_projects\use_rag_mcp\docs\AI智能服务评审工作流\06_方案业务评审问题_AI智能服务.md"
    
    # 1. Initialize Client (Correct order: api_key, base_url)
    client = RAGClient(api_key, base_url)
    
    # 2. Upload Test Material
    print(f"Uploading {test_material_path} to dataset {dataset_id}...")
    file_name = os.path.basename(test_material_path)
    
    upload_res = client.upload_document(dataset_id, test_material_path)
    
    upload_success = False
    if "error" not in upload_res and "code" in upload_res and upload_res["code"] == 0:
        print(f"Upload Result: {upload_res}")
        upload_success = True
    else:
        print(f"Upload might have failed or timed out: {upload_res}")
        print("Checking if file exists in dataset...")
        try:
            docs_res = client.list_documents(dataset_id, page=1, page_size=100, keywords=file_name)
            # Handle potential data structure variations
            docs_list = []
            if "data" in docs_res:
                if isinstance(docs_res["data"], list):
                    docs_list = docs_res["data"]
                elif isinstance(docs_res["data"], dict) and "docs" in docs_res["data"]:
                    docs_list = docs_res["data"]["docs"]
            
            for doc in docs_list:
                if doc["name"] == file_name:
                    print(f"File {file_name} found in dataset! Assuming upload succeeded.")
                    # Check parsing status if possible
                    if doc.get("run_status") == '1':
                        print("File is parsed successfully.")
                    else:
                        print(f"File status: {doc.get('run_status')} (1=Parsed)")
                    upload_success = True
                    break
        except Exception as e:
            print(f"Error checking documents: {e}")

    if not upload_success:
        print("Could not verify file upload. Proceeding anyway to test retrieval...")
        # return

    # 3. Wait for parsing
    print("Waiting 15 seconds for RAGFlow parsing/indexing...")
    time.sleep(15)
    
    # 4. Run Clarification
    print(f"Running clarification on {target_doc_path}...")
    try:
        result = fill_clarification_suggestions(target_doc_path)
        print("Clarification Result:")
        print(result)
    except Exception as e:
        print(f"Error during clarification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
