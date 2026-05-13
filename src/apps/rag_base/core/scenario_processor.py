import re
import json
from typing import Dict, Any, List, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.apps.rag_base.core.rag_client import RAGClient
from src.apps.rag_base.core.shadow_file_manager import ShadowFileManager
from src.apps.rag_base.core.prompts import get_prompts
from src.common.logger import get_app_logger

logger = get_app_logger("rag_base")

class ScenarioProcessor:
    def __init__(self, rag_client: RAGClient):
        self.rag_client = rag_client
        self.prompts = get_prompts()

    def create_shadow_file(self, doc_path: str) -> str:
        """Atomic Tool: Create a shadow copy of the document."""
        return ShadowFileManager.create_shadow_copy(doc_path)

    def extract_questions(self, doc_path: str) -> List[Dict[str, Any]]:
        """Atomic Tool: Extract questions from the document using Field-Based Context."""
        content = ShadowFileManager.read_file(doc_path)
        lines = content.split('\n')
        
        questions: List[Dict[str, Any]] = []
        in_code_block = False
        current_question = None
        
        for idx, line in enumerate(lines):
            stripped = line.strip()
            
            # 1. Skip Code Blocks
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            
            # 2. Header Detection (Start of a new logical block)
            header_match = re.match(r'^(#{1,6})\s+(.*)', line)
            if header_match:
                # Save previous question if valid
                if current_question:
                    questions.append(current_question)
                    current_question = None
                
                header_text = header_match.group(2).strip()
                # Heuristic: If header itself is a question
                if '?' in header_text or '？' in header_text or header_text.lower().startswith("question"):
                    current_question = {"line_index": idx, "text": header_text, "context": []}
                else:
                    # Potential question container, keep scanning fields
                    current_question = {"line_index": idx, "text": header_text, "context": [], "is_header_question": False}
                continue
            
            # 3. Field Extraction (Context within the block)
            # Looks for "- Key: Value" or "Key: Value" patterns
            if current_question:
                # Field Match: "- 描述: ...", "- Description: ...", "问题: ..."
                field_match = re.match(r'^[-*]?\s*(描述|问题|Description|Question|Context)[:：]\s*(.*)', stripped, re.IGNORECASE)
                if field_match:
                    content_val = field_match.group(2).strip()
                    if content_val:
                        current_question["context"].append(content_val)
                        # If the header wasn't a question, maybe this field makes it one?
                        # But for now, we just append to context.
                
                # Stop if empty line? No, allow empty lines.
                # Stop at next header is handled by step 2.

        # Append last one
        if current_question:
            questions.append(current_question)
            
        # Filter: Only keep items that are questions or have question-like fields
        final_questions = []
        for q in questions:
            # Construct full query
            # Priority: Header text if it's a question, otherwise join context
            full_text = q['text']
            if q.get('context'):
                full_text += " " + " ".join(q['context'])
            
            # Simple heuristic to decide if it's worth asking
            # 1. Header has '?'
            # 2. Or explicit "Question/问题" field found (implied by context presence if we strictly filtered fields)
            # Let's be permissive: if header looks like question OR we found context fields.
            is_valid = ('?' in q['text'] or '？' in q['text'] or q.get('context'))
            
            if is_valid:
                # Store the FULL enriched text for retrieval, but keep line_index of the header
                final_questions.append({
                    "line_index": q['line_index'],
                    "text": full_text
                })
                logger.info(f"Extracted Question at {q['line_index']}: {full_text[:50]}...")
        
        return final_questions

    def retrieve_rag_suggestion(self, query: str, dataset_id: str = "") -> Dict[str, Any]:
        """Atomic Tool: Retrieve a single suggestion.
        
        Args:
            query: The query/question text.
            dataset_id: Optional dataset ID.
        """
        
        # 1. Pre-processing
        cleaned_query = ""
        if dataset_id:
            # MCP-side LLM Preprocessing
            sys_prompt = self.prompts["preprocess_system_prompt"]
            cleaned_query = self.rag_client.call_llm(sys_prompt, query)
            if not cleaned_query:
                 # Fallback to rule-based if LLM fails
                 cleaned_query = re.sub(r'^[\#\-\*\d\.\s]+', '', query).strip()
            logger.info(f"LLM Query Rewrite: '{query[:30]}...' -> '{cleaned_query}'")
        else:
            # Regex Fallback
            # Note: Primary query rewriting should be done by the Client/Agent before calling this tool.
            # This regex is a safety net for raw calls.
            cleaned_query = re.sub(r'^[\#\-\*\d\.\s]+', '', query).strip()
            cleaned_query = re.sub(r'^(Question|问题|Description|描述)[:：]\s*', '', cleaned_query, flags=re.IGNORECASE).strip()
            logger.info(f"Query Cleaning: '{query[:30]}...' -> '{cleaned_query[:30]}...'")
        
        # 2. Retrieve & Answer
        if dataset_id:
            # MCP-side Orchestration (Retrieve Chunks -> LLM Synthesis)
            chunk_result = self.rag_client.retrieve_chunks(dataset_id, cleaned_query)
            chunks = []
            if chunk_result.get("status") == "success":
                chunks = chunk_result.get("data", [])
            
            if not chunks:
                return {"suggestion": "", "confidence": 0.0, "skipped": True}
            
            # Prepare Context
            context_text = "\n\n".join([f"Fragment {i+1}: {c.get('content_with_weight', c.get('content', ''))}" for i, c in enumerate(chunks)])
            
            # Synthesize Answer
            sys_prompt = self.prompts["synthesis_system_prompt"]
            user_prompt = f"上下文片段：\n{context_text}\n\n问题：{query}"
            
            answer_text = self.rag_client.call_llm(sys_prompt, user_prompt)
            
            # Calculate confidence (Max chunk similarity as proxy)
            confidence = 0.0
            try:
                if chunks:
                    confidence = max([float(c.get("similarity", 0)) for c in chunks])
            except:
                confidence = 0.5
            
            result = {
                "answer": answer_text,
                "confidence": confidence,
                "references": chunks
            }
        else:
            # Legacy RAGFlow Chat
            result = self.rag_client.retrieve_and_answer(cleaned_query)

        
        if result['confidence'] < 0.2:
            return {"suggestion": "", "confidence": result['confidence'], "skipped": True}

        answer_text = result['answer']
        # Filter out "No relevant info" responses if LLM returns them
        if "无相关信息" in answer_text or "No relevant information" in answer_text:
             return {"suggestion": "", "confidence": 0.0, "skipped": True}

        refs = result.get('references', [])
        
        # Format References
        ref_text = ""
        if refs:
            doc_names = set()
            for r in refs:
                if isinstance(r, dict):
                    # Try to find document name
                    name = r.get('doc_name') or r.get('document_name')
                    if name:
                        doc_names.add(name)
            
            if doc_names:
                ref_str = ", ".join(sorted(doc_names))
                ref_text = f"\n> *Sources: {ref_str}*"
        
        answer_block = (
            f"\n> 💡 **AI Suggestion** (Confidence: {result['confidence']:.2f})\n"
            f"> {answer_text.replace(chr(10), chr(10)+'> ')}"
            f"{ref_text}\n"
        )
        return {
            "suggestion": answer_block,
            "confidence": result['confidence'],
            "skipped": False
        }

    def apply_suggestions(self, doc_path: str, suggestions_map: Dict[Union[int, str], str]) -> str:
        """Atomic Tool: Apply suggestions to the document."""
        content = ShadowFileManager.read_file(doc_path)
        lines = content.split('\n')
        new_lines = []
        
        # Ensure keys are integers
        int_map = {}
        for k, v in suggestions_map.items():
            try:
                int_map[int(k)] = v
            except ValueError:
                logger.warning(f"Invalid line index in suggestions_map: {k}")

        for idx, line in enumerate(lines):
            new_lines.append(line)
            if idx in int_map:
                new_lines.append(int_map[idx])
        
        ShadowFileManager.write_file(doc_path, '\n'.join(new_lines))
        return doc_path

    def process_clarification_suggestions(self, doc_path: str, dataset_id: str) -> Dict[str, Any]:
        """
        Scenario 1 Controller: Orchestrates the atomic tools.
        """
        try:
            # 1. Create Shadow Copy
            shadow_path = self.create_shadow_file(doc_path)
            
            # 2. Extract Questions
            questions = self.extract_questions(shadow_path)
            
            # 3. Parallel Retrieval
            suggestions_map: Dict[int, str] = {}
            if questions:
                logger.info(f"Processing {len(questions)} questions in parallel...")
                with ThreadPoolExecutor(max_workers=5) as executor:
                    # Submit tasks
                    future_to_idx = {
                        executor.submit(self.retrieve_rag_suggestion, q['text'], dataset_id): q['line_index']
                        for q in questions
                    }
                    
                    for future in as_completed(future_to_idx):
                        idx = future_to_idx[future]
                        try:
                            res = future.result()
                            if not res.get('skipped'):
                                suggestions_map[idx] = res['suggestion']
                        except Exception as exc:
                            logger.error(f"Retrieval failed for line {idx}: {exc}")

            # 4. Apply Suggestions
            if suggestions_map:
                self.apply_suggestions(shadow_path, suggestions_map)
                msg = f"Filled {len(suggestions_map)} suggestions into shadow file."
            else:
                msg = "No high-confidence suggestions found."
            
            return {
                "status": "success", 
                "original_file": doc_path,
                "shadow_file": shadow_path,
                "message": msg
            }
            
        except Exception as e:
            logger.error(f"Scenario processing failed: {e}")
            return {"status": "error", "message": str(e)}
