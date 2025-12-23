import sys
import os
import json
import logging

# Setup path to import src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.apps.rag_base.config import load_config
from src.apps.rag_base.core.rag_client import RAGClient
from src.apps.rag_base.core.scenario_processor import ScenarioProcessor
from src.common.logger import get_app_logger

# Setup Logger to Console for this script
logger = get_app_logger("rag_base_verification")
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

def main():
    logger.info("Starting Verification...")
    
    # 1. Config
    config = load_config()
    logger.info(f"Loaded config: API_KEY={'*' * len(config['RAGFLOW_API_KEY'])}, HOST={config['RAGFLOW_HOST']}")
    
    if not config['RAGFLOW_API_KEY']:
        logger.error("Missing RAGFLOW_API_KEY")
        return

    # 2. RAG Client Smoke Test
    client = RAGClient(config)
    logger.info("Testing RAG Connectivity (List Datasets)...")
    res = client.list_datasets(page=1, page_size=5)
    logger.info(f"List Datasets Result: {res.get('status')}")
    if res.get('status') != 'success':
        logger.error(f"Failed to connect to RAGFlow: {res}")
        # Continue anyway to test local logic if possible? No, scenario needs RAG.
        # But for mock test we might want to proceed.
    
    # 3. Scenario 1 Test
    logger.info("Testing Scenario 1 (Clarification Suggestions)...")
    
    # Create dummy markdown
    test_file = os.path.join(current_dir, "test_clarification.md")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("# Review Record\n\n## 1. What is RAGFlow?\n\n## 2. How to deploy?\n")
    
    processor = ScenarioProcessor(client)
    
    # Mock RAG response if connectivity failed? 
    # For now, let's run it. If no Chat ID, it returns 0 confidence and skips.
    
    res = processor.process_clarification_suggestions(test_file, "")
    logger.info(f"Scenario Result: {res}")
    
    if res['status'] == 'success':
        shadow_file = res['shadow_file']
        if os.path.exists(shadow_file):
            logger.info(f"Shadow file created: {shadow_file}")
            with open(shadow_file, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"Shadow Content Preview:\n{content[:500]}")
            
            # Clean up
            os.remove(shadow_file)
        else:
            logger.error("Shadow file reported created but not found!")
    
    os.remove(test_file)
    logger.info("Verification Complete.")

if __name__ == "__main__":
    main()
