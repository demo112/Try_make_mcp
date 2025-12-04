# Alignment Document - Everything2MD Web Preview

## 1. Original Requirements
- **Target**: Provide a simple Web Interface for the Everything2MD tool.
- **Problem**: Currently, the tool is only accessible via the MCP protocol (CLI/LLM Client). Users cannot easily test or use it directly via a browser.
- **Goal**: Implement a web server that accepts file uploads, converts them using the existing logic, and displays/downloads the Markdown.

## 2. Project Context Understanding
- **Existing Codebase**:
  - `server.py`: Contains the MCP server and, critically, the conversion logic (mixed together).
  - `_convert_*` helpers: Recently extracted synchronous helpers in `server.py`.
- **Architecture**:
  - We need to reuse the conversion logic without running the full MCP server.
  - `FastAPI` is a modern, fast web framework that fits well with the existing async structure.

## 3. Clarified Ambiguities (Q&A)
- **Q: Should we modify `server.py`?**
  - **A**: Yes. We should extract the core conversion logic (path finding, `_convert_*` functions) into a separate module (`converter.py`) so both `server.py` (MCP) and the new `web_app.py` (Web) can import it without dependencies on each other's frameworks.
- **Q: What UI framework?**
  - **A**: Keep it simple. Standard HTML/CSS served by FastAPI (using `jinja2` or just returning HTML strings for minimal dependencies).
- **Q: Where to store uploads?**
  - **A**: Use a temporary directory (e.g., `tempfile` or a specific `uploads` folder) and clean up after processing.

## 4. Recommendation
- Extract logic to `src/apps/everything2md/converter.py`.
- Create `src/apps/everything2md/web_app.py` using FastAPI.
- Add `python-multipart` and `fastapi` (and `uvicorn`) to dependencies.
