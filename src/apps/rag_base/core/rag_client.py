import requests
import json
import os
from typing import Dict, Any, List, Optional
from src.common.logger import get_app_logger

logger = get_app_logger("rag_base")

class RAGClient:
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("RAGFLOW_API_KEY", "")
        self.base_url = config.get("RAGFLOW_HOST", "http://127.0.0.1:9380")
        self.chat_id = config.get("RAGFLOW_CHAT_ID", "")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        if not self.api_key:
            logger.warning("RAGFLOW_API_KEY is missing. RAG features will fail.")

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            data = response.json()
            if response.status_code >= 400 or data.get("code", 0) != 0:
                logger.error(f"RAGFlow API Error: {response.status_code} - {data}")
                return {"status": "error", "message": data.get("message", "Unknown error"), "code": data.get("code")}
            return {"status": "success", "data": data.get("data", data)}
        except Exception as e:
            logger.error(f"Failed to parse response: {e}, Content: {response.text}")
            return {"status": "error", "message": f"Response parsing failed: {str(e)}"}

    # --- Dataset Operations ---

    def create_dataset(self, name: str, avatar: str = "", description: str = "") -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/datasets"
        payload = {
            "name": name,
            "avatar": avatar,
            "description": description,
            "permission": "me",
            "document_count": 0,
            "chunk_count": 0,
            "parse_method": "general"
        }
        logger.info(f"Creating dataset: {name}")
        resp = requests.post(url, headers=self.headers, json=payload)
        return self._handle_response(resp)

    def delete_dataset(self, dataset_id: str) -> Dict[str, Any]:
        # Try RESTful delete first
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}"
        logger.info(f"Deleting dataset: {dataset_id}")
        resp = requests.delete(url, headers=self.headers)
        if resp.status_code == 404 or resp.status_code == 405:
             # Fallback to old style if needed, but let's stick to REST for v1
             pass
        return self._handle_response(resp)

    def list_datasets(self, page: int = 1, page_size: int = 30) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/datasets?page={page}&page_size={page_size}"
        logger.info(f"Listing datasets page {page}")
        resp = requests.get(url, headers=self.headers)
        return self._handle_response(resp)

    def update_dataset(self, dataset_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}"
        payload = {"name": name, "description": description}
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        logger.info(f"Updating dataset: {dataset_id}")
        resp = requests.put(url, headers=self.headers, json=payload)
        return self._handle_response(resp)

    # --- Document Operations ---

    def upload_document(self, dataset_id: str, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"File not found: {file_path}"}
            
        # API: POST /api/v1/datasets/{id}/documents
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents"
        filename = os.path.basename(file_path)
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f)}
                logger.info(f"Uploading {filename} to {dataset_id}")
                resp = requests.post(url, headers={"Authorization": self.headers["Authorization"]}, files=files)
                return self._handle_response(resp)
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return {"status": "error", "message": str(e)}

    def list_documents(self, dataset_id: str, page: int = 1, page_size: int = 30, keywords: str = "") -> Dict[str, Any]:
        # API: GET /api/v1/datasets/{id}/documents
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents?page={page}&page_size={page_size}&keywords={keywords}"
        logger.info(f"Listing documents for {dataset_id}")
        resp = requests.get(url, headers=self.headers)
        return self._handle_response(resp)

    def delete_document(self, dataset_id: str, document_id: str) -> Dict[str, Any]:
        # API: DELETE /api/v1/datasets/{dataset_id}/documents/{document_id}
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}"
        logger.info(f"Deleting document: {document_id}")
        resp = requests.delete(url, headers=self.headers)
        return self._handle_response(resp)
        
    def update_document(self, dataset_id: str, document_id: str, name: Optional[str] = None, enabled: Optional[bool] = None) -> Dict[str, Any]:
        """
        Update document metadata (rename or toggle status).
        API: PUT /api/v1/datasets/{dataset_id}/documents/{document_id}
        """
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}"
        payload = {}
        if name: payload["name"] = name
        if enabled is not None: payload["run_status"] = "1" if enabled else "0"
        
        logger.info(f"Updating document {document_id}: {payload}")
        resp = requests.put(url, headers=self.headers, json=payload)
        return self._handle_response(resp)

    def get_document_content(self, dataset_id: str, document_id: str) -> Dict[str, Any]:
        """
        Get parsed chunks of the document.
        API: GET /api/v1/datasets/{dataset_id}/documents/{document_id}/chunks
        """
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}/chunks"
        logger.info(f"Getting chunks for {document_id}")
        resp = requests.get(url, headers=self.headers)
        return self._handle_response(resp)

    def get_document_status(self, dataset_id: str, document_id: str) -> Dict[str, Any]:
         # Reusing list to get status if specific endpoint missing, or try GET detail
         url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}"
         resp = requests.get(url, headers=self.headers)
         return self._handle_response(resp)

    def retrieve_chunks(self, dataset_id: str, query: str, page: int = 1, page_size: int = 30, similarity_threshold: float = 0.2) -> Dict[str, Any]:
        """
        Retrieve chunks from a dataset without LLM generation.
        API: POST /api/v1/retrieval
        """
        url = f"{self.base_url}/api/v1/retrieval"
        payload = {
            "question": query,
            "dataset_ids": [dataset_id],
            "page": page,
            "page_size": page_size,
            "similarity_threshold": similarity_threshold,
            "vector_similarity_weight": 0.3,
            "top_k": 1024 
        }
        
        try:
            logger.info(f"Retrieving chunks from {dataset_id}: {url}")
            resp = requests.post(url, headers=self.headers, json=payload)
            
            if resp.status_code == 200:
                json_data = resp.json()
                if json_data.get("code") == 0:
                    data = json_data.get("data", {})
                    # Compatibility: some versions wrap in 'chunks'
                    if isinstance(data, dict) and "chunks" in data:
                        return {"status": "success", "data": data["chunks"]}
                    elif isinstance(data, list):
                        return {"status": "success", "data": data}
                    return {"status": "success", "data": []}
                else:
                    return {"status": "error", "message": json_data.get("message")}
            
            logger.error(f"RAGFlow Retrieve Chunks Error: {resp.status_code} - {resp.text}")
            return {"status": "error", "message": f"API Error: {resp.status_code}"}
            
        except Exception as e:
            logger.error(f"Retrieve Chunks Connection Error: {e}")
            return {"status": "error", "message": str(e)}

    # --- Retrieval / Scenario 1 ---

    def retrieve_and_answer(self, query: str) -> Dict[str, Any]:
        """
        Use RAGFlow Chat API to get an answer.
        Requires RAGFLOW_CHAT_ID to be set in .env.
        """
        if not self.chat_id:
            logger.warning("RAGFLOW_CHAT_ID not configured. Cannot perform chat retrieval.")
            return {"answer": "Error: RAGFLOW_CHAT_ID not configured.", "confidence": 0.0}

        url = f"{self.base_url}/api/v1/chat/completions"
        payload = {
            "chat_id": self.chat_id,
            "messages": [{"role": "user", "content": query}],
            "stream": False
        }
        
        try:
            logger.info(f"Querying RAGFlow Chat: {query[:30]}...")
            resp = requests.post(url, headers=self.headers, json=payload)
            result = self._handle_response(resp)
            
            if result["status"] == "success":
                # Assuming data structure: { "answer": "...", "reference": [...] }
                # RAGFlow API structure might vary, let's assume standard OpenAI-like or RAGFlow specific
                # RAGFlow usually returns 'data' object.
                data = result["data"]
                if isinstance(data, dict):
                     # Extract references safely
                     refs = data.get("reference", {})
                     confidence = 0.5 # Default
                     chunks = []
                     
                     if isinstance(refs, dict):
                         confidence = refs.get("total_similarity", 0.5)
                         chunks = refs.get("chunks", [])
                     elif isinstance(refs, list):
                         chunks = refs
                         if chunks:
                             # Use max similarity as confidence if available
                             try:
                                 confidence = max([float(c.get("similarity", 0)) for c in chunks])
                             except:
                                 confidence = 0.5

                     return {
                        "answer": data.get("answer", ""),
                        "confidence": confidence,
                        "references": chunks
                     }
                return {"answer": str(data), "confidence": 0.5, "references": []}
            else:
                return {"answer": f"Error: {result['message']}", "confidence": 0.0}
                
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {"answer": f"Exception: {str(e)}", "confidence": 0.0}
