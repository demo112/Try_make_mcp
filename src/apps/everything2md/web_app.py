import os
import shutil
import logging
import asyncio
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse

try:
    from .converter import convert_file_sync
except ImportError:
    from converter import convert_file_sync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Everything2MD Web Preview")

HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Everything2MD Web Preview</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { display: flex; flex-direction: column; gap: 20px; }
        textarea { width: 100%; height: 400px; padding: 10px; }
        button { padding: 10px 20px; background-color: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        #status { margin-top: 10px; color: #666; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Everything2MD Web Preview</h1>
    <div class="container">
        <div>
            <p>Upload a document (PDF, DOCX, PPTX, etc.) to convert it to Markdown.</p>
            <input type="file" id="fileInput">
            <button onclick="uploadFile()">Convert</button>
            <div id="status"></div>
        </div>
        <div>
            <h3>Result:</h3>
            <textarea id="resultArea" readonly></textarea>
        </div>
    </div>

    <script>
        async function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const statusDiv = document.getElementById('status');
            const resultArea = document.getElementById('resultArea');
            
            if (!fileInput.files[0]) {
                statusDiv.textContent = "Please select a file first.";
                statusDiv.className = "error";
                return;
            }

            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);

            statusDiv.textContent = "Converting... Please wait.";
            statusDiv.className = "";
            resultArea.value = "";

            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const text = await response.text();
                    resultArea.value = text;
                    statusDiv.textContent = "Conversion successful!";
                } else {
                    const errorText = await response.text();
                    statusDiv.textContent = "Error: " + errorText;
                    statusDiv.className = "error";
                }
            } catch (error) {
                statusDiv.textContent = "Network Error: " + error.message;
                statusDiv.className = "error";
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTML_CONTENT

@app.post("/convert", response_class=PlainTextResponse)
async def convert_document(file: UploadFile = File(...)):
    filename = file.filename
    logger.info(f"Received upload: {filename}")
    
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = os.path.join(temp_dir, filename)
        output_path = os.path.join(temp_dir, "output.md")
        
        try:
            # Save uploaded file
            with open(source_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Perform conversion in thread pool
            await asyncio.to_thread(convert_file_sync, source_path, output_path)
            
            # Read result
            if os.path.exists(output_path):
                with open(output_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return content
            else:
                raise HTTPException(status_code=500, detail="Conversion failed to produce output file.")
                
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            # Return 500 with error message
            # Note: In production, might want to hide internal errors, but for dev tool it's useful
            raise HTTPException(status_code=500, detail=str(e))
            
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
