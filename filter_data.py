import argparse
import json
import os
import shutil

def filter_data(input_json, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_json, 'r') as f:
        data = json.load(f)

    for item in data:
        filename = item['filename']
        aesthetic_value = item['aesthetic']['aesthetic']
        not_aesthetic_value = item['aesthetic']['not_aesthetic']

        if aesthetic_value > not_aesthetic_value:
            dest_folder = os.path.join(output_dir, 'aesthetic')
        else:
            dest_folder = os.path.join(output_dir, 'not_aesthetic')

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        shutil.copy2(filename, dest_folder)

parser = argparse.ArgumentParser(description="Seleksi dataset berdasarkan estetika.")
parser.add_argument("--input", type=str, required=True, help="Path ke file JSON input.")
parser.add_argument("--output_dir", type=str, required=True, help="Direktori output untuk menyimpan file yang dipilih.")

args = parser.parse_args()
filter_data(args.input, args.output_dir)
