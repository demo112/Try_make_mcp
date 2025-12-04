# TODO List - Everything2MD OCR Support

## Pending Items
- [ ] **Language Config**: Allow users to specify OCR language in `.env` (e.g., `OCR_LANGUAGE=chi_sim`).
- [ ] **Docker Update**: Add Tesseract installation to `Dockerfile`.

## Known Issues
- OCR is slow; large batches of images will take time.
- Accuracy depends heavily on image quality and Tesseract version.
