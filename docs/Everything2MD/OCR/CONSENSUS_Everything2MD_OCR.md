# Consensus Document - Everything2MD OCR Support

## 1. Objective
Implement OCR (Optical Character Recognition) support to convert image files to Markdown text using Tesseract.

## 2. Implementation Details

### 2.1 Dependencies
- Add `pytesseract` and `Pillow` to `requirements.txt`.

### 2.2 Configuration
- Add `TESSERACT_PATH` to `.env` handling in `converter.py`.
- Default Windows path: `C:\Program Files\Tesseract-OCR\tesseract.exe`.
- Default Linux path: `/usr/bin/tesseract`.

### 2.3 Code Changes
- **`src/apps/everything2md/converter.py`**:
  - Import `pytesseract` and `PIL.Image`.
  - Add `find_executable` call for `tesseract`.
  - Implement `_convert_image_to_md(source_path, output_path)`.
  - Update `convert_file_sync` dispatcher to handle image extensions.
- **`src/apps/everything2md/server.py`**:
  - Update docstring to list supported image formats.
  - Ensure `asyncio.to_thread` handles the new types (it blindly calls `convert_file_sync` so it might just work if extensions are passed correctly, but we should check if we are filtering extensions in `server.py`).
  - *Correction*: `server.py` does check extensions in the `convert_to_markdown` function. It needs to be updated to allow image extensions.

## 3. Acceptance Criteria
- [ ] Can convert a PNG/JPG image with text to a Markdown file.
- [ ] Fails gracefully if Tesseract is not installed or path is wrong.
- [ ] Works asynchronously without blocking the server.
- [ ] Web App allows uploading images.
