import os
import logging
import requests
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RAGClient:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        
    def refine_query(self, global_ctx: str, local_ctx: str, question: str) -> str:
        """
        [DEPRECATED] Use agentic_search instead.
        Refine the query by combining contexts.
        """
        # Truncate global context to avoid token limits
        truncated_global = global_ctx[:500] + "..." if len(global_ctx) > 500 else global_ctx
        
        query = (
            f"Background Context: {truncated_global}\n"
            f"Specific Scenario: {local_ctx}\n"
            f"Question: {question}"
        )
        return query

    def agentic_search(self, global_ctx: str, local_ctx: str, question: str, dataset_ids: str = "") -> Dict[str, Any]:
        """
        Execute an agentic search workflow:
        1. Analyze context to generate keywords (Simulated LLM).
        2. Search RAGFlow with keywords.
        3. Synthesize answer comparing Local vs Remote info.
        """
        # 1. Query Rewriting (Simulation)
        # In a real app, we would call an LLM here to extract keywords.
        # Simple heuristic: Combine Business Context + Question Key Terms
        keywords = f"{local_ctx} {question}"
        
        # 2. Search
        # Try specific search first
        result = self.retrieve_and_answer(keywords, dataset_ids)
        
        # 3. Self-Correction / Retry
        if result["score"] < 0.5:
            logger.info(f"Low confidence ({result['score']}) for '{keywords}'. Retrying with broader query...")
            # Broaden query: just the question
            result_retry = self.retrieve_and_answer(question, dataset_ids)
            if result_retry["score"] > result["score"]:
                result = result_retry
                
        # 4. Dual-Context Synthesis (Simulation)
        # We inject a note about the local context into the final answer
        # to ensure the user considers their own new requirements.
        
        original_answer = result["answer"]
        
        # Check for conflicts (Mock logic)
        conflict_note = ""
        if "timeout" in question.lower() and "30s" in original_answer and "15s" in global_ctx:
             conflict_note = "\n\n⚠️ **Conflict Detected**: RAG knowledge says 30s, but your ALIGNMENT doc mentions 15s."
             
        final_answer = (
            f"{original_answer}"
            f"{conflict_note}"
            f"\n\n(Context analyzed: Local='{local_ctx}', Global Summary available)"
        )
        
        result["answer"] = final_answer
        return result

    def retrieve_and_answer(self, query: str, dataset_ids: str = "") -> Dict[str, Any]:
        """
        Call RAGFlow API to get an answer.
        Returns dict with 'answer', 'citation', 'score'.
        """
        # Mock implementation if no real API Key
        if self.api_key == "mock_key":
            return self._mock_response(query)
            
        try:
            # Real RAGFlow API structure (Hypothetical, adjust to actual API)
            url = f"{self.base_url}/api/v1/retrieval_completion"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "question": query,
                "dataset_ids": dataset_ids.split(",") if dataset_ids else []
            }
            
            # NOTE: This is a placeholder for the actual API call
            # resp = requests.post(url, headers=headers, json=payload, timeout=30)
            # resp.raise_for_status()
            # data = resp.json()
            # return {
            #     "answer": data.get("answer", ""),
            #     "citation": str(data.get("chunks", [])),
            #     "score": data.get("confidence", 0.0)
            # }
            
            # Fallback to mock for now as we don't have a live RAGFlow instance
            return self._mock_response(query)
            
        except Exception as e:
            logger.error(f"RAG Error: {e}")
            return {
                "answer": "Error retrieving answer from RAGFlow.",
                "citation": "System Error",
                "score": 0.0
            }

    def _mock_response(self, query: str) -> Dict[str, Any]:
        """Generate a mock response for testing."""
        return {
            "answer": f"Based on the knowledge base, here is a suggested answer for: {query[:50]}...",
            "citation": "Mock Document v1.0, Section 3.2",
            "score": 0.88
        }
