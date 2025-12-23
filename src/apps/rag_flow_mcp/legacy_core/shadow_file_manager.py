import shutil
import os
import time
from pathlib import Path
from src.common.logger import get_app_logger

logger = get_app_logger("rag_base")

class ShadowFileManager:
    @staticmethod
    def create_shadow_copy(file_path: str) -> str:
        """
        Creates a copy of the file with _ai_revision_{timestamp} suffix.
        Returns the absolute path of the shadow copy.
        """
        original_path = Path(file_path)
        if not original_path.exists():
            raise FileNotFoundError(f"Original file not found: {file_path}")

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        shadow_filename = f"{original_path.stem}_ai_revision_{timestamp}{original_path.suffix}"
        shadow_path = original_path.parent / shadow_filename

        try:
            shutil.copy2(original_path, shadow_path)
            logger.info(f"Created shadow copy: {shadow_path}")
            return str(shadow_path.absolute())
        except Exception as e:
            logger.error(f"Failed to create shadow copy: {e}")
            raise

    @staticmethod
    def read_file(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def write_file(file_path: str, content: str):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
