import re
from mcp.server.fastmcp import FastMCP
from src.common import get_app_logger
import os
import sys

# Ensure core modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import load_config
from core.doc_processor import DocumentProcessor
from core.rag_client import RAGClient
from core.evaluator import QualityEvaluator

# Initialize components
config = load_config()
logger = get_app_logger("rag_flow_mcp")
mcp = FastMCP("rag_flow_mcp")

doc_processor = DocumentProcessor()
rag_client = RAGClient(
    config["RAGFLOW_API_KEY"], 
    config["RAGFLOW_HOST"],
    config.get("RAGFLOW_CHAT_ID", "")
)
evaluator = QualityEvaluator()

@mcp.tool()
def process_review_doc(file_path: str, project_name: str) -> str:
    """
    Process a review document (e.g. 06_方案业务评审问题_*.md).
    It parses questions, queries RAGFlow, and injects AI suggestions.
    
    Args:
        file_path: Absolute path to the markdown file.
        project_name: Name of the project (to find context).
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
        
    try:
        # 1. Read Content
        content = doc_processor.read_file(file_path)
        
        # 2. Get Global Context
        # Assuming project docs are in docs/project_name/
        # We need to construct the project docs path. 
        # Since file_path is likely inside docs/project_name/..., we can infer or use the param.
        # Let's try to infer root docs path from file_path if possible, or just use project_name
        # For simplicity, we assume standard structure: root/docs/project_name/...
        
        # Heuristic to find project root in docs
        docs_root = os.path.join(os.getcwd(), "docs", project_name)
        global_ctx = doc_processor.extract_global_context(docs_root)
        
        # 3. Parse Questions
        questions = doc_processor.parse_questions(content)
        if not questions:
            return "No questions found in the document."
            
        answers_map = {}
        processed_count = 0
        
        # 4. Process Each Question
        for q in questions:
            # Use Agentic Search
            result = rag_client.agentic_search(
                global_ctx, 
                q["business_context"], 
                q["description"],
                config["RAG_DATASET_IDS"]
            )
            
            # Evaluate
            eval_res = evaluator.evaluate(q["description"], result)
            
            if eval_res["is_valid"]:
                answers_map[str(q["id"])] = result
                processed_count += 1
            else:
                logger.info(f"Skipped question {q['id']} due to low quality: {eval_res['reason']}")
                
        # 5. Write Back
        if answers_map:
            new_content = doc_processor.inject_ai_answers(content, answers_map)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return f"Successfully processed {processed_count} questions. File updated."
        else:
            return "No valid answers generated."
            
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def harvest_knowledge_candidates(file_path: str) -> str:
    """
    Analyze the review document to find discrepancies between AI suggestions and human answers.
    Generates a list of candidates for knowledge base updates.
    
    Args:
        file_path: Absolute path to the completed review document.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
        
    try:
        content = doc_processor.read_file(file_path)
        # We need a parser that extracts both AI Suggestion and Human Answer
        # For simplicity, let's assume we can regex them out from the blocks
        
        # Re-using parse logic but extending it (or doing ad-hoc regex here for the MVP)
        # Let's do a simple block split
        blocks = content.split("## ")[1:] # Skip preamble
        
        candidates = []
        
        for block in blocks:
            # Extract Title
            title_line = block.split('\n')[0]
            
            # Extract AI Suggestion
            ai_match = re.search(r'\*\*AI 参考建议\*\*：\n> .+?\n> (.+?)\n', block, re.DOTALL)
            ai_text = ai_match.group(1).strip() if ai_match else "N/A"
            
            # Extract Human Answer
            human_match = re.search(r'\*\*回答\*\*：(.+?)(\n##|\Z)', block, re.DOTALL)
            human_text = human_match.group(1).strip() if human_match else ""
            
            # Logic: If Human Answer is present AND (AI is N/A OR Differs)
            if human_text:
                is_diff = False
                reason = ""
                
                if ai_text == "N/A":
                    is_diff = True
                    reason = "New Knowledge (AI missed)"
                elif len(human_text) > 10 and human_text != ai_text:
                    # Very naive diff: exact match. In reality, use semantic similarity.
                    # Here we just assume if they are different strings, it's a candidate.
                    # To reduce noise, we only flag if lengths differ significantly or keywords differ.
                    # For MVP, let's just flag it.
                    is_diff = True
                    reason = "Knowledge Update (Conflict/Refinement)"
                
                if is_diff:
                    candidates.append({
                        "title": title_line,
                        "human_answer": human_text,
                        "ai_suggestion": ai_text,
                        "reason": reason
                    })
        
        if not candidates:
            return "No knowledge update candidates found. AI and Human answers align (or no human answers yet)."
            
        # Format Report
        report = ["# Knowledge Update Candidates\n"]
        for c in candidates:
            report.append(f"## {c['title']}")
            report.append(f"- **Reason**: {c['reason']}")
            report.append(f"- **Old Knowledge**: {c['ai_suggestion'][:100]}...")
            report.append(f"- **New Knowledge**: {c['human_answer']}")
            report.append("")
            
        return "\n".join(report)
        
    except Exception as e:
        logger.error(f"Harvest failed: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def consolidate_knowledge(staging_dir: str, topic: str) -> str:
    # 1. Gather all fragments related to the topic
    # For MVP, we just read a single staging file, but logically this should scan multiple.
    staging_file = os.path.join(staging_dir, f"{topic}_staging.md")
    if not os.path.exists(staging_file):
        return f"No staging file found for topic: {topic}"
        
    content = doc_processor.read_file(staging_file)
    
    # 2. Call LLM to consolidate (Simulation)
    # In real impl, we send `content` to LLM with instructions to rewrite as a spec.
    
    consolidated_doc = f"""# {topic} Consolidated Specification
> Generated by AI Consolidator from {len(content.split('##'))-1} fragments.

## 1. Overview
This document consolidates recent decisions regarding {topic}.

## 2. Key Specifications
(Simulated LLM Output based on fragments)
- Specification A derived from fragments...
- Specification B derived from fragments...

## 3. Conflict Resolution
- Resolved conflict between Q1 and Q5 by prioritizing Q5 (newer).

---
**Approval Status**: [ ] Draft  [ ] Approved
"""

    output_path = os.path.join(staging_dir, f"{topic}_Consolidated_v1.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(consolidated_doc)
        
    return f"Consolidated document generated at: {output_path}. Please review and approve."

if __name__ == "__main__":
    mcp.run()