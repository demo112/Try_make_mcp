# Alignment Document - Everything2MD Async Processing

## 1. Original Requirements
- **Target**: Optimize the `Everything2MD` MCP server to handle concurrent requests and large file conversions without blocking.
- **Problem**: The current implementation uses synchronous `subprocess.run` and blocking library calls (`pymupdf4llm`), which can freeze the server during long conversion tasks.
- **Goal**: Refactor the tool execution to be asynchronous.

## 2. Project Context Understanding
- **Existing Codebase**:
  - `server.py`: Main entry point using `FastMCP`.
  - `convert_to_markdown`: Monolithic synchronous function handling various file types.
  - Dependencies: `subprocess` (LibreOffice, Pandoc), `pymupdf4llm` (PDF), `pptx2md` (PPTX).
- **Architecture**:
  - FastMCP supports `async def` tools.
  - Heavy lifting is done by external processes or C-extension libraries.

## 3. Clarified Ambiguities (Q&A)
- **Q: Does FastMCP support async tools?**
  - **A**: Yes, FastMCP supports `async def`.
- **Q: How to handle CPU-bound tasks (like `pymupdf4llm`)?**
  - **A**: Use `asyncio.to_thread` or `loop.run_in_executor` to offload them to a thread pool.
- **Q: How to handle IO-bound tasks (like `subprocess`)?**
  - **A**: `asyncio.create_subprocess_exec` is the native async way, but since we have complex logic involving intermediate files, wrapping existing synchronous logic in a thread pool might be safer and cleaner than rewriting everything to use async subprocess primitives, unless we want to stream output. Given the current "convert then return" model, thread pool is sufficient.

## 4. Recommendation
- Refactor `convert_to_markdown` to be `async def`.
- Extract specific conversion logic (DOCX, PDF, PPTX) into separate helper functions.
- Run these helper functions in a thread pool using `fastmcp.Context` or `asyncio.to_thread`.
