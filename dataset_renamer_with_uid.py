import os
import base64
import uuid

def encode_string_to_base64(s):
    """
    Meng-encode string dengan Base64.
    """
    return base64.b64encode(s.encode()).decode()

def generate_random_string():
    """
    Menghasilkan string acak dari UUID.
    """
    return str(uuid.uuid4())

def rename_files_with_encoded_prefix(folder_path, prefix):
    """
    Rename semua file dalam folder dengan menambahkan prefix yang di-encode dan nama file acak.

    Parameters:
    - folder_path: Path ke folder yang berisi file yang akan di-rename.
    - prefix: Prefix yang akan di-encode dan ditambahkan ke setiap nama file.
    """
    encoded_prefix = encode_string_to_base64(prefix)
    
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(file_name)[1]
            
            new_file_name = f"{encoded_prefix}_{generate_random_string()}{file_extension}"
            new_file_path = os.path.join(folder_path, new_file_name)
            
            os.rename(file_path, new_file_path)
            print(f"Renamed {file_name} to {new_file_name}")

if __name__ == "__main__":
    FOLDER_PATH = r'C:\Users\OP Team\Pictures\Image Classifier\Bad_Clean'
    PREFIX = "Bad_Clean"
    rename_files_with_encoded_prefix(FOLDER_PATH, PREFIX)
