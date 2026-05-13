import json
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def capture_test_case(query: str, expected_keywords: List[str], expected_document: str = "") -> Dict[str, Any]:
    """
    Capture a test case into the golden dataset for future regression testing.
    
    Args:
        query: The question or query.
        expected_keywords: List of keywords that MUST appear in the answer.
        expected_document: (Optional) The document path that should provide the answer.
    """
    # Locate golden_dataset.json
    # Assuming it's in project_root/tests/golden_dataset.json
    # We can infer project root from this file location: src/apps/rag_flow_mcp/tools/qa_tool.py
    # Root is 5 levels up? No.
    # __file__ = .../src/apps/rag_flow_mcp/tools/qa_tool.py
    # root = .../
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../../../../"))
    dataset_path = os.path.join(project_root, "tests", "golden_dataset.json")
    
    if not os.path.exists(dataset_path):
        # Fallback relative to CWD if project structure is different
        dataset_path = os.path.abspath("tests/golden_dataset.json")
        
    if not os.path.exists(dataset_path):
         return {"status": "error", "message": f"Golden dataset not found at: {dataset_path}"}
         
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        new_case = {
            "query": query,
            "expected_answer_keywords": expected_keywords,
            "expected_document": expected_document
        }
        
        # Check for duplicates
        for item in data:
            if item["query"] == query:
                 return {"status": "warning", "message": "Test case already exists for this query."}
                 
        data.append(new_case)
        
        with open(dataset_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return {
            "status": "success", 
            "message": "Test case captured.",
            "path": dataset_path,
            "total_cases": len(data)
        }
    except Exception as e:
        logger.error(f"Failed to capture test case: {e}")
        return {"status": "error", "message": str(e)}
