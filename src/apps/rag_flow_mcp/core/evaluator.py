from typing import Dict, Any

class QualityEvaluator:
    def evaluate(self, question: str, rag_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the quality of the RAG answer.
        Returns a dict with 'is_valid', 'score', 'reason'.
        """
        score = rag_result.get("score", 0.0)
        answer = rag_result.get("answer", "")
        
        # Rule 1: Minimum confidence threshold
        if score < 0.3:
            return {
                "is_valid": False,
                "score": score,
                "reason": "Confidence too low"
            }
            
        # Rule 2: Refusal detection
        refusal_keywords = ["I don't know", "cannot answer", "no information", "无法回答", "没有信息"]
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
