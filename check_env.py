import sys
import os

print(f"Python executable: {sys.executable}")
print(f"Sys path: {sys.path}")

try:
    import xhtml2pdf
    print(f"xhtml2pdf: {xhtml2pdf.__file__}")
except ImportError as e:
    print(f"Error importing xhtml2pdf: {e}")

try:
    import docx
    print(f"docx: {docx.__file__}")
except ImportError as e:
    print(f"Error importing docx: {e}")
