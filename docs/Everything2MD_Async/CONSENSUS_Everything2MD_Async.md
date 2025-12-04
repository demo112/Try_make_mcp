# Consensus Document - Everything2MD Async Processing

## 1. Requirement Description
Refactor the `Everything2MD` MCP server to use asynchronous processing for file conversions. This ensures that long-running conversion tasks (e.g., large PDFs or DOCX files) do not block the server's main loop, allowing it to handle other requests (like health checks or other tool calls) concurrently.

## 2. Technical Implementation
- **Async Tool Definition**: Change `convert_to_markdown` from `def` to `async def`.
- **Thread Pool Offloading**:
  - Use `asyncio.to_thread()` to run the blocking conversion logic.
  - This applies to both `subprocess.run` calls (LibreOffice, Pandoc) and library calls (`pymupdf4llm`).
- **Code Restructuring**:
  - Break down the monolithic `convert_to_markdown` function into smaller, format-specific synchronous handlers (e.g., `_convert_docx_sync`, `_convert_pdf_sync`).
  - The main async tool will dispatch to these handlers via `await asyncio.to_thread(...)`.

## 3. Acceptance Criteria
- **Functionality**: All existing file conversions (DOCX, PDF, PPTX, XLSX) must still work correctly.
- **Non-blocking**: The server should be able to accept a second request while processing a large file (conceptually, though hard to verify without a client sending concurrent requests, we verify code structure).
- **Error Handling**: Exceptions raised in threads must be correctly propagated and returned as error messages.

## 4. Boundaries & Assumptions
- We assume `FastMCP` handles the event loop correctly.
- We will not implement a job queue system (e.g., Celery) at this stage; just simple async offloading.
- We will not implement progress reporting for this iteration.
