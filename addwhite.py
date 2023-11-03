import os
import argparse
from PIL import Image

def add_white_background(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    for file in files:
        if file.endswith('.png'):
            file_path = os.path.join(folder_path, file)
            image = Image.open(file_path).convert("RGBA")
            
            white_background = Image.new("RGBA", image.size, "WHITE")
            white_background.paste(image, (0, 0), image)
            
            white_background.convert("RGB").save(file_path, "PNG")
            print(f"Processed {file}")

    print("Processing complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a white background to all PNG files in a given folder.")
    parser.add_argument('folder_path', type=str, help="Path to the folder containing the PNG files.")
    
    args = parser.parse_args()
    add_white_background(args.folder_path)
