# 架构设计：MCP交付规范升级

## 1. 核心流程变更

### 1.1 初始化流程 (`init_app`)
1.  创建应用目录 `src/apps/{app_name}`。
2.  生成 `server.py` (更新模板：增加配置读取逻辑)。
3.  **新增**: 生成 `config.json` (默认配置模板)。
4.  创建文档目录 `docs/{display_name}`。
5.  **新增**: 生成 `UserManual.md` (交付文档模板)。

### 1.2 构建流程 (`build_app`)
1.  执行 PyInstaller 打包，生成 `dist/{app_name}.exe`。
2.  **新增**: 创建目录 `dist/{app_name}_release`。
3.  **新增**: 移动 `dist/{app_name}.exe` 到 release 目录。
4.  **新增**: 复制 `src/apps/{app_name}/config.json` 到 release 目录。
5.  **新增**: 复制 `docs/{display_name}/UserManual.md` (若无则 `Readme.md`) 到 release 目录，重命名为 `README.md`。

## 2. 模块设计

### 2.1 `src.common.config` (新增)
为了简化应用开发，提供统一的配置加载器。

```python
import json
import os
import sys
from typing import Dict, Any

def load_config(default_config: Dict[str, Any] = None) -> Dict[str, Any]:
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
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config.json: {e}")
            
    return default_config or {}
```

### 2.2 `init_app.py` 模板更新
*   `SERVER_TEMPLATE`: 引入 `load_config`，演示如何使用配置（例如控制日志级别）。
*   `CONFIG_TEMPLATE`: 一个简单的 JSON，例如 `{"log_level": "INFO"}`。
*   `MANUAL_TEMPLATE`: 简单的 Markdown，说明如何配置和运行。

## 3. 兼容性设计
*   对于已存在的应用（如 `math_time`），`build_app` 需要能够优雅降级：
    *   如果找不到 `config.json`，则不复制（或生成默认空配置？-> 不复制，以免覆盖）。
    *   如果找不到 `UserManual.md`，尝试复制 `Readme.md`。

## 4. 验证计划
1.  使用 `init_app` 创建 `new_standard_app`。
2.  检查源码目录是否有 `config.json`。
3.  运行 `build_app new_standard_app`。
4.  检查 `dist/new_standard_app_release` 目录内容。
5.  运行 release 目录下的 exe，验证是否读取了同目录的 `config.json`。
