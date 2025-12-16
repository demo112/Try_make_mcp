from typing import Dict, Any, List
import logging
# from litellm import completion # Commented out to avoid dependency issues if API key not set
import difflib

logger = logging.getLogger(__name__)

class QualityEvaluator:
    def evaluate(self, question: str, rag_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the quality of the RAG answer (Runtime check).
        Returns a dict with 'is_valid', 'score', 'reason'.
        """
        score = rag_result.get("score", 0.0)
        answer = rag_result.get("answer", "")
        
        # Rule 1: Minimum confidence threshold (Runtime)
        if score < 0.6: # Increased threshold per P0 requirements
            return {
                "is_valid": False,
                "score": score,
                "reason": "Confidence too low (< 0.6)"
            }
            
        # Rule 2: Refusal detection
        refusal_keywords = ["I don't know", "cannot answer", "no information", "无法回答", "没有信息", "未找到"]
        if any(kw in answer for kw in refusal_keywords):
            return {
                "is_valid": False,
                "score": 0.1,
                "reason": "Model refused to answer"
            }
            
        return {
            "is_valid": True,
            "score": score,
            "reason": "Pass"
        }

class QualityGatekeeper:
    """
    Used for CI/CD Testing (Golden Dataset Verification).
    """
    def evaluate_similarity(self, actual: str, expected_keywords: List[str]) -> float:
        """
        Evaluate if the actual answer covers the expected keywords.
        Simple implementation: Recall rate of keywords.
        """
        if not expected_keywords:
            return 1.0
            
        actual_lower = actual.lower()
        matched_count = 0
        
        for kw in expected_keywords:
            if kw.lower() in actual_lower:
                matched_count += 1
                
        score = matched_count / len(expected_keywords)
        return score
