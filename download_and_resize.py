import os
import subprocess
import zipfile
from PIL import Image, ImageFilter

def download_with_aria2c(download_urls, output_path):
    for download_url in download_urls:
        try:
            filename = os.path.basename(download_url)
            result = subprocess.run(['aria2c', download_url, '-d', output_path, '-o', filename], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT,
                                    text=True)
            print(result.stdout)
        except Exception as e:
            print(f"An error occurred while downloading {download_url}: {str(e)}")

def extract_zip(zip_path, extract_path):
    try:
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            print(f"File extracted to {extract_path}")
        os.remove(zip_path)
        print(f"ZIP file {zip_path} deleted")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def resize_images(src_folder, max_size=(640, 640), format='JPEG'):
    valid_image_extensions = ('.jpeg', '.jpg', '.png', '.bmp', '.tiff', '.gif')
    
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            _, file_extension = os.path.splitext(file)
            if file_extension.lower() not in valid_image_extensions:
                continue
            
            src_filepath = os.path.join(root, file)
            filename_no_ext = os.path.splitext(file)[0]
            dest_filepath = os.path.join(root, f"{filename_no_ext}_resized.jpg")
            
            try:
                with Image.open(src_filepath) as img:
                    img.thumbnail(max_size, Image.LANCZOS)
                    
                    if img.mode == 'RGBA':
                        bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
                        img = Image.alpha_composite(bg, img)
                        img = img.convert('RGB')
                    
                    elif img.mode == 'P':
                        img = img.convert('RGBA')
                        bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
                        img = Image.alpha_composite(bg, img)
                        img = img.convert('RGB')
                    
                    img.save(dest_filepath, format=format, quality=85)
                    os.remove(src_filepath)
                
                new_name = dest_filepath.replace("_resized", "")
                os.rename(dest_filepath, new_name)
            except Exception as e:
                print(f"Error resizing image {file}: {str(e)}")

download_url_str = "downloadurl1,downloadurl2"
download_urls = download_url_str.split(',')

output_path = '/content/temp'
extract_path = '/content/filtered'

download_with_aria2c(download_urls, output_path)

for download_url in download_urls:
    filename = os.path.basename(download_url)
    zip_path = os.path.join(output_path, filename)
    extract_zip(zip_path, extract_path)

resize_images(extract_path, max_size=(1024, 1024))
