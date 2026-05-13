import os
import difflib
import time
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

class ShadowFileManager:
    def __init__(self):
        pass

    def generate_shadow_copy(self, original_path: str, new_content: str) -> Tuple[str, str]:
        """
        Create a shadow copy of the file with new content and a diff report.
        
        Args:
            original_path: Path to the original file.
            new_content: The new content to write.
            
        Returns:
            Tuple[str, str]: (path_to_shadow_file, path_to_diff_report)
        """
        if not os.path.exists(original_path):
            raise FileNotFoundError(f"Original file not found: {original_path}")

        # 1. Read original content
        with open(original_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # 2. Generate file paths
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(original_path)
        shadow_path = f"{base}_ai_revision_{timestamp}{ext}"
        diff_path = f"{base}_diff_{timestamp}.md"

        # 3. Write shadow file
        with open(shadow_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        logger.info(f"Shadow copy created: {shadow_path}")

        # 4. Generate Diff Report
        diff_content = self._generate_diff_report(original_content, new_content, original_path, shadow_path)
        with open(diff_path, 'w', encoding='utf-8') as f:
            f.write(diff_content)
        logger.info(f"Diff report created: {diff_path}")

        return shadow_path, diff_path

    def _generate_diff_report(self, old: str, new: str, old_path: str, new_path: str) -> str:
        """
        Generate a Markdown formatted diff report.
        """
        old_lines = old.splitlines()
        new_lines = new.splitlines()
        
        diff = difflib.unified_diff(
            old_lines, 
            new_lines, 
            fromfile=os.path.basename(old_path), 
            tofile=os.path.basename(new_path),
            lineterm=''
        )
        
        report = []
        report.append(f"# Diff Report: {os.path.basename(old_path)}")
        report.append(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Source**: `{old_path}`")
        report.append(f"**Revision**: `{new_path}`")
        report.append("")
        report.append("## Changes")
        report.append("```diff")
        
        for line in diff:
            report.append(line)
            
        report.append("```")
        report.append("")
        report.append("## Action")
        report.append("- [ ] Review changes above.")
        report.append("- [ ] Use a merge tool (like VS Code 'Compare Selected') to apply changes.")
        
        return "\n".join(report)
