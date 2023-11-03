import os
import random
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
from PIL import Image

def display_random_image_and_text(folder_path):
    image_extensions = ['.jpeg', '.jpg', '.png', '.bmp', '.tiff', '.gif']
    
    all_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            all_files.append(os.path.join(root, file))
    
    image_files = [f for f in all_files if os.path.splitext(f)[1].lower() in image_extensions]
    
    chosen_image_path = random.choice(image_files)
    chosen_txt_path = os.path.splitext(chosen_image_path)[0] + '.txt'
    
    img = Image.open(chosen_image_path)
    plt.imshow(img)
    plt.axis('off')
    plt.show()
    
    width, height = img.size
    file_size_bytes = os.path.getsize(chosen_image_path)
    
    if file_size_bytes < 1024 * 1024:
        file_size = file_size_bytes / 1024
        size_str = f"{file_size:.2f} KB"
    else:
        file_size = file_size_bytes / (1024 * 1024)
        size_str = f"{file_size:.2f} MB"
    print(f"Image dimensions: {width} x {height}px")
    print(f"Image file size: {size_str}")
    
    if os.path.exists(chosen_txt_path):
        with open(chosen_txt_path, 'r', encoding='utf-8') as txt_file:
            text_content = txt_file.read()
            display(Markdown(f"**Text content from {os.path.basename(chosen_txt_path)}:**\n{text_content}"))
    else:
        print(f"No corresponding text file found for {os.path.basename(chosen_image_path)}.")


folder_path = '/content/filtered'
display_random_image_and_text(folder_path)
