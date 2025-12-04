# Alignment Document - Everything2MD Build & Packaging

## 1. Background
The user requested "generate cmp application" (interpreted as "MCP Application"). The codebase currently runs as Python scripts. To deliver a true "Application", we need to package the Python code into a standalone executable (`.exe` on Windows) that allows users to run the MCP Server without managing a Python environment manually.

## 2. Interpretation
"cmp" is interpreted as a typo for "MCP". The request "give me the application" implies a distributable binary artifact.

## 3. Requirements
- **Input**: `src/apps/everything2md/server.py` (MCP Server) and `web_app.py` (Web Preview).
- **Output**: 
  - `everything2md-mcp.exe`: The MCP Server executable.
  - `everything2md-web.exe`: The Web Preview executable (Optional, but good for completeness).
- **Tooling**: `PyInstaller`.
- **Environment**: Windows (current environment).

## 4. Constraints
- Must handle hidden imports (FastAPI, Uvicorn, Pydantic, etc.).
- Must handle external dependencies (LibreOffice, Pandoc, Tesseract) gracefully (we cannot bundle them easily, so we rely on PATH or .env, but the EXE must find the code to do that).
- `dotenv` loading must work in frozen mode.

## 5. Strategy
- Use `PyInstaller` to build a one-file (or one-dir) executable.
- Create a `build.py` script to automate the process.
