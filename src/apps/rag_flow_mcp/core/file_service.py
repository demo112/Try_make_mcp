import os
import logging
from typing import Tuple, Optional, List
from .shadow_file_manager import ShadowFileManager

logger = logging.getLogger(__name__)

class FileService:
    """
    文件服务 (File Service)
    
    职责: 统一处理所有文件 I/O 操作，实现逻辑层与物理层的解耦。
    """
    
    def __init__(self):
        self.shadow_manager = ShadowFileManager()
        
    def read_text(self, file_path: str) -> str:
        """读取文本文件内容"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    def write_text(self, file_path: str, content: str) -> None:
        """写入文本文件内容 (直接写入，慎用)"""
        self.ensure_dir(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def create_shadow_copy(self, file_path: str, content: str) -> Tuple[str, str]:
        """创建影子副本 (安全写入)"""
        return self.shadow_manager.generate_shadow_copy(file_path, content)
        
    def exists(self, path: str) -> bool:
        """检查路径是否存在"""
        return os.path.exists(path)
        
    def ensure_dir(self, dir_path: str) -> None:
        """确保目录存在"""
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            
    def list_files(self, dir_path: str, pattern: str = "*") -> List[str]:
        """列出目录下的文件 (简单的 glob)"""
        import glob
        if not os.path.exists(dir_path):
            return []
        return glob.glob(os.path.join(dir_path, pattern))

    def write_json(self, file_path: str, data: dict) -> None:
        """写入 JSON 文件"""
        import json
        self.ensure_dir(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
