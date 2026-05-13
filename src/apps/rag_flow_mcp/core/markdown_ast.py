import logging
import io
import pandas as pd
from typing import List, Tuple, Optional
from markdown_it import MarkdownIt
from markdown_it.token import Token

logger = logging.getLogger(__name__)

class MarkdownASTManager:
    def __init__(self):
        # Use gfm-like preset to support tables
        # Disable linkify to avoid extra dependency
        try:
            self.md = MarkdownIt("gfm-like", {"breaks": True, "html": True, "linkify": False})
        except KeyError:
            # Fallback if gfm-like is not found (older versions), though unlikely
            self.md = MarkdownIt("commonmark", {"breaks": True, "html": True}).enable('table')

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

    def update_table_cell(self, content: str, header_text: str, row_idx: int, col_idx: int, new_value: str, table_index: int = 0) -> str:
        """
        Update a specific cell in a markdown table located under a specific header.
        
        Args:
            content: Markdown content.
            header_text: Header text to locate the section.
            row_idx: 0-based index of the DATA row (excluding header).
            col_idx: 0-based index of the column.
            new_value: New string value for the cell.
            table_index: Index of the table within the section (default 0).
        """
        tokens = self.parse(content)
        line_range = self.find_section_range(tokens, header_text)
        
        if not line_range:
            logger.warning(f"Header '{header_text}' not found.")
            return content
            
        start_line, end_line = line_range
        
        # Find tables within section
        tables = []
        for i, token in enumerate(tokens):
            if token.type == "table_open" and token.map:
                t_start, t_end = token.map
                # Check if strictly within section
                if t_start >= start_line and t_end <= end_line:
                    tables.append((t_start, t_end))
        
        if not tables or table_index >= len(tables):
            logger.warning(f"Table index {table_index} not found in section '{header_text}'.")
            return content
            
        t_start, t_end = tables[table_index]
        
        # Extract lines
        lines = content.splitlines(keepends=False)
        table_lines = lines[t_start:t_end]
        
        # Clean up empty lines if any
        table_lines = [l for l in table_lines if l.strip()]
        
        if len(table_lines) < 2:
            return content
            
        # Parse manually to be robust
        try:
            # Prepare data for pandas
            # Strategy:
            # 1. Split header
            # 2. Skip separator
            # 3. Split rows
            
            def split_row(line):
                parts = line.split('|')
                # Remove empty first/last if they exist (standard pipe table style)
                if line.strip().startswith('|'):
                    parts = parts[1:]
                if line.strip().endswith('|'):
                    parts = parts[:-1]
                return [p.strip() for p in parts]

            headers = split_row(table_lines[0])
            data_rows = []
            
            # Skip index 1 (separator: |---|---|)
            # But ensure index 1 is actually separator? 
            # MarkdownIt identifies table, so it must be valid.
            
            for i in range(2, len(table_lines)):
                data_rows.append(split_row(table_lines[i]))
                
            # Update
            if row_idx < 0 or row_idx >= len(data_rows):
                logger.warning(f"Row index {row_idx} out of bounds.")
                return content
            
            row = data_rows[row_idx]
            if col_idx < 0 or col_idx >= len(row):
                 logger.warning(f"Col index {col_idx} out of bounds.")
                 return content
                 
            row[col_idx] = new_value
            
            # Reconstruct using pandas
            df = pd.DataFrame(data_rows, columns=headers)
            new_table_md = df.to_markdown(index=False, tablefmt="pipe")
            
            # Replace in original content
            original_lines_full = content.splitlines(keepends=True)
            
            new_output = []
            new_output.extend(original_lines_full[:t_start])
            # Ensure new table ends with newline
            if not new_table_md.endswith('\n'):
                new_table_md += '\n'
            new_output.append(new_table_md)
            new_output.extend(original_lines_full[t_end:])
            
            return "".join(new_output)
            
        except Exception as e:
            logger.error(f"Failed to update table: {e}")
            return content

