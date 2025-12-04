# TODO List - Everything2MD Web Preview

## Pending Items
- [ ] **UI Polish**: Add Bootstrap or Tailwind CSS to the HTML template for a better look.
- [ ] **Download Button**: Add a proper download button for the converted file instead of just displaying text.
- [ ] **Docker Entry**: Update `Dockerfile` (or create a new one) to support running the web app.
- [ ] **Batch Upload**: Support uploading multiple files at once.

## Known Issues
- Large files might timeout if the conversion takes too long (default timeouts apply).
- Temporary files are cleaned up immediately, so "download" must happen via the response content.
