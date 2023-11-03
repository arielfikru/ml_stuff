import os
import random
import time
import threading
import subprocess

sample_prompt = "/content/fine_tune/config/sample_prompt.txt"
config_file = "/content/fine_tune/config/config_file.toml"

def get_random_txt_content(folder_path):
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt') and os.path.isfile(os.path.join(folder_path, f))]
    
    selected_file = random.choice(txt_files)
    
    with open(os.path.join(folder_path, selected_file), 'r') as f:
        content = f.read().strip()
    
    return content

def update_sample_prompt():
    folder_path = "/content/fine_tune/train_data"

    while True:
        content = get_random_txt_content(folder_path)
        tags = content.split(",")
        random.shuffle(tags
        
        reduction = random.randint(0, len(tags) // 2)
        tags = tags[:-reduction]
        
        tags_to_remove = [", full body", ", simple background", ", white background"]
        tags = [tag for tag in tags if tag not in tags_to_remove]
        
        shuffled_content = ",".join(tags)
        
        if not any(tag in shuffled_content for tag in ["boy", "girl"]):
            gender_tag = random.choice(["1boy", "1girl"])
            shuffled_content = gender_tag + "," + shuffled_content
        
        new_content = f"masterpiece, best quality, {shuffled_content}   --n lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry   --w 512   --h 768   --l 7   --s 28"
        
        with open(sample_prompt, 'w') as f:
            f.write(new_content)

        time.sleep(180) 

def main_training():
    accelerate_conf = {
        "config_file" : accelerate_config,
        "num_cpu_threads_per_process" : 1,
    }

    train_conf = {
        "sample_prompts" : sample_prompt,
        "config_file" : config_file
    }

    def train(config):
        args = ""
        for k, v in config.items():
            if k.startswith("_"):
                args += f'"{v}" '
            elif isinstance(v, str):
                args += f'--{k}="{v}" '
            elif isinstance(v, bool) and v:
                args += f"--{k} "
            elif isinstance(v, float) and not isinstance(v, bool):
                args += f"--{k}={v} "
            elif isinstance(v, int) and not isinstance(v, bool):
                args += f"--{k}={v} "

        return args

    accelerate_args = train(accelerate_conf)
    train_args = train(train_conf)
    final_args = f"accelerate launch {accelerate_args} fine_tune.py {train_args}"

    os.chdir(repo_dir)
    process = subprocess.Popen(final_args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(f"\r{output.strip()}", end="")
    process.poll()

thread1 = threading.Thread(target=update_sample_prompt)
thread2 = threading.Thread(target=main_training)

thread1.start()
thread2.start()

thread1.join()
thread2.join()
