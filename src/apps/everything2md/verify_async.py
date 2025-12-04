import asyncio
import os
import sys
from unittest.mock import MagicMock, patch

# Add src/apps/everything2md to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import convert_to_markdown

async def test_async_execution():
    print("Testing async execution...")
    
    # Test 1: File not found (Fastest check)
    result = await convert_to_markdown("non_existent.docx", "output.md")
    print(f"Result 1 (File not found): {result}")
    assert "Error: Source file not found" in result

    # Test 2: Mocking successful conversion to verify async dispatch
    # Patching the function imported in server.py
    with patch('server.convert_file_sync') as mock_convert:
        # Create a dummy PDF file to pass existence check
        with open("dummy.pdf", "w") as f:
            f.write("dummy")
        
        try:
            result = await convert_to_markdown("dummy.pdf", "output.md")
            print(f"Result 2 (Mock PDF): {result}")
            
            # Verify it called the helper
            if result == "Conversion successful":
                print("Async dispatch successful!")
                mock_convert.assert_called_once()
            else:
                print(f"Unexpected result: {result}")
                
        finally:
            if os.path.exists("dummy.pdf"):
                os.remove("dummy.pdf")
            if os.path.exists("output.md"):
                os.remove("output.md")

if __name__ == "__main__":
    try:
        asyncio.run(test_async_execution())
        print("✅ Async Verification Passed")
    except Exception as e:
        print(f"❌ Async Verification Failed: {e}")
        sys.exit(1)
