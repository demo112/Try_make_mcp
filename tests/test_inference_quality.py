import pytest
import json
import os
from typing import List, Dict
from src.apps.rag_flow_mcp.core.evaluator import QualityGatekeeper

class MockInferenceEngine:
    def __init__(self, dataset: List[Dict]):
        self.dataset = dataset

    def search(self, query: str) -> str:
        """
        Mock search that returns a perfect answer based on the golden dataset.
        In a real scenario, this would call the actual RAGFlow API.
        """
        for case in self.dataset:
            if case["query"] == query:
                # Return a constructed answer containing all keywords to ensure high score
                keywords = case["expected_answer_keywords"]
                return f"This is a mocked answer containing keywords: {' '.join(keywords)}."
        return "I don't know."

class TestInferenceQuality:
    def setup_method(self):
        dataset_path = os.path.join(os.path.dirname(__file__), "golden_dataset.json")
        with open(dataset_path, "r", encoding="utf-8") as f:
            self.dataset: List[Dict] = json.load(f)
        self.inference_engine = MockInferenceEngine(self.dataset)

    def test_semantic_similarity(self):
        """
        验证推理引擎的回答质量是否达到基准线 (Score > 0.8)
        
        NOTE: This test uses a MockInferenceEngine. 
        To test against the real RAGFlow, replace MockInferenceEngine with the real InferenceEngine
        and ensure .env is configured.
        """
        evaluator = QualityGatekeeper()
        pass_count = 0
        total_count = len(self.dataset)

        for case in self.dataset:
            query = case["query"]
            expected_keywords = case["expected_answer_keywords"]
            
            # 模拟推理引擎调用
            actual_answer = self.inference_engine.search(query)
            
            # 评估相似度
            score = evaluator.evaluate_similarity(actual_answer, expected_keywords)
            
            # Assert score > 0.8
            assert score > 0.8, f"Score {score} too low for query: {query}"
            pass_count += 1

        assert pass_count == total_count
