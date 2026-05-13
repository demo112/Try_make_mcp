import os
import re

def clean_duplicate_files(root_dir, delete=False):
    # Pattern to match files ending with _1, _2, etc., possibly with an extension
    pattern = re.compile(r'(.+)_(\d+)(\.[^.]+)?$')
    
    count = 0
    deleted_size = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # User requested to include all paths, so we do NOT skip .git
        # if '.git' in dirpath.split(os.sep):
        #    continue
            
        for filename in filenames:
            match = pattern.match(filename)
            if match:
                base_name = match.group(1)
                number = match.group(2)
                extension = match.group(3) if match.group(3) else ''
                
                # Reconstruct the potential original filename
                original_filename = f"{base_name}{extension}"
                original_path = os.path.join(dirpath, original_filename)
                
                duplicate_path = os.path.join(dirpath, filename)
                
                # If original exists, this is likely a duplicate
                if os.path.exists(original_path):
                    try:
                        file_size = os.path.getsize(duplicate_path)
                        if delete:
                            os.remove(duplicate_path)
                            print(f"Deleted: {duplicate_path}")
                        else:
                            print(f"Would delete: {duplicate_path}")
                        
                        count += 1
                        deleted_size += file_size
                    except Exception as e:
                        print(f"Error processing {duplicate_path}: {e}")

    return count, deleted_size

if __name__ == "__main__":
    root = os.getcwd()
    # First run in dry-run mode
    # print("--- Dry Run ---")
    # c, s = clean_duplicate_files(root, delete=False)
    # print(f"Found {c} files, total size: {s/1024/1024:.2f} MB")
    
    # Uncomment to execute
    print("\n--- Executing Deletion ---")
    c, s = clean_duplicate_files(root, delete=True)
    print(f"Deleted {c} files, recovered {s/1024/1024:.2f} MB")
