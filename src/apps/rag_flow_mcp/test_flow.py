import os
import json
import shutil
from src.apps.rag_flow_mcp.server import (
    fill_clarification_suggestions,
    evolve_scheme_document,
    harvest_knowledge_candidates,
    promote_knowledge
)

TEST_DIR = "test_run"
SCHEME_DOC = os.path.join(TEST_DIR, "docs/MockProduct/02_Architect/test_scheme_v1.0.md")
CLARIFICATION_DOC = os.path.join(TEST_DIR, "docs/MockProduct/04_Approve/test_clarification.md")
KB_DIR = os.path.join(TEST_DIR, "knowledge/L2/MockProduct/MockModule")

def setup():
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(os.path.dirname(SCHEME_DOC))
    os.makedirs(os.path.dirname(CLARIFICATION_DOC))
    
    # Create Scheme Doc
    with open(SCHEME_DOC, 'w', encoding='utf-8') as f:
        f.write("""
# Test Scheme v1.0

## 1. Introduction
This is a test scheme.

## 2. Architecture
The system uses a 3-tier architecture.
""")

    # Create Clarification Doc
    with open(CLARIFICATION_DOC, 'w', encoding='utf-8') as f:
        f.write("""
---
product: MockProduct
module: MockModule
version: 1.0
---

# Clarification Log

## 1. Timeout Setting
**问题描述**：What should be the timeout for API calls?
**业务上下文**：High concurrency environment.
""")

def test_inference():
    print(">>> Testing Inference Engine...")
    res = fill_clarification_suggestions(CLARIFICATION_DOC)
    print(f"Result: {res}")
    
    with open(CLARIFICATION_DOC, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "**AI 参考建议**" in content:
        print("PASS: AI suggestions injected.")
    else:
        print("FAIL: AI suggestions missing.")
        exit(1)

def test_evolution():
    print("\n>>> Testing Evolution Engine...")
    
    # Simulate Human Decision
    with open(CLARIFICATION_DOC, 'a', encoding='utf-8') as f:
        f.write("\n**回答**：The timeout should be set to 500ms.\n")
        
    res = evolve_scheme_document(SCHEME_DOC, CLARIFICATION_DOC)
    print(f"Result: {res}")
    
    expected_v1_1 = SCHEME_DOC.replace("v1.0", "v1.1")
    if os.path.exists(expected_v1_1):
        with open(expected_v1_1, 'r', encoding='utf-8') as f:
            content = f.read()
        if "进化更新" in content:
             print("PASS: Scheme evolved.")
        else:
             print("FAIL: Scheme evolved but missing content.")
    else:
        print(f"FAIL: v1.1 file not found at {expected_v1_1}")
        exit(1)

def test_lifecycle():
    print("\n>>> Testing Lifecycle Engine...")
    
    # Harvest
    res_harvest = harvest_knowledge_candidates(CLARIFICATION_DOC)
    candidates = json.loads(res_harvest)
    print(f"Harvested: {len(candidates)} candidates")
    
    if len(candidates) != 1:
        print("FAIL: Expected 1 candidate.")
        exit(1)
        
    candidate = candidates[0]
    
    # Promote
    res_promote = promote_knowledge(json.dumps(candidate), KB_DIR)
    print(f"Promote Result: {res_promote}")
    
    expected_file = os.path.join(KB_DIR, f"knowledge_{candidate['id']}.json")
    if os.path.exists(expected_file):
        print("PASS: Knowledge promoted.")
    else:
        print(f"FAIL: Knowledge file not found at {expected_file}")
        exit(1)

if __name__ == "__main__":
    setup()
    test_inference()
    test_evolution()
    test_lifecycle()
    print("\nALL TESTS PASSED.")
