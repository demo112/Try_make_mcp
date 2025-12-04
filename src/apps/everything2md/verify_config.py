import os
import sys
import subprocess
import tempfile

SERVER_SCRIPT = os.path.join("src", "apps", "everything2md", "server.py")

def test_valid_config():
    print("Testing Valid Configuration...")
    with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp:
        tmp.close()
        
        env = os.environ.copy()
        env["LIBREOFFICE_PATH"] = tmp.name
        
        # Run a script that imports server and prints the path
        cmd = [sys.executable, "-c", "import src.apps.everything2md.server as s; print(f'FOUND:{s.SOFFICE_PATH}')"]
        result = subprocess.run(cmd, env=env, cwd=os.getcwd(), capture_output=True, text=True)
        
        os.unlink(tmp.name)
        
        if result.returncode != 0:
            print("FAILED: Script crashed")
            print(result.stderr)
            return False
            
        if f"FOUND:{tmp.name}" in result.stdout:
            print("PASSED: Correct path loaded from env")
            return True
        else:
            print(f"FAILED: Output was {result.stdout}")
            return False

def test_invalid_config():
    print("\nTesting Invalid Configuration...")
    env = os.environ.copy()
    env["LIBREOFFICE_PATH"] = "C:\\NonExistentPath\\soffice.exe"
    
    cmd = [sys.executable, "-c", "import src.apps.everything2md.server"]
    result = subprocess.run(cmd, env=env, cwd=os.getcwd(), capture_output=True, text=True)
    
    if result.returncode != 0:
        if "Configured LIBREOFFICE_PATH path not found" in result.stderr or "Critical Error" in result.stdout:
             print("PASSED: Script failed as expected with error message")
             return True
        else:
             print(f"FAILED: Script failed but with unexpected error: {result.stderr}")
             return False
    else:
        print("FAILED: Script should have failed but didn't")
        return False

if __name__ == "__main__":
    if test_valid_config() and test_invalid_config():
        print("\nAll Config Tests Passed!")
        sys.exit(0)
    else:
        sys.exit(1)
