import json
import os
import sys
from typing import Dict, Any, Optional

def load_config(default_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    加载配置。优先读取 EXE 同目录下的 config.json。
    如果文件不存在，返回 default_config。
    """
    # 获取 EXE 所在目录 (如果是脚本运行则是 CWD)
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.getcwd()
        
    config_path = os.path.join(base_path, 'config.json')
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                print(f"Loading config from {config_path}")
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config.json: {e}")
            
    return default_config or {}
