import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import tempfile

# Add src/apps/everything2md to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from converter import convert_file_sync, _convert_image_to_md

class TestOCR(unittest.TestCase):
    
    def setUp(self):
        # Create a dummy image file
        self.test_image = "test_image.png"
        with open(self.test_image, "wb") as f:
            f.write(b"fake image data")
        self.output_md = "output_ocr.md"

    def tearDown(self):
        if os.path.exists(self.test_image):
            os.remove(self.test_image)
        if os.path.exists(self.output_md):
            os.remove(self.output_md)

    @patch("converter.pytesseract")
    @patch("converter.Image")
    def test_ocr_success(self, mock_image, mock_pytesseract):
        # Mock setup
        mock_pytesseract.image_to_string.return_value = "Extracted Text"
        mock_pytesseract.get_tesseract_version.return_value = "5.0.0"
        
        # Run conversion
        convert_file_sync(self.test_image, self.output_md)
        
        # Verify
        mock_pytesseract.image_to_string.assert_called_once()
        with open(self.output_md, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, "Extracted Text")
        print("✅ OCR Success Test Passed")

    @patch("converter.pytesseract")
    def test_ocr_missing_tesseract_binary(self, mock_pytesseract):
        # Mock Tesseract binary missing (get_version raises)
        mock_pytesseract.get_tesseract_version.side_effect = Exception("Not found")
        
        with self.assertRaises(RuntimeError) as cm:
            convert_file_sync(self.test_image, self.output_md)
        
        self.assertIn("executable not found", str(cm.exception))
        print("✅ OCR Missing Binary Test Passed")

if __name__ == "__main__":
    unittest.main()
