# Alignment Document - Everything2MD OCR Support

## 1. Background
The current Everything2MD MCP server supports Office documents (DOCX, PPTX, XLSX) and PDFs. To truly fulfill the "Everything" promise, it needs to support converting images (PNG, JPG, etc.) containing text into Markdown. This requires Optical Character Recognition (OCR) capabilities.

## 2. Requirements Analysis
- **Input**: Image files (.png, .jpg, .jpeg, .tiff, .bmp).
- **Output**: Markdown text containing the extracted text from the image.
- **Technology**: 
  - Python Library: `pytesseract` (wrapper for Tesseract-OCR).
  - Image Processing: `Pillow`.
  - System Dependency: Tesseract-OCR engine binary.
- **Configuration**: 
  - Must support configuring the Tesseract executable path via environment variable (`TESSERACT_PATH`) to support different environments (Windows/Linux/Docker).

## 3. Constraints
- **Performance**: OCR is CPU intensive and slow. It must run in the thread pool (asyncio.to_thread) to avoid blocking the MCP server.
- **Dependency**: Users must install Tesseract-OCR separately. The code must handle the "missing Tesseract" case gracefully (e.g., error message or skip).

## 4. Integration Point
- The logic should be implemented in `converter.py` to be shared by both MCP and Web App.
- `server.py` and `web_app.py` will automatically support it if they rely on `converter.py`'s dispatch logic (need to update supported extensions list).
