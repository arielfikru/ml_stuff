import re
import json
import argparse
import openai
import os
import time 

tokens_used = 0

def translate_dialog(dialog, to_indonesia=False):
    global tokens_used

    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"Translate this Japanese dialogue to English: {dialog}",
        max_tokens=100,
        temperature=0
    )
    translated_english = response.choices[0].text.strip()
    tokens_used += response['usage']['total_tokens']

    print(f"'{dialog}' has been translated to '{translated_english}'")

    if to_indonesia:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Translate this English sentence to Indonesian: {translated_english}",
            max_tokens=100,
            temperature=0
        )
        translated_indonesian = response.choices[0].text.strip()
        tokens_used += response['usage']['total_tokens']
        print(f"'{translated_english}' has been translated to '{translated_indonesian}'")
        return translated_indonesian

    return translated_english


def srt_to_json(args):
    if not args.input_srt or not args.output_json:
        return
        
    with open(args.input_srt, 'r', encoding="utf-8") as file:
        content = file.read()
        blocks = content.split("\n\n")

        result = []
        skip_next = False

        request_count = 0
        start_time = time.time()

        for index, block in enumerate(blocks):
            if skip_next:
                skip_next = False
                continue

            lines = block.strip().split("\n")
            if len(lines) < 3:
                continue

            message = lines[0]
            time_range = lines[1]
            dialog = " ".join(lines[2:])

            if args.translate:
                dialog = translate_dialog(dialog)

            if args.free_mode and request_count >= 3:
                end_time = time.time()
                elapsed_time = end_time - start_time
                if elapsed_time < 20:
                    time.sleep(20 - elapsed_time)
                start_time = time.time()
                request_count = 0

            if args.translate or args.to_indonesia:
                request_count += 1

            if dialog.endswith("→") and index+1 < len(blocks):
                next_block = blocks[index+1].strip().split("\n")
                if len(next_block) >= 3:
                    next_dialog = " ".join(next_block[2:])
                    next_time_range = next_block[1]
                    _, next_time_end = map(str.strip, next_time_range.split("-->"))

                    dialog += " " + (translate_dialog(next_dialog) if args.translate else next_dialog)
                    time_end = next_time_end
                    skip_next = True
                else:
                    continue
            else:
                time_start, time_end = map(str.strip, time_range.split("-->"))
                
            dialog = dialog.replace("→", " ").strip()

            result.append({
                "message": message,
                "time_start": time_start,
                "time_end": time_end,
                "dialog": dialog
            })

        with open(args.output_json, 'w', encoding="utf-8") as out_file:
            json.dump(result, out_file, ensure_ascii=False, indent=4)

    if args.translate_to_srt:
        with open(args.input_srt.replace('.srt', '_translated.srt'), 'w', encoding="utf-8") as out_srt:
            for entry in result:
                out_srt.write(f"{entry['message']}\n")
                out_srt.write(f"{entry['time_start']} --> {entry['time_end']}\n")
                out_srt.write(f"{entry['dialog']}\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SRT to JSON converter and translator.")
    parser.add_argument("--input_srt", required=True, help="Input SRT file path.")
    parser.add_argument("--output_json", required=True, help="Output JSON file path.")
    parser.add_argument("--translate", action="store_true", help="Translate dialogues using OpenAI API.")
    parser.add_argument("--to_indonesia", action="store_true", help="Translate from Japanese to English and then to Indonesian.")
    parser.add_argument("--translate_to_srt", action="store_true", help="Output translated SRT.")
    parser.add_argument("--set_authtoken", help="Set OpenAI API authentication token.")
    parser.add_argument("--free_mode", action="store_true", help="Use free mode which sends 3 requests per minute.")

    args = parser.parse_args()

    if (args.translate or args.to_indonesia) and not args.set_authtoken:
        print("Error: You must set the OpenAI authentication token using --set_authtoken when using --translate or --to_indonesia.")
        exit()

    if args.set_authtoken:
        openai.api_key = args.set_authtoken

    srt_to_json(args)

    print(f"Total tokens used: {tokens_used}")
