import torch
from pathlib import Path
import os
from PIL import Image

custom_weights = '/content/yolov5s_anime.pt'
input_folder = '/content/gallery-dl/safebooru/yor_briar 1girl solo sweater'
output_folder = '/content/yor_face'
expand_box = 1.5
print_log = True

os.makedirs(output_folder, exist_ok=True)

model = torch.hub.load('ultralytics/yolov5', 'custom', path=custom_weights, force_reload=True)

def adjust_bbox(bbox, expand_factor):
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1
    new_width = width * expand_factor
    new_height = height * expand_factor
    new_x1 = x1 - (new_width - width) / 2
    new_y1 = y1 - (new_height - height) / 2
    new_x2 = x2 + (new_width - width) / 2
    new_y2 = y2 + (new_height - height) / 2
    return new_x1, new_y1, new_x2, new_y2

expand_factor = expand_box

for img_path in Path(input_folder).glob('*.*'):
    results = model(img_path)

    original_img = Image.open(img_path)

    for idx, det in enumerate(results.xyxy[0]):
        bbox = adjust_bbox(det[:4].cpu().numpy(), expand_factor)

        x1_new, y1_new, x2_new, y2_new = bbox
        x1_new, y1_new, x2_new, y2_new = map(int, [x1_new, y1_new, x2_new, y2_new])

        x1_new, y1_new = max(x1_new, 0), max(y1_new, 0)
        x2_new, y2_new = min(x2_new, original_img.size[0]), min(y2_new, original_img.size[1])

        save_path = os.path.join(output_folder, f"{img_path.stem}_{idx}.jpg")

        cropped_img = original_img.crop((x1_new, y1_new, x2_new, y2_new))
        cropped_img.save(save_path)

    if print_log:
      print(f'Processed {img_path}')
