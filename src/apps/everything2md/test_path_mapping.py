import os
import sys
import unittest

# Add src/apps/everything2md to path so we can import path_utils
sys.path.append(os.path.join(os.getcwd(), "src", "apps", "everything2md"))

from path_utils import map_path_to_container

class TestPathMapping(unittest.TestCase):
    def setUp(self):
        # Save original env
        self.orig_env = os.environ.copy()
        
    def tearDown(self):
        # Restore env
        os.environ.clear()
        os.environ.update(self.orig_env)
        
    def test_no_mapping_configured(self):
        if "HOST_ROOT" in os.environ: del os.environ["HOST_ROOT"]
        if "CONTAINER_ROOT" in os.environ: del os.environ["CONTAINER_ROOT"]
        
        path = r"C:\Users\test.docx"
        self.assertEqual(map_path_to_container(path), path)
        
    def test_basic_mapping(self):
        os.environ["HOST_ROOT"] = "C:\\"
        os.environ["CONTAINER_ROOT"] = "/mnt/c/"
        
        input_path = "C:\\Users\\test.docx"
        expected = "/mnt/c/Users/test.docx"
        self.assertEqual(map_path_to_container(input_path), expected)
        
    def test_mapping_without_trailing_slash(self):
        os.environ["HOST_ROOT"] = "C:"
        os.environ["CONTAINER_ROOT"] = "/mnt/c"
        
        input_path = "C:\\Users\\test.docx"
        expected = "/mnt/c/Users/test.docx"
        self.assertEqual(map_path_to_container(input_path), expected)

    def test_case_insensitive_drive(self):
        os.environ["HOST_ROOT"] = "C:\\"
        os.environ["CONTAINER_ROOT"] = "/mnt/c/"
        
        input_path = "c:\\Users\\test.docx" # lower c
        expected = "/mnt/c/Users/test.docx"
        self.assertEqual(map_path_to_container(input_path), expected)

    def test_unmapped_path(self):
        os.environ["HOST_ROOT"] = "C:\\"
        os.environ["CONTAINER_ROOT"] = "/mnt/c/"
        
        input_path = "D:\\Data\\test.docx" # Different drive
        self.assertEqual(map_path_to_container(input_path), input_path)

if __name__ == '__main__':
    unittest.main()
