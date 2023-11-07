import cv2
import torch
from PIL import Image, ImageFile
from pathlib import Path
import os
import urllib.request
import argparse
import subprocess

ImageFile.LOAD_TRUNCATED_IMAGES = True

parser = argparse.ArgumentParser(description='Crop faces from images using YOLOv5 model.')
parser.add_argument('--input', type=str, default='./input', help='Folder path to input images.')
parser.add_argument('--output', type=str, default='./output', help='Folder path for saving output images.')
parser.add_argument('--weights', type=str, help='Path to model weights file.')
parser.add_argument('--resolution', type=int, nargs=2, default=[512, 512], help='Resolution for the output images. Pass as two numbers.')
parser.add_argument('--confidence', type=float, default=0.5, help='Confidence threshold for detection.')
parser.add_argument('--margin', type=float, default=0.2, help='Margin percentage to add around the detected face.')
parser.add_argument('--recursive', action='store_true', help='Recursively process images in subfolders.')
parser.add_argument('--no_log', action='store_true', help='Disable logging of processed faces.')
parser.add_argument('--batch_size', type=int, default=4, help='Number of images to process in a batch.')
parser.add_argument('--use_cuda', action='store_true', help='Use CUDA for processing if available.')

args = parser.parse_args()

downloads_dir = Path(__file__).parent / 'downloads'
downloads_dir.mkdir(exist_ok=True)

default_weights_url = "https://huggingface.co/nekofura/yolo/resolve/main/yolov5s_anime.pt"
weights_filename = 'yolov5s_anime.pt'
local_weights_path = downloads_dir / weights_filename
if not local_weights_path.exists() and not args.weights:
    print(f"Downloading model weights to {local_weights_path}")
    urllib.request.urlretrieve(default_weights_url, local_weights_path)

model_weights = args.weights or str(local_weights_path)

yolov5_repo_path = downloads_dir / 'yolov5'
if not yolov5_repo_path.exists():
    subprocess.run(['git', 'clone', '--depth', '1', 'https://github.com/ultralytics/yolov5', str(yolov5_repo_path)], check=True)

device = 'cuda' if torch.cuda.is_available() and args.use_cuda else 'cpu'

model = torch.hub.load(str(yolov5_repo_path), 'custom', path=model_weights, source='local', force_reload=False).to(device)

def strip_icc_profile(image_path):
    try:
        with Image.open(image_path) as img:
            img.info.pop('icc_profile', None)
            img.save(image_path, format=img.format)
    except OSError:
        print(f"Error encountered with image {image_path}. Removing corrupted image.")
        os.remove(image_path)

def add_margin(x1, y1, x2, y2, width, height, margin):
    x1 = max(x1 - margin, 0)
    y1 = max(y1 - margin, 0)
    x2 = min(x2 + margin, width - 1)
    y2 = min(y2 + margin, height - 1)
    return int(x1), int(y1), int(x2), int(y2)

def process_detections(input_image_path, detections, output_directory, target_resolution, margin_percentage, no_log):
    image = cv2.imread(input_image_path)
    height, width, _ = image.shape
    face_count = 0
    for detection in detections:
        x1, y1, x2, y2, conf, cls = detection
        margin = margin_percentage * min(x2 - x1, y2 - y1)
        x1, y1, x2, y2 = add_margin(x1, y1, x2, y2, width, height, margin)
        cropped_face = image[int(y1):int(y2), int(x1):int(x2)]
        resized_face = cv2.resize(cropped_face, target_resolution)
        original_file_name = Path(input_image_path).stem
        face_filename = f"{output_directory}/{original_file_name}.jpg" if face_count == 0 else f"{output_directory}/{original_file_name}_face_{face_count}.jpg"
        cv2.imwrite(face_filename, resized_face)
        if not no_log:
            print(f"Face {face_count} saved to {face_filename}")
        face_count += 1

def process_batch(batch, output_directory, target_resolution, confidence_threshold, margin_percentage, no_log):
    images = [cv2.imread(img_path) for img_path in batch]
    results = model(images, size=640)
    for img_path, result in zip(batch, results.pred):
        detections = result
        detections = detections[detections[:, 4] >= confidence_threshold]
        process_detections(img_path, detections, output_directory, target_resolution, margin_percentage, no_log)

def process_images(input_path, output_directory, target_resolution, confidence_threshold, margin_percentage, no_log, batch_size):
    batch = []
    for root, dirs, files in os.walk(input_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(root, file)
                strip_icc_profile(image_path)  # Strip the ICC profile
                batch.append(image_path)
                if len(batch) >= batch_size:
                    process_batch(batch, output_directory, target_resolution, confidence_threshold, margin_percentage, no_log)
                    batch = []
        if not args.recursive:
            break
    if batch:
        process_batch(batch, output_directory, target_resolution, confidence_threshold, margin_percentage, no_log)


output_path = Path(args.output)
output_path.mkdir(parents=True, exist_ok=True)

process_images(args.input, output_path, args.resolution, args.confidence, args.margin, args.no_log, args.batch_size)
