import os
import torch
from torchvision.io import read_image
from torchvision.transforms.functional import to_pil_image

print_za_log = True
removeCorrupted = True
moveCorrupted = False
batch_size = 4

if removeCorrupted and moveCorrupted:
    raise ValueError("removeCorrupted and moveCorrupted cannot both be True. Please set one to False.")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def check_images(file_paths):
    valid_files = []
    for file_path in file_paths:
        try:
            tensor = read_image(file_path).to(device)
            img = to_pil_image(tensor)
            valid_files.append(True)
        except Exception:
            valid_files.append(False)
    return valid_files

def handle_corrupted(file_path):
    if removeCorrupted:
        os.remove(file_path)
        if print_za_log:
            print(f"{file_path} has been removed.")
    elif moveCorrupted:
        corrupted_folder = os.path.join(os.path.dirname(file_path), 'corrupted_folder')
        os.makedirs(corrupted_folder, exist_ok=True)
        os.rename(file_path, os.path.join(corrupted_folder, os.path.basename(file_path)))
        if print_za_log:
            print(f"{file_path} has been moved to {corrupted_folder}.")

def check_images_in_directory(directory_path):
    batch_paths = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                if len(batch_paths) < batch_size:
                    batch_paths.append(os.path.join(root, file))
                else:
                    valid_files = check_images(batch_paths)
                    for idx, valid in enumerate(valid_files):
                        if valid:
                            if print_za_log:
                                print(f"{batch_paths[idx]} pass - not corrupted")
                        else:
                            if print_za_log:
                                print(f"{batch_paths[idx]} not pass - maybe corrupted")
                            handle_corrupted(batch_paths[idx])
                    batch_paths = []

    if batch_paths:
        valid_files = check_images(batch_paths)
        for idx, valid in enumerate(valid_files):
            if valid:
                if print_za_log:
                    print(f"{batch_paths[idx]} pass - not corrupted")
            else:
                if print_za_log:
                    print(f"{batch_paths[idx]} not pass - maybe corrupted")
                handle_corrupted(batch_paths[idx])

root_directory = 'path/to/your/images'
check_images_in_directory(root_directory)
