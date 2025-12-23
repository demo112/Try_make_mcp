# 对齐文档：MCP交付规范升级

## 1. 原始需求分析
**用户指令**：“更改工厂的规范。所有的mcp都是要以一个exe和一个配置与说明文档为交付目标”

**核心解读**：
用户要求升级“MCP生产工厂”的交付标准。原标准仅关注 EXE 的生成，新标准要求交付物必须是一个包含以下内容的“发布包”：
1.  **可执行文件**: `{app_name}.exe`
2.  **配置文件**: `config.json` 或 `.env` (含默认配置/模板)
3.  **说明文档**: `README.md` 或 `Manual.md` (含使用说明)

## 2. 影响范围分析
*   **`src/factory/init_app.py`**:
    *   需要生成 `config_template.json` (或类似) 到应用源码目录。
    *   需要生成 `UserManual.md` 到文档目录，并准备好被打包脚本引用。
    *   代码模板 (`server.py`) 可能需要更新，以演示如何读取外部配置文件。
*   **`src/factory/build_app.py`**:
    *   构建完成后，不能只输出 exe。
    *   需要创建一个发布文件夹 `dist/{app_name}_release/`。
    *   将 exe、配置文件、说明文档复制到发布文件夹。
*   **`src/common`**:
    *   可能需要增加读取外部配置文件的通用函数（优先支持与 exe 同目录的配置文件）。

## 3. 交付物定义 (Deliverables)
最终 `build_app.py` 运行后的 `dist/` 目录结构示例：
```text
dist/
└── math_time_release/
    ├── math_time.exe
    ├── config.json       # 默认配置
    └── README.md         # 使用说明
```

## 4. 识别的模糊点与假设
*   **配置格式**：用户未指定，假设使用 JSON，因为它在 Python 中无依赖且易读。
*   **文档来源**：假设说明文档来源于 `docs/{display_name}/UserManual.md`（如果没有则使用 `README.md`）。
*   **EXE 读取配置**：PyInstaller 打包后的 EXE 运行时，当前工作目录（CWD）通常是 EXE 所在目录。代码需要确保从 CWD 读取配置，而不是从临时解压目录 (`_MEIxxxx`) 读取。
