import torch
from pathlib import Path
import os
from PIL import Image

custom_weights = '/content/yolov5s_anime.pt'
input_folder = '/content/gallery-dl/safebooru/yor_briar 1girl solo sweater'
output_folder = '/content/yor_face'
expand_box = 1.5
render_box = False
print_log = False

os.makedirs(output_folder, exist_ok=True)

model = torch.hub.load('ultralytics/yolov5', 'custom', path=custom_weights, force_reload=True)

def adjust_bbox(bbox, expand_factor, img_width, img_height):
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1
    new_width = width * expand_factor
    new_height = height * expand_factor
    new_x1 = max(x1 - (new_width - width) / 2, 0)
    new_y1 = max(y1 - (new_height - height) / 2, 0)
    new_x2 = min(x2 + (new_width - width) / 2, img_width)
    new_y2 = min(y2 + (new_height - height) / 2, img_height)
    return new_x1, new_y1, new_x2, new_y2

for img_path in Path(input_folder).glob('*.*'):
    results = model(img_path)

    if not render_box:
        original_img = Image.open(img_path)
        img_width, img_height = original_img.size
    else:
        rendered_img = results.render()[0]
        img_height, img_width, _ = rendered_img.shape

    for idx, det in enumerate(results.xyxy[0]):
        bbox = adjust_bbox(det[:4].cpu().numpy(), expand_box, img_width, img_height)

        x1_new, y1_new, x2_new, y2_new = map(int, bbox)

        save_path = os.path.join(output_folder, f"{img_path.stem}_{idx}.jpg")

        if not render_box:
            cropped_img = original_img.crop((x1_new, y1_new, x2_new, y2_new))
            cropped_img.save(save_path)
        else:
            cropped_img = rendered_img[y1_new:y2_new, x1_new:x2_new]
            Image.fromarray(cropped_img).save(save_path)

    if print_log:
        print(f'Processed {img_path}')
