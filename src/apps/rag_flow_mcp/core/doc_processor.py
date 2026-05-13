import re
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        pass

    def read_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_metadata(self, content: str) -> Dict[str, str]:
        """
        Extract metadata from YAML frontmatter or implied context.
        Example Frontmatter:
        ---
        product: Payment
        module: Gateway
        ---
        """
        metadata = {"product": "General", "module": "General"}
        
        # Simple YAML-like parsing between first two ---
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            yaml_block = match.group(1)
            for line in yaml_block.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    metadata[key.strip().lower()] = val.strip()
        
        return metadata

    def parse_questions(self, content: str) -> List[Dict]:
        """
        Parse questions from the markdown content.
        Returns a list of dicts with:
        - id: question index
        - title: question title
        - description: question description
        - business_context: business context
        - raw_block: the full text block for this question
        """
        questions = []
        
        # Regex to match ## [index].[title] blocks
        # We assume the block ends at the next ## header or end of file
        pattern = re.compile(r'(##\s+(\d+)\.(.+?)\n)(.*?)(?=\n##\s+\d+\.|\Z)', re.DOTALL)
        
        matches = pattern.findall(content)
        
        for header, idx, title, body in matches:
            q_data = {
                "id": idx,
                "title": title.strip(),
                "full_block": header + body
            }
            
            # Extract fields
            desc_match = re.search(r'\*\*问题描述\*\*：(.*?)\n\*\*', body, re.DOTALL)
            ctx_match = re.search(r'\*\*业务上下文\*\*：(.*?)\n\*\*', body, re.DOTALL)
            
            q_data["description"] = desc_match.group(1).strip() if desc_match else ""
            q_data["business_context"] = ctx_match.group(1).strip() if ctx_match else ""
            
            questions.append(q_data)
            
        return questions

    def inject_ai_answers(self, content: str, answers_map: Dict[str, Dict]) -> str:
        """
        Inject AI answers into the content.
        answers_map: { question_id: { "answer": str, "citation": str, "score": float } }
        """
        
        # We iterate through the file and replace blocks. 
        # But a safer way is to use regex substitution for each question block
        
        new_content = content
        
        for q_id, ans_data in answers_map.items():
            # Construct the AI answer block
            score_str = f"{ans_data.get('score', 0.0) * 100:.0f}%"
            ai_block = (
                f"\n**AI 参考建议**：\n"
                f"> 🤖 **RAG自动回复** (置信度: {score_str})\n"
                f"> {ans_data['answer']}\n"
                f">\n"
                f"> *来源: {ans_data.get('citation', 'Unknown')}*\n"
            )
            
            # Regex to find the insertion point for this specific question
            # We look for the block starting with ## q_id.
            # And then inside that block, we look for **回答**
            # We want to insert BEFORE **回答**
            
            # Pattern explanation:
            # (##\s+q_id\..+?)  -> Match header (Group 1)
            # (.*?)             -> Match content before target (Group 2)
            # (?<!\*\*AI 参考建议\*\*：\n) -> Negative lookbehind to avoid double insertion (Hard to do with var length)
            # instead, we will check if "AI 参考建议" exists in the block
            
            # Simpler approach: Locate the specific header, then find the first "**回答**" after it.
            
            header_pattern = re.compile(fr'(##\s+{q_id}\..+?)(?=\n##\s+\d+\.|\Z)', re.DOTALL)
            match = header_pattern.search(new_content)
            
            if match:
                full_block = match.group(0)
                
                # Check if already has AI answer
                if "**AI 参考建议**" in full_block:
                    # Update existing
                    # Regex to replace existing AI block
                    # Assumes AI block ends before **回答** or next field
                    update_pattern = re.compile(r'(\*\*AI 参考建议\*\*：\n.+?)(?=\n\*\*回答\*\*)', re.DOTALL)
                    updated_block = update_pattern.sub(ai_block.strip(), full_block)
                else:
                    # Insert new
                    # Find **回答**
                    if "**回答**" in full_block:
                        updated_block = full_block.replace("**回答**", ai_block + "\n**回答**")
                    else:
                        # Fallback: append to end if no Answer field (should not happen in standard doc)
                        updated_block = full_block + "\n" + ai_block
                
                # Replace the block in the main content
                new_content = new_content.replace(full_block, updated_block)
                
        return new_content

    def extract_global_context(self, project_path: str) -> str:
        """
        Try to find ALIGNMENT or CONSENSUS docs in the project to extract global context.
        project_path: e.g. docs/MyProject/
        """
        p = Path(project_path)
        context = []
        
        # Check 01_Align
        align_dir = p / "01_Align"
        if align_dir.exists():
            for f in align_dir.glob("*.md"):
                context.append(f"--- From {f.name} ---")
                try:
                    content = f.read_text(encoding='utf-8')
                    # Take first 1000 chars as summary
                    context.append(content[:1000] + "...")
                except Exception:
                    pass
                    
        return "\n".join(context)
