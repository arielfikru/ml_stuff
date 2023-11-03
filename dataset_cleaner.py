import os
import shutil
import random

def move_random_files(source_folder, dest_folder, n, seed=0):
    """
    Memindahkan n file secara acak dari source_folder ke dest_folder.

    Parameters:
    - source_folder: Path ke folder sumber.
    - dest_folder: Path ke folder tujuan.
    - n: Jumlah file yang ingin dipindahkan.
    - seed: Seed untuk random.
    """
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    all_files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]

    if len(all_files) < n:
        raise ValueError(f"Only {len(all_files)} files found, but {n} files requested to be moved.")

    random.seed(seed)

    selected_files = random.sample(all_files, n)

    for file_name in selected_files:
        source_path = os.path.join(source_folder, file_name)
        dest_path = os.path.join(dest_folder, file_name)
        shutil.move(source_path, dest_path)
        print(f"Moved {file_name} from {source_folder} to {dest_folder}")

if __name__ == "__main__":
    SOURCE_FOLDER = r'C:\Users\OP Team\Pictures\Image Classifier\Bad'
    DEST_FOLDER = r'C:\Users\OP Team\Pictures\Image Classifier\Bad_Clean'
    FILE_COUNT = 30
    SEED = 42

    move_random_files(SOURCE_FOLDER, DEST_FOLDER, FILE_COUNT, SEED)
