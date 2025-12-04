# Consensus Document - Everything2MD Web Preview

## 1. Requirement Description
Create a standalone Web Application (`web_app.py`) that exposes the Everything2MD conversion capabilities via a browser interface.

## 2. Technical Implementation
- **Refactoring**:
  - Move `find_executable`, global path constants, and `_convert_*` functions from `server.py` to a new `converter.py` module.
  - `server.py` will import these to maintain MCP functionality.
- **Web App**:
  - **Framework**: FastAPI.
  - **Routes**:
    - `GET /`: Show upload form.
    - `POST /convert`: Handle file upload, execute conversion (async), and return the Markdown content.
  - **Async**: Reuse the `asyncio.to_thread` pattern for non-blocking conversions.
- **Dependencies**: Add `fastapi`, `uvicorn`, `python-multipart`.

## 3. Acceptance Criteria
- **Refactoring**: MCP Server (`server.py`) must still pass all existing tests (`verify_async.py`).
- **Web Interface**:
  - User can open `http://localhost:8000` (or similar).
  - User can upload supported files (PDF, DOCX, etc.).
  - Browser displays the converted Markdown text.
- **Concurrency**: Web app handles concurrent requests without crashing (relies on the same async architecture).

## 4. Boundaries
- No database.
- No user authentication.
- Files are temporary and not permanently stored.
- Basic styling only.
