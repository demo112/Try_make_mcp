import os
import logging
import requests
import json
from typing import Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class RAGClient:
    def __init__(self, api_key: str, base_url: str, chat_id: str = ""):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.chat_id = chat_id
        
        logger.info(f"RAGClient initialized with Base URL: {self.base_url}, Chat ID: {self.chat_id}")

        # Configure session with retries
        self.session = requests.Session()
        # Disable proxy usage to ensure local/LAN connections work reliably
        self.session.trust_env = False
        
        retries = Retry(
            total=1,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        
        # Default timeout
        self.timeout = 120

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
        
        # Enforce "Single Question Focus" via prompt engineering (if LLM were used here)
        # Since we pass 'keywords' to RAG, we append a strict instruction to the query itself
        # to guide the RAG/LLM backend.
        strict_query = f"{question}\n\n[System Instruction: You MUST answer ONLY the specific question above. Do NOT merge with other topics. Do NOT hallucinate.]"
        
        # 2. Search
        # Try specific search first
        result = self.retrieve_and_answer(strict_query, dataset_ids)
        
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
            # Removed debug context info to keep output clean as per user request
        )
        
        result["answer"] = final_answer
        return result

    def retrieve_and_answer(self, query: str, dataset_ids: str = "") -> Dict[str, Any]:
        """
        Call RAGFlow API to get an answer.
        Returns dict with 'answer', 'citation', 'score'.
        """
        # If API key is explicitly set to mock or default, use mock
        if self.api_key == "mock_key":
            return self._mock_response(query)
            
        try:
            # RAGFlow API v1 Implementation
            # Endpoint: /api/v1/chats_openai/{chat_id}/chat/completions
            
            if not self.chat_id:
                return {
                    "answer": "Error: RAGFLOW_CHAT_ID is not configured.",
                    "citation": "Config Error",
                    "score": 0.0
                }
            
            url = f"{self.base_url}/api/v1/chats_openai/{self.chat_id}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Payload construction
            # RAGFlow typically expects 'question' and 'stream' inside the body
            # And 'quote' to get citations.
            # Using standard OpenAI-like structure: messages
            payload = {
                "model": "ragflow",  # Required by API but ignored
                "messages": [{"role": "user", "content": query}],
                "stream": False,
                "quote": True
            }
            
            # If specific datasets are required, RAGFlow usually handles this via 
            # the conversation ID or session. 
            # If this is a stateless call, we might need to pass dataset_ids if the API supports it.
            # For now, we assume the API Key is bound to a specific tenant/knowledge base context 
            # OR we pass it in payload if documented. 
            # Let's try passing it if provided.
            if dataset_ids:
                 ids_list = dataset_ids.split(",")
                 payload["dataset_ids"] = ids_list
                 logger.info(f"Using dataset_ids: {ids_list}")

            logger.info(f"Sending request to RAGFlow: {url}")
            resp = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            
            if resp.status_code != 200:
                logger.error(f"RAGFlow API Error: {resp.status_code} - {resp.text}")
                return {
                    "answer": f"Error: RAGFlow returned {resp.status_code} - {resp.text[:200]}",
                    "citation": "API Error",
                    "score": 0.0
                }
                
            data = resp.json()
            logger.info(f"RAGFlow Response: {data}")
            
            if not isinstance(data, dict):
                 return {
                    "answer": f"Unexpected Response Format: {type(data)}",
                    "citation": "API Error",
                    "score": 0.0
                }

            if data.get("code", 0) != 0:
                 msg = data.get('message', 'Unknown error')
                 if "Model(@None)" in msg:
                     msg += " (Hint: Please configure an LLM model for this Chat Assistant in RAGFlow UI)"
                 return {
                    "answer": f"RAGFlow Error: {msg}",
                    "citation": "API Error",
                    "score": 0.0
                }
            # { "choices": [ { "message": { "content": "..." } } ], "code": 0 }
            # Wait, if it's OpenAI compatible, it might not have "code": 0 at top level if success.
            # But RAGFlow wrapper might add it.
            
            answer = ""
            citations = []
            
            if "choices" in data and len(data["choices"]) > 0:
                answer = data["choices"][0].get("message", {}).get("content", "")
            
            # Check for top-level code error (RAGFlow specific) if answer is empty
            if not answer and data.get("code", 0) != 0:
                 msg = data.get('message', 'Unknown error')
                 if "Model(@None)" in msg:
                     msg += " (Hint: Please configure an LLM model for this Chat Assistant in RAGFlow UI)"
                 return {
                    "answer": f"RAGFlow Error: {msg}",
                    "citation": "API Error",
                    "score": 0.0
                }
            # RAGFlow might return it in a different way or in the content?
            # Based on docs, if quote=True, it might be in 'reference' field of data if it's not strictly OpenAI?
            # Or maybe inside the message?
            # Let's check if 'data' has 'reference' (some implementations do this).
            
            # Fallback: Check standard RAGFlow 'data' field if the structure is mixed
            result_data = data.get("data") or {}
            if not answer and "answer" in result_data:
                answer = result_data["answer"]
                
            # Refs
            refs = result_data.get("reference", [])
            # Also check if refs are in data root (some versions)
            if not refs and "reference" in data:
                refs = data["reference"]
                
            score = 0.8 if refs else 0.3
            
            if isinstance(refs, list):
                for r in refs:
                    if isinstance(r, dict):
                        doc_name = r.get("doc_name", "Unknown")
                        citations.append(doc_name)
                    elif isinstance(r, str):
                        citations.append(r)
            
            citation_str = ", ".join(citations[:3]) if citations else "No citation"
            
            return {
                "answer": answer,
                "citation": citation_str,
                "score": score
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"RAG Connection Error: {e}")
            return {
                "answer": f"Connection Error: {str(e)}",
                "citation": "System Error",
                "score": 0.0
            }

    def list_datasets(self, page: int = 1, page_size: int = 30) -> Dict[str, Any]:
        """
        List all knowledge bases (datasets).
        API: GET /api/v1/datasets
        """
        if self.api_key == "mock_key":
            return {"data": [{"id": "mock_id", "name": "Mock KB"}], "total": 1}

        try:
            url = f"{self.base_url}/api/v1/datasets?page={page}&page_size={page_size}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            logger.info(f"Listing datasets: {url}")
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            
            if resp.status_code != 200:
                logger.error(f"RAGFlow List Datasets Error: {resp.status_code} - {resp.text}")
                return {"error": f"API Error: {resp.status_code}", "details": resp.text}
                
            return resp.json()
            
        except Exception as e:
            logger.error(f"List Datasets Connection Error: {e}")
            return {"error": str(e)}

    def list_documents(self, dataset_id: str, page: int = 1, page_size: int = 30, keywords: str = "") -> Dict[str, Any]:
        """
        List documents in a specific knowledge base.
        API: GET /api/v1/datasets/{dataset_id}/documents
        """
        if self.api_key == "mock_key":
             return {"data": [{"id": "doc1", "name": "test.pdf"}], "total": 1}

        try:
            url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents?page={page}&page_size={page_size}&keywords={keywords}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            logger.info(f"Listing documents for {dataset_id}: {url}")
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            
            if resp.status_code != 200:
                logger.error(f"RAGFlow List Documents Error: {resp.status_code} - {resp.text}")
                return {"error": f"API Error: {resp.status_code}", "details": resp.text}
                
            return resp.json()
            
        except Exception as e:
            logger.error(f"List Documents Connection Error: {e}")
            return {"error": str(e)}

    def upload_document(self, dataset_id: str, file_path: str) -> Dict[str, Any]:
        """
        Upload a document to the knowledge base.
        API: POST /api/v1/datasets/{dataset_id}/documents
        """
        if self.api_key == "mock_key":
            return {"code": 0, "message": "Mock upload success"}

        try:
            url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            logger.info(f"Uploading document to {dataset_id}: {file_path}")
            
            # Using multipart/form-data for file upload
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                # Note: Do not set Content-Type header when using 'files' param in requests, 
                # it will be set automatically with boundary.
                resp = self.session.post(url, headers=headers, files=files, timeout=self.timeout)
            
            if resp.status_code != 200:
                logger.error(f"RAGFlow Upload Error: {resp.status_code} - {resp.text}")
                return {"error": f"API Error: {resp.status_code}", "details": resp.text}
                
            return resp.json()
            
        except Exception as e:
            logger.error(f"Upload Document Connection Error: {e}")
            return {"error": str(e)}

    def retrieve_chunks(self, dataset_id: str, query: str, page: int = 1, page_size: int = 30, similarity_threshold: float = 0.2) -> Dict[str, Any]:
        """
        Retrieve chunks from a dataset without LLM generation.
        API: POST /api/v1/retrieval
        """
        if self.api_key == "mock_key":
             return {"data": [{"content_with_weight": "Mock content", "similarity": 0.9}], "total": 1}

        try:
            # Correct Endpoint based on GitHub Issues: POST /api/v1/retrieval
            url = f"{self.base_url}/api/v1/retrieval"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "question": query,
                "dataset_ids": [dataset_id],
                "page": page,
                "page_size": page_size,
                "similarity_threshold": similarity_threshold,
                "vector_similarity_weight": 0.3,
                "top_k": 1024 
            }
            
            logger.info(f"Retrieving chunks from {dataset_id}: {url}")
            resp = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            
            if resp.status_code == 200:
                json_data = resp.json()
                # 兼容性修复：某些版本返回 {"code":0, "data": {"chunks": [...]}} 而不是 {"code":0, "data": [...]}
                if isinstance(json_data.get("data"), dict) and "chunks" in json_data["data"]:
                     # 转换结构以保持统一
                     json_data["data"] = json_data["data"]["chunks"]
                return json_data
            
            logger.error(f"RAGFlow Retrieve Chunks Error: {resp.status_code} - {resp.text}")
            return {"error": f"API Error: {resp.status_code}", "details": resp.text}
            
        except Exception as e:
            logger.error(f"Retrieve Chunks Connection Error: {e}")
            return {"error": str(e)}

    def _mock_response(self, query: str) -> Dict[str, Any]:
        """Generate a mock response for testing."""
        return {
            "answer": f"Based on the knowledge base, here is a suggested answer for: {query[:50]}...",
            "citation": "Mock Document v1.0, Section 3.2",
            "score": 0.88
        }
