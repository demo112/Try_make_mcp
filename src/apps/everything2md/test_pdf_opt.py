import os
import sys
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# Setup paths
SERVER_SCRIPT = os.path.join("src", "apps", "everything2md", "server.py")
TEST_DIR = os.path.join("src", "apps", "everything2md", "test_data")
os.makedirs(TEST_DIR, exist_ok=True)

def create_test_pdf(filename):
    """Create a PDF with text and a table"""
    filepath = os.path.join(TEST_DIR, filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []
    
    # Add some text via canvas (not flowable here, mixing methods for simplicity usually not recommended but we just want content)
    # Actually, let's use reportlab flowables for structure
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Test PDF Document", styles['Title']))
    elements.append(Paragraph("This is a sample paragraph for testing conversion.", styles['Normal']))
    
    # Add a table
    data = [['Header 1', 'Header 2'],
            ['Row 1 Col 1', 'Row 1 Col 2'],
            ['Row 2 Col 1', 'Row 2 Col 2']]
    t = Table(data)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                           ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                           ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                           ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(t)
    
    doc.build(elements)
    print(f"Created test PDF: {filepath}")
    return filepath

def test_pdf_conversion():
    pdf_path = create_test_pdf("test.pdf")
    md_path = pdf_path.replace(".pdf", ".md")
    
    print("Running conversion...")
    
    # Invoke the server function directly via script execution to simulate environment
    # We will use a small script runner
    runner_code = f"""
import sys
sys.path.append('.')
from src.apps.everything2md.server import convert_to_markdown

result = convert_to_markdown(r"{pdf_path}", r"{md_path}")
print(f"RESULT:{{result}}")
"""
    
    result = subprocess.run([sys.executable, "-c", runner_code], 
                           cwd=os.getcwd(), 
                           capture_output=True, 
                           text=True)
    
    if result.returncode != 0:
        print("FAILED: Server script crashed")
        print(result.stderr)
        return False
        
    if "RESULT:Conversion successful" not in result.stdout:
        print(f"FAILED: Conversion function returned error: {result.stdout}")
        return False
        
    if not os.path.exists(md_path):
        print("FAILED: Output MD file not created")
        return False
        
    # Check content
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print("\n--- Generated Markdown Content ---")
    print(content)
    print("----------------------------------\n")
    
    # Verify key elements
    checks = [
        "Test PDF Document",
        "Row 1 Col 1",
        "Row 2 Col 2"
    ]
    
    all_passed = True
    for check in checks:
        if check in content:
            print(f"PASSED: Found '{check}'")
        else:
            print(f"FAILED: Missing '{check}'")
            all_passed = False
            
    # Check for markdown table syntax
    if "|" in content and "-|-" in content.replace(" ", ""): # Rough check for table structure
         print("PASSED: Table structure detected")
    else:
         print("WARNING: Table structure might be missing or formatted differently")
         # pymupdf4llm table output format can vary, but usually standard markdown
         
    return all_passed

if __name__ == "__main__":
    if test_pdf_conversion():
        print("\nPDF Optimization Test Passed!")
        sys.exit(0)
    else:
        print("\nPDF Optimization Test Failed!")
        sys.exit(1)
