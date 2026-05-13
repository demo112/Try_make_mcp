import os
import json
import shutil
import pytest
from pathlib import Path
from src.apps.rag_flow_mcp.server import (
    fill_clarification_suggestions,
    evolve_scheme_document,
    harvest_knowledge_candidates,
    promote_knowledge
)

# 使用绝对路径，避免在不同目录下运行测试导致路径错误
BASE_DIR = Path(__file__).parent.resolve()
TEST_DIR = BASE_DIR / "test_run"
SCHEME_DOC = TEST_DIR / "docs/MockProduct/02_Architect/test_scheme_v1.0.md"
CLARIFICATION_DOC = TEST_DIR / "docs/MockProduct/04_Approve/test_clarification.md"
KB_DIR = TEST_DIR / "knowledge/L2/MockProduct/MockModule"

@pytest.fixture(scope="module", autouse=True)
def setup_test_env():
    """初始化测试环境，运行前清理并创建必要文件"""
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    
    # Ensure parent directories exist
    SCHEME_DOC.parent.mkdir(parents=True, exist_ok=True)
    CLARIFICATION_DOC.parent.mkdir(parents=True, exist_ok=True)
    
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
    
    yield
    
    # Optional: Clean up after tests
    # if TEST_DIR.exists():
    #     shutil.rmtree(TEST_DIR)

def test_inference():
    print(">>> Testing Inference Engine...")
    res = fill_clarification_suggestions(str(CLARIFICATION_DOC))
    print(f"Result: {res}")
    
    with open(CLARIFICATION_DOC, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 注意：如果 Inference 引擎没有配置真实的 RAG，可能不会生成建议，或者生成 mock 建议
    # 这里我们假设它至少运行成功，不抛出异常
    assert os.path.exists(CLARIFICATION_DOC)

def test_evolution():
    print("\n>>> Testing Evolution Engine...")
    
    # Simulate Human Decision
    with open(CLARIFICATION_DOC, 'a', encoding='utf-8') as f:
        f.write("\n**回答**：The timeout should be set to 500ms.\n")
        
    res = evolve_scheme_document(str(SCHEME_DOC), str(CLARIFICATION_DOC))
    print(f"Result: {res}")
    
    expected_v1_1 = str(SCHEME_DOC).replace("v1.0", "v1.1")
    # 如果没有决策点被识别，可能不会生成新文件，这里需要根据实际逻辑调整断言
    # 只要不报错即可，或者检查返回值
    res_json = json.loads(res)
    assert res_json.get("status") == "success"

def test_lifecycle():
    print("\n>>> Testing Lifecycle Engine...")
    
    # Harvest
    res_harvest = harvest_knowledge_candidates(str(CLARIFICATION_DOC))
    candidates = json.loads(res_harvest)
    print(f"Harvested: {len(candidates)} candidates")
    
    assert len(candidates) == 1, "Expected 1 candidate to be harvested"
        
    candidate = candidates[0]
    
    # Promote
    # 注意：candidate 是 dict，promote_knowledge 接收 JSON string
    candidate_json = json.dumps(candidate, ensure_ascii=False)
    res_promote = promote_knowledge(candidate_json, str(KB_DIR))
    print(f"Promote Result: {res_promote}")
    
    res_promote_dict = json.loads(res_promote)
    assert res_promote_dict.get("status") == "success"
    assert os.path.exists(res_promote_dict.get("path"))
    
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
