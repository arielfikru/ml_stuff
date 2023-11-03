!apt install aria2
!pip install huggingface_hub

import requests
import json
import os
import sys
import subprocess
import time
import zipfile
from datetime import datetime
from huggingface_hub import upload_file

download_dir = "/content/skadi"
search_tags = "skadi_(arknights)"
banned_tag = "parody,comic,chibi,monochrome,lowres,3koma,4koma,manga,speech_bubble,1boy,2boys,3boys"
keep_tag = "1girl"
conditional_tag = ""
from_date = ""
to_date = ""
save_tags = True
save_json = True
save_json_all = True
min_score = 10
max_score = 500
max_pages = 100
limit_params = 100
force_max_download = 1000
rating_banned = "e,s,q"
copyright_tag = False
artist_tag = False
meta_tag = False
score_tag = False
prefix_score = False


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
            #print(f"Attempt {attempt + 1} failed, retrying in 5 seconds...")
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
            post.get("score", 0) > max_score or
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
    formatted_tags = formatted_tags.replace(" ", ", ")
    formatted_tags = formatted_tags.replace("_", " ")
    formatted_tags = formatted_tags.replace(", (", " (")

    while ",, " in formatted_tags:
        formatted_tags = formatted_tags.replace(",, ", ", ")

    with open(os.path.join(download_path, f"{file_name_without_ext}.txt"), "w") as f:
        f.write(formatted_tags)


def save_post_as_json(post, download_path, file_name_without_ext):
    json_path = os.path.join(download_path, f"{file_name_without_ext}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(post, f, ensure_ascii=False, indent=4)

def zip_directory(output_filename, dir_name):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dir_name):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), dir_name)
                )

def upload_to_huggingface(local_file_path, repo_id, repo_type, token, commit_message, add_dir):
    filename_with_extension = os.path.basename(local_file_path)
    path_in_repo = os.path.join(add_dir, filename_with_extension)

    upload_file(
        path_or_fileobj=local_file_path,
        path_in_repo=path_in_repo,
        repo_id=repo_id,
        repo_type=repo_type,
        token=token,
        commit_message=commit_message,
    )
    print(f"File {path_in_repo} has been uploaded.")


api_url = "https://danbooru.donmai.us/posts.json"
params = {"limit": limit_params, "tags": search_tags}
headers = {"User-Agent": "Mozilla/5.0"}

def main():
    download_count = 0
    no_new_downloads_counter = 0

    for page in range(1, max_pages + 1):
        params['page'] = page
        response = requests.get(api_url, params=params, headers=headers)

        if response.status_code == 200:
            posts = response.json()
            try:
                filtered_posts = get_filtered_posts(posts, conditional_tag)
                if save_json_all:
                    all_posts_data.extend(filtered_posts)

                new_downloads_this_page = 0

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
                            download_count += 1
                            new_downloads_this_page += 1  # increment ini
                            print(f"\rDownloaded {download_count} images", end="")
                            sys.stdout.flush()

                            if download_count >= force_max_download:
                                print("\nReached the maximum allowed downloads. Exiting...")
                                return

                            if save_tags:
                                tags_to_save = post.get("tag_string_character", "")
                                save_tags_as_txt(tags_to_save, download_path, file_prefix + file_name_without_ext, score,
                                                 score_tag, copyright_tag, artist_tag, meta_tag, post)

                            if save_json and not save_json_all:
                                save_post_as_json(post, download_path, file_prefix + file_name_without_ext)
                                
                    if page == max_pages and save_json_all:
                        with open(os.path.join(download_dir, "meta_booru.json"), "w", encoding="utf-8") as f:
                            json.dump(all_posts_data, f, ensure_ascii=False, indent=4)
                            
                if new_downloads_this_page == 0:
                    no_new_downloads_counter += 1
                    if no_new_downloads_counter >= 60:
                        print("\nNo new downloads for 1 minute. Exiting...")
                        break
                else:
                    no_new_downloads_counter = 0

            except ValueError as e:
            
                print("\nError:", e)

if __name__ == "__main__":
    main()

    print("\nZipping downloaded images...")
    zip_output_filename = f"{os.path.basename(download_dir)}.zip"
    zip_directory(zip_output_filename, download_dir)
    uploads_path = zip_output_filename
    repo_id = "ArielACE/Training"
    repo_type = "dataset"
    token = "X"
    commit_message = "Scenery"
    add_dir = "/dataset_raw/"

    upload_to_huggingface(uploads_path, repo_id, repo_type, token, commit_message, add_dir)
