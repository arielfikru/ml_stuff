import os
from PIL import Image
import cv2
import numpy as np

def convert_png_to_jpeg(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            png_image = Image.open(os.path.join(folder_path, filename))
            
            if png_image.mode == 'RGBA':
                background = Image.new("RGB", png_image.size, (255, 255, 255))
                background.paste(png_image, mask=png_image.split()[3])
                rgb_image = background
            else:
                rgb_image = png_image.convert('RGB')

            cv2_image = np.array(rgb_image)
            cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(os.path.join(folder_path, filename[:-4] + '.jpg'), cv2_image)

convert_png_to_jpeg('path/to/your/folder')
