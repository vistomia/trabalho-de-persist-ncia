import zipfile
from pathlib import Path

def zip_store_files(store_path="store", output_zip="store_backup.zip"):
    """
    Zip all files in the store directory to a single zip file without overloading RAM.
    Uses streaming compression to handle large files efficiently.
    """
    store_dir = Path(store_path)
    
    if not store_dir.exists():
        print(f"Store directory '{store_path}' does not exist")
        return False
    
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for file_path in store_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(store_dir)
                    zipf.write(file_path, arcname)
        
        print(f"Successfully created {output_zip}")
        return True
        
    except Exception as e:
        print(f"Error creating zip file: {e}")
        return False

if __name__ == "__main__":
    zip_store_files()