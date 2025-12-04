# Checklist Document - Everything2MD Build

## Pre-Build Verification
- [ ] **Codebase**: Ensure `src/apps/everything2md` contains `server.py` and `web_app.py`.
- [ ] **Dependencies**: `requirements.txt` is up to date. `pyinstaller` is installed.
- [ ] **Environment**: Virtual environment `.venv` is active.
- [ ] **Cleanliness**: `dist/` and `build/` folders from previous attempts are removed.

## Build Script Verification
- [ ] **Script Existence**: `src/apps/everything2md/build.py` is created.
- [ ] **Configuration**:
  - [ ] `PyInstaller` options set to `--onefile` (or as decided).
  - [ ] Hidden imports for `uvicorn`, `fastapi`, `pydantic`, `mcp` are configured.
  - [ ] Output names match `everything2md-mcp` and `everything2md-web`.

## Security & Sensitivity
- [ ] **No Secrets**: Ensure no API keys or passwords are hardcoded in the build script or source code.
- [ ] **Paths**: Ensure absolute paths are not hardcoded; use relative or dynamic paths.

## Post-Build Verification Plan
- [ ] **Existence**: Check if `.exe` files are generated in `dist/`.
- [ ] **Execution**:
  - [ ] `everything2md-mcp.exe` starts and listens on stdio (or waits for input).
  - [ ] `everything2md-web.exe` starts and serves the UI.
- [ ] **External Tools**: Verify `.exe` can find/call LibreOffice/Pandoc if available in system PATH (or configured via `.env`).
