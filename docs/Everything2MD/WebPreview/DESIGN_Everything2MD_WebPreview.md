# Design Document - Everything2MD Web Preview

## 1. Architecture Overview

The architecture introduces a new `converter.py` module that acts as the shared core logic provider for both the MCP Server (`server.py`) and the new Web Application (`web_app.py`).

```mermaid
graph TD
    Client[Client (Browser)] --> WebApp[FastAPI App]
    MCPClient[MCP Client] --> MCPServer[FastMCP Server]
    
    WebApp --> Converter[converter.py]
    MCPServer --> Converter
    
    Converter --> LibO[LibreOffice]
    Converter --> Pandoc
    Converter --> PyMuPDF
    Converter --> PathUtils[path_utils.py]
```

## 2. Component Design

### 2.1 Core Converter Module (`converter.py`)
- **Responsibilities**:
  - Path configuration (`find_executable`).
  - Synchronous conversion logic (`_convert_*`).
  - Should not depend on `mcp` or `fastapi`.
- **Functions**:
  - `find_executable(...)`
  - `convert_office_to_md_sync(...)`
  - `convert_pdf_to_md_sync(...)`
  - `convert_pptx_to_md_sync(...)`

### 2.2 Web Application (`web_app.py`)
- **Framework**: FastAPI.
- **Endpoints**:
  - `GET /`: Returns a simple HTML page with a file upload form.
  - `POST /convert`:
    - Accepts `UploadFile`.
    - Saves file to a temporary directory.
    - Calls `converter.py` functions in a thread pool (`asyncio.to_thread`).
    - Reads the generated Markdown.
    - Cleans up temporary files.
    - Returns the Markdown content (text/plain).

### 2.3 HTML Template
- Simple, embedded HTML string in `web_app.py` (to avoid extra file management for now).
- Features:
  - File input.
  - "Convert" button.
  - `<pre>` area to display results.
  - "Download" button (optional, or just save as...).

## 3. Data Flow (Web)
1. User uploads `doc.docx`.
2. `web_app` saves to `/tmp/uuid/doc.docx`.
3. `web_app` calls `converter.convert_office_to_md_sync("/tmp/uuid/doc.docx", "/tmp/uuid/output.md")` in thread.
4. Converter runs LibreOffice -> Pandoc.
5. `web_app` reads `/tmp/uuid/output.md`.
6. `web_app` deletes `/tmp/uuid`.
7. `web_app` returns Markdown text to browser.

## 4. Exception Handling
- Web App catches exceptions from `converter`.
- Returns 500 Internal Server Error with the error message to the UI.
