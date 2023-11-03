import os
import torch
import argparse
from PIL import Image
from tqdm import tqdm
from transformers import AutoModelForImageClassification, ViTImageProcessor

SUPPORTED_EXTENSIONS = [".jpg", ".png", ".jpeg"]

def clean_unsupported_files(folder):
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            if not filename.endswith(tuple(SUPPORTED_EXTENSIONS)) and not filename.endswith(".py"):
                unsupported_folder = os.path.join(root, "unsupported_files")
                if not os.path.exists(unsupported_folder):
                    os.makedirs(unsupported_folder)
                os.rename(os.path.join(root, filename), os.path.join(unsupported_folder, filename))

def classify_and_move(input_folder, model, processor, device, recursive=False):
    model.to(device)

    def process_image(image_path, root_folder):
        image = Image.open(image_path)
        inputs = processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            predicted_class = outputs.logits.argmax(dim=1).item()

        portrait_folder = os.path.join(root_folder, "portrait")
        not_portrait_folder = os.path.join(root_folder, "not_portrait")
        if not os.path.exists(portrait_folder):
            os.makedirs(portrait_folder)
        if not os.path.exists(not_portrait_folder):
            os.makedirs(not_portrait_folder)

        if predicted_class == 0:
            os.rename(image_path, os.path.join(not_portrait_folder, os.path.basename(image_path)))
        else:
            os.rename(image_path, os.path.join(portrait_folder, os.path.basename(image_path)))

    if recursive:
        for root, _, filenames in os.walk(input_folder):
            for filename in tqdm(filenames, desc=f"Processing {root}", unit="file"):
                if filename.endswith(tuple(SUPPORTED_EXTENSIONS)):
                    process_image(os.path.join(root, filename), root)
    else:
        filenames = [f for f in os.listdir(input_folder) if f.endswith(tuple(SUPPORTED_EXTENSIONS))]
        for filename in tqdm(filenames, desc=f"Processing {input_folder}", unit="file"):
            process_image(os.path.join(input_folder, filename), input_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify images and move them to appropriate folders.")
    parser.add_argument("--this_dir", action="store_true", help="Use the current directory as the input folder.")
    parser.add_argument("--input", type=str, help="Specify the input folder.")
    parser.add_argument("--recursive", action="store_true", help="Process all subfolders recursively.")
    parser.add_argument("--use_gpu", action="store_true", help="Use GPU for processing if available.")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size for processing images.")
    parser.add_argument("--num_workers", type=int, default=4, help="Number of workers for data loading.")
    
    args = parser.parse_args()

    device = "cuda" if args.use_gpu and torch.cuda.is_available() else "cpu"

    processor = ViTImageProcessor.from_pretrained("ArielACE/real_classifier_v1")
    model = AutoModelForImageClassification.from_pretrained("ArielACE/real_classifier_v1")
    model.eval()

    if args.input:
        clean_unsupported_files(args.input)
        classify_and_move(args.input, model, processor, device, args.recursive)
    elif args.this_dir:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        clean_unsupported_files(current_dir)
        classify_and_move(current_dir, model, processor, device, args.recursive)
    else:
        print("Please provide an input method: either --this_dir or --input <path_to_folder>.")
