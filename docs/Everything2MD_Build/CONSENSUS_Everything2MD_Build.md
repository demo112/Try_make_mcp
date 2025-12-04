# Consensus Document - Everything2MD Build & Packaging

## 1. Requirement Description
The objective is to transform the current Python script-based `Everything2MD` tools (MCP Server and Web Preview) into standalone Windows executables (`.exe`). This allows users to run the tools without needing to manually install Python or manage virtual environments.

## 2. Acceptance Criteria
- **Artifacts**:
  - `dist/everything2md-mcp.exe`: Standalone executable for the MCP Server.
  - `dist/everything2md-web.exe`: Standalone executable for the Web Preview Interface.
- **Functionality**:
  - Both executables must start successfully on a Windows machine.
  - `everything2md-mcp.exe` must function as a standard MCP server (stdio communication).
  - `everything2md-web.exe` must launch the web server and serve the UI.
  - Both must be able to read configuration from a `.env` file located in the same directory (or parent directory).
  - Both must correctly identify and invoke external dependencies (LibreOffice, Pandoc, Tesseract, PyMuPDF) using the paths defined in `.env` or system PATH.
- **Environment**:
  - The build process runs on the current Windows development environment.
  - The output targets Windows 64-bit.

## 3. Technical Implementation
- **Build Tool**: `PyInstaller` (Version 6.x+).
- **Automation**: A Python script `src/apps/everything2md/build.py` will be created to orchestrate the build.
- **Configuration**:
  - Use `--onefile` mode for single-executable convenience (or `--onedir` if startup speed/debugging is a priority; we will default to `--onefile` for "App" feel, unless size/speed dictates otherwise).
  - Handle hidden imports for dynamic libraries (FastAPI, Uvicorn, Pydantic).
  - Ensure `python-dotenv` loads the `.env` file relative to the *executable* path, not the temp execution path.
- **Dependencies**:
  - **Internal**: All Python packages (fastapi, mcp, pillow, pytesseract, etc.) will be bundled.
  - **External**: LibreOffice, Pandoc, and Tesseract binaries will **NOT** be bundled. The application will assume they are installed on the host system. This keeps the artifact size reasonable and avoids licensing/portability complexities.

## 4. Boundaries & Assumptions
- **No Installer**: We are producing raw `.exe` files, not an MSI or Setup wizard.
- **External Tools**: The user is responsible for installing LibreOffice/Pandoc/Tesseract separately.
- **Platform**: Windows only for this task.

## 5. Risk Management
- **Anti-Virus**: PyInstaller executables sometimes trigger false positives. (Accepted risk).
- **Path Resolution**: `sys._MEIPASS` handling is critical for bundled assets, though we currently rely mostly on code.
