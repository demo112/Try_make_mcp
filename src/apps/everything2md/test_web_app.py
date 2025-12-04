import os
import sys
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Add src/apps/everything2md to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Everything2MD Web Preview" in response.text

def test_convert_endpoint():
    # Mock the converter function to avoid external dependencies during test
    with patch('web_app.convert_file_sync') as mock_convert:
        # Setup the mock to write a dummy output file
        def side_effect(source, output):
            with open(output, "w") as f:
                f.write("# Converted Markdown\n\nContent.")
        
        mock_convert.side_effect = side_effect

        # Create a dummy file to upload
        files = {'file': ('test.docx', b'dummy content', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        
        response = client.post("/convert", files=files)
        
        assert response.status_code == 200
        assert response.text == "# Converted Markdown\n\nContent."
        mock_convert.assert_called_once()

def test_convert_endpoint_failure():
    with patch('web_app.convert_file_sync') as mock_convert:
        mock_convert.side_effect = Exception("Conversion error")
        
        files = {'file': ('test.docx', b'dummy content', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        
        response = client.post("/convert", files=files)
        
        assert response.status_code == 500
        assert "Conversion error" in response.json()['detail']

if __name__ == "__main__":
    # Manually run tests if executed as script
    try:
        test_read_root()
        print("✅ Root endpoint test passed")
        test_convert_endpoint()
        print("✅ Convert endpoint test passed")
        test_convert_endpoint_failure()
        print("✅ Failure handling test passed")
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        sys.exit(1)
