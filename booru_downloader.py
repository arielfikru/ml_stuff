import requests
import json
import os
import subprocess
from datetime import datetime
import time

download_dir = "/content/arknights_aesthetic_sfw3"
search_tags = "arknights"
banned_tag = "parody,comic,chibi,monochrome"
keep_tag = ""
conditional_tag = "1other:2girl:3girl:2boy"
from_date = ""
to_date = ""
save_tags = True
save_json = True
save_json_all = True
max_pages = 100
min_score = 5
limit_params = 50
rating_banned = "e,s,q"
copyright_tag = False
artist_tag = False
meta_tag = False
prefix_score = False
score_tag = False
save_json = True
all_posts_data = []


supported_types = [
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".caption",
    ".npz",
    ".txt",
    ".json",
]

temp_dir = "/content/temp"
os.makedirs(temp_dir, exist_ok=True)


def download_image(url, download_path, prefix):
    file_name = os.path.basename(url)
    new_file_name = prefix + file_name if prefix_score else file_name
    
    for attempt in range(3):
        command = ["aria2c", url, "--dir", download_path, "--out", new_file_name]
        result = subprocess.run(command)
        if result.returncode == 0: 
            return True
        else:  
            print(f"Attempt {attempt + 1} failed, retrying in 5 seconds...")
            time.sleep(5)
    return False


def get_folder_name(rating):
    folder_map = {
        "g": "general",
        "q": "questionable",
        "s": "sensitive",
        "e": "explicit"
    }
    return folder_map.get(rating, "unknown")

def is_date_in_range(created_at, from_date, to_date):
    post_date = datetime.strptime(created_at.split("T")[0], "%Y-%m-%d")
    if not from_date and not to_date:
        return True
    elif from_date and not to_date:
        from_date_obj = datetime.strptime(from_date, "%d/%m/%Y")
        return from_date_obj <= post_date
    elif not from_date and to_date:
        to_date_obj = datetime.strptime(to_date, "%d/%m/%Y")
        return post_date <= to_date_obj
    else:
        from_date_obj = datetime.strptime(from_date, "%d/%m/%Y")
        to_date_obj = datetime.strptime(to_date, "%d/%m/%Y")
        if from_date_obj > to_date_obj:
            raise ValueError("Invalid date range: from_date is later than to_date.")
        return from_date_obj <= post_date <= to_date_obj

def get_filtered_posts(posts, conditional_tag):
    filtered_posts = []
    for post in posts:
        file_ext = post.get("file_ext")
        
        if (
            post.get("score", 0) < min_score or 
            any(tag in post.get("tag_string", "").split(" ") for tag in banned_tag.split(",")) or 
            (keep_tag and not all(tag in post.get("tag_string", "").split(" ") for tag in keep_tag.split(","))) or 
            not is_date_in_range(post.get("created_at"), from_date, to_date) or 
            post.get("rating") in rating_banned.split(",") or 
            (f".{file_ext}" not in supported_types) or
            not meets_conditional_tag_condition(post, conditional_tag)
        ):
            continue
        
        filtered_posts.append(post)
        
    return filtered_posts

def meets_conditional_tag_condition(post, conditional_tag):
    if not conditional_tag or len(conditional_tag.split(":")) < 2:
        return True
    
    post_tags = set(post.get("tag_string", "").split(" "))
    conditional_tags = set(conditional_tag.split(":"))
    
    matching_tags_count = len(conditional_tags.intersection(post_tags))
    
    if matching_tags_count >= 2:
        return False
    
    return True

def get_file_prefix(score):
    if score >= 100:
        return "masterpiece_"
    elif 50 <= score <= 99:
        return "best_quality_"
    elif 11 <= score <= 49:
        return "high_quality_"
    elif 5 <= score <= 10:
        return "bad_quality_"
    elif score <= 4:
        return "worst_quality_"
    else:
        return ""

def save_tags_as_txt(tags, download_path, file_name_without_ext, score, score_tag, 
                     copyright_tag, artist_tag, meta_tag, post):
    
    tags_list = []

    if score_tag:
        score_string = get_file_prefix(score).replace("_", " ").strip()
        tags_list.append(score_string)
    
    tags_list.append(tags)
    
    if copyright_tag:
        tags_list.append(post.get("tag_string_copyright", ""))
    if artist_tag:
        tags_list.append(post.get("tag_string_artist", ""))
    if meta_tag:
        tags_list.append(post.get("tag_string_meta", ""))
    
    tags_list.append(post.get("tag_string_general", ""))
    
    final_tags_string = ", ".join(filter(None, tags_list))

    formatted_tags = final_tags_string.replace("_(", " (")
    formatted_tags = formatted_tags.replace("_", " ")
    formatted_tags = formatted_tags.replace(" ", ", ")
    formatted_tags = formatted_tags.replace(", (", " (")
    
    while ",, " in formatted_tags:
        formatted_tags = formatted_tags.replace(",, ", ", ")
    
    with open(os.path.join(download_path, f"{file_name_without_ext}.txt"), "w") as f:
        f.write(formatted_tags)


def save_post_as_json(post, download_path, file_name_without_ext):
    json_path = os.path.join(download_path, f"{file_name_without_ext}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(post, f, ensure_ascii=False, indent=4)


api_url = "https://danbooru.donmai.us/posts.json"
params = {"limit": limit_params, "tags": search_tags}
headers = {"User-Agent": "Mozilla/5.0"}


for page in range(1, max_pages + 1):
    params['page'] = page  
    response = requests.get(api_url, params=params, headers=headers)
    
    if response.status_code == 200:
        posts = response.json()
        try:
            filtered_posts = get_filtered_posts(posts, conditional_tag)
            if save_json_all:
                all_posts_data.extend(filtered_posts)
                        
            for post in filtered_posts:
                image_url = post.get("file_url")
                if image_url:
                    score = post.get("score", 0)
                    file_name = os.path.basename(image_url)
                    file_name_without_ext = os.path.splitext(file_name)[0]
                    subfolder_name = get_folder_name(post["rating"])
                    download_path = os.path.join(download_dir, subfolder_name)
                    os.makedirs(download_path, exist_ok=True)
                        
                    file_prefix = get_file_prefix(score) if prefix_score else "" 
                        
                    if download_image(image_url, download_path, file_prefix): 
                        print(f"Downloading {file_name} to {subfolder_name}...")

                        if save_tags:
                            tags_to_save = post.get("tag_string_character", "")
                            save_tags_as_txt(tags_to_save, download_path, file_prefix + file_name_without_ext, score, 
                                             score_tag, copyright_tag, artist_tag, meta_tag, post)
                            
                        if save_json and not save_json_all:
                            save_post_as_json(post, download_path, file_prefix + file_name_without_ext)

                    else:
                        print(f"Failed to download {file_name} to {subfolder_name} after 3 attempts, skipping...")

                if page == max_pages and save_json_all:
                    with open(os.path.join(download_dir, "meta_booru.json"), "w", encoding="utf-8") as f:
                        json.dump(all_posts_data, f, ensure_ascii=False, indent=4)

        except ValueError as e:
            print("Error:", e)
    else:
        print(f"Failed to retrieve data for page {page}: ", response.status_code)

