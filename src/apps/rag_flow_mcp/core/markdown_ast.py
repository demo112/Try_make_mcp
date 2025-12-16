import logging
from typing import List, Tuple, Optional
from markdown_it import MarkdownIt
from markdown_it.token import Token

logger = logging.getLogger(__name__)

class MarkdownASTManager:
    def __init__(self):
        self.md = MarkdownIt("commonmark", {"breaks": True, "html": True})

    def parse(self, content: str) -> List[Token]:
        return self.md.parse(content)

    def find_section_range(self, tokens: List[Token], header_text: str) -> Optional[Tuple[int, int]]:
        """
        Find the line range (start_line, end_line) of a section under a specific header.
        Range includes the header itself and all content until the next header of same or higher level.
        Line numbers are 0-based.
        """
        start_line = -1
        end_line = -1
        header_level = -1
        
        # 1. Find the header
        for i, token in enumerate(tokens):
            if token.type == "heading_open":
                # Check next token for text content
                if i + 1 < len(tokens) and tokens[i+1].type == "inline":
                    if header_text in tokens[i+1].content:
                        start_line = token.map[0]
                        header_level = int(token.tag.replace("h", ""))
                        # Initial end_line guess: end of file or map[1]
                        end_line = token.map[1] 
                        
                        # Continue to find the actual end of section
                        # Iterate from this header onwards
                        for j in range(i + 1, len(tokens)):
                            next_token = tokens[j]
                            # Update end_line based on current token's map
                            if next_token.map:
                                end_line = max(end_line, next_token.map[1])
                                
                            if next_token.type == "heading_open":
                                next_level = int(next_token.tag.replace("h", ""))
                                if next_level <= header_level:
                                    # Found next header of same or higher level (e.g. h2 found h2 or h1)
                                    # Section ends at the start of this new header
                                    end_line = next_token.map[0]
                                    return (start_line, end_line)
                        
                        # If loop finishes, section goes to end of content
                        # We don't have total line count here easily, but we can infer from max map
                        return (start_line, end_line)
        
        return None

    def replace_section(self, content: str, header_text: str, new_content: str) -> str:
        """
        Replace the content of a section identified by header_text.
        Preserves the original header line(s).
        """
        tokens = self.parse(content)
        line_range = self.find_section_range(tokens, header_text)
        
        if not line_range:
            logger.warning(f"Header '{header_text}' not found.")
            return content
            
        start_line, end_line = line_range
        lines = content.splitlines(keepends=True)
        
        # Ensure lines list is long enough
        if start_line >= len(lines):
             return content

        # Find the header token to get its specific end line
        header_end_line = start_line + 1
        for token in tokens:
            if token.type == "heading_open" and token.map and token.map[0] == start_line:
                header_end_line = token.map[1]
                break
        
        # Safety check
        if header_end_line > end_line:
            header_end_line = end_line

        new_lines = []
        # Keep lines up to the end of the header
        new_lines.extend(lines[:header_end_line])
        
        # Ensure separation - REMOVED to avoid extra newlines
        # if new_content and not new_content.startswith('\n'):
        #     new_lines.append('\n')
            
        new_lines.append(new_content)
        
        if new_content and not new_content.endswith('\n'):
            new_lines.append('\n')
            
        new_lines.extend(lines[end_line:])
        
        return "".join(new_lines)

    def insert_after_section(self, content: str, header_text: str, content_to_insert: str) -> str:
        """
        Insert content at the end of a section.
        """
        tokens = self.parse(content)
        line_range = self.find_section_range(tokens, header_text)
        
        if not line_range:
            logger.warning(f"Header '{header_text}' not found.")
            return content
            
        _, end_line = line_range
        lines = content.splitlines(keepends=True)
        
        if not content_to_insert.endswith('\n'):
            content_to_insert += '\n'
            
        new_lines = []
        new_lines.extend(lines[:end_line])
        new_lines.append(content_to_insert)
        new_lines.extend(lines[end_line:])
        
        return "".join(new_lines)
