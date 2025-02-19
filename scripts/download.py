import wget
import json
import argparse
import os
import subprocess


def main():
    parser = argparse.ArgumentParser(description="Download video data from a JSON file.")
    parser.add_argument("--json_path", type=str,
                        default="video_labels/video_info.json",
                        help="Path to the JSON file containing video meta info.")
    parser.add_argument("--output_dir", type=str,
                        default="./output", help="Path to save the videos")

    args = parser.parse_args()
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    with open(args.json_path, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    for key, value in loaded_data.items():
        video_names = value["positive"]
        for video_name in video_names:
            url = "https://huggingface.co/datasets/zhiqiulin/video_captioning/resolve/main/" + video_name
            output_path = os.path.join(output_dir, video_name)
            result = subprocess.run(['wget', '-O', output_path, url])


if __name__ == '__main__':
    main()