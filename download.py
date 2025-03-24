# python download.py --json_path video_data/20250218_1042/videos.json --label_collections cam_motion cam_setup
# python download.py --json_path video_data/20250219_0338/videos.json --label_collections cam_motion
# from download import get_labels
# motion_labels = get_labels("video_labels/cam_motion-20250219_0338/label_names_subset.json")
# shotcomp_labels = get_labels("video_labels/cam_motion-cam_setup-20250218_1042/label_names_subset.json")
# shot_size_change_label = shotcomp_labels["cam_setup.shot_size.shot_size_change"]
# print(f"'{shot_size_change_label['definition']}' has {len(shot_size_change_label['pos'])} positive examples")
import os
from tqdm import tqdm
from label import Label, extract_labels_dict
import argparse
import json
from process_json import json_to_video_data
import subprocess

HF_PREFIX = "https://huggingface.co/datasets/zhiqiulin/video_captioning/resolve/main/"

def save_to_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
        
def load_from_json(path):
    with open(path, "r") as f:
        return json.load(f)

def download_videos(video_data_dict, video_dir="videos"):
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    print(f"Downloading {len(video_data_dict)} videos to {video_dir}")
    failed_videos = []

    for video_name, video_data in tqdm(video_data_dict.items()):
        path = os.path.join(video_dir, video_name)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            continue

        url = HF_PREFIX + video_name
        result = subprocess.run(
            ["wget", url, "-O", path, "-q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if result.returncode != 0:
            print(f"Failed to download {video_name}. Removing from dictionary.")
            if os.path.exists(path):
                os.remove(path)
            failed_videos.append(video_name)

    # Remove failed videos from the dictionary
    for video in failed_videos:
        del video_data_dict[video]
    print(f"Successfully downloaded {len(video_data_dict)} videos")
    print(f"Failed to download {len(failed_videos)} videos, saving them to failed_videos.json")
    save_to_json(failed_videos, os.path.join(video_dir, "failed_videos.json"))
    return video_data_dict

def get_valid_labels_dict(video_data_dict, label_collections=["cam_motion", "cam_setup"]):
    video_data_list = list(video_data_dict.values())
    labels = Label.load_all_labels()
    all_valid_labels_dict = {}
    for label_collection in label_collections:
        labels_dict = extract_labels_dict(getattr(labels, label_collection), label_collection)
        invalid_labels = []
        for label_name, label in labels_dict.items():
            # call verify()
            try:
                label.verify(video_data_list)
            except Exception as e:
                print(f"Skipping {label_name}: {e}")
                invalid_labels.append(label_name)
                continue
        if len(invalid_labels) > 0:
            print(f"Skipping {len(invalid_labels)} invalid labels for {label_collection}: {invalid_labels}")
            for label_name in invalid_labels:
                labels_dict.pop(label_name)
        all_valid_labels_dict.update(labels_dict)

    return all_valid_labels_dict

def get_video_labels_dir(json_path, label_collections=["cam_motion", "cam_setup"], video_labels_dir="video_labels"):
    timestamp = json_path.split(os.sep)[-2]
    collection_name = "-".join(label_collections)
    return os.path.join(video_labels_dir, f"{collection_name}-{timestamp}")

def label_video_mapping(video_data_dict, valid_labels_dict, json_path, label_collections=["cam_motion", "cam_setup"], video_labels_dir="video_labels"):
    video_labels_dir = get_video_labels_dir(json_path, label_collections, video_labels_dir)
    labels_dir = os.path.join(video_labels_dir, "labels")
    
    if not os.path.exists(labels_dir):
        os.makedirs(labels_dir)
    
    all_label_path = os.path.join(video_labels_dir, "all_labels.json")
    label_name_path = os.path.join(video_labels_dir, "label_names.json")
    # Only load label JSON files if they already exist
    if os.path.exists(all_label_path):
        sorted_labels = load_from_json(all_label_path)
        sorted_labels_list = load_from_json(label_name_path)
        # Only return labels in label_names.json
        return {name: sorted_labels[name] for name in sorted_labels_list}
    
    # Otherwise, create label JSON files
    video_data_list = list(video_data_dict.values())
    label_to_videos_dict = {}
    for label_name, label in valid_labels_dict.items():
        label_path = os.path.join(labels_dir, f"{label_name}.json")
        label_to_videos = {
            "label": label_name,
            "label_name": label.label,
            "definition": label.def_question[0],
            "pos": [data.workflows[0].video_name for data in label.pos(video_data_list)],
            "neg": [data.workflows[0].video_name for data in label.neg(video_data_list)]
        }
        save_to_json(label_to_videos, label_path)
        if len(label_to_videos["pos"]) == 0:
            print(f"Skipping {label_name}: no positive examples")
        elif len(label_to_videos["neg"]) == 0:
            print(f"Skipping {label_name}: no negative examples")
        else:
            label_to_videos_dict[label_name] = label_to_videos
    
    # Sort labels by number of positive examples
    sorted_labels = sorted(label_to_videos_dict.items(), key=lambda x: len(x[1]["pos"]), reverse=True)
    sorted_labels = {label_name: label_to_videos for label_name, label_to_videos in sorted_labels}
    # print all label names and number of positive examples and negative examples
    for label_name, label_to_videos in sorted_labels.items():
        print(f"{label_name}: {len(label_to_videos['pos'])} positive examples, {len(label_to_videos['neg'])} negative examples")
    save_to_json(sorted_labels, all_label_path)
    sorted_labels_list = [name for name in sorted_labels.keys()]
    save_to_json(sorted_labels_list, label_name_path)
    return sorted_labels

def get_label_video_mapping(json_path, label_collections=["cam_motion", "cam_setup"], video_labels_dir="video_labels", video_dir="videos"):
    video_data_dict = json_to_video_data(json_path, label_collections=label_collections)
    valid_labels_dict = get_valid_labels_dict(video_data_dict, label_collections=label_collections)
    video_data_dict = download_videos(video_data_dict, video_dir=video_dir)
    label_to_videos = label_video_mapping(
        video_data_dict,
        valid_labels_dict,
        json_path=json_path,
        label_collections=label_collections,
        video_labels_dir=video_labels_dir
    )
    print_rare_labels(video_data_dict, valid_labels_dict, save_dir=get_video_labels_dir(json_path, label_collections, video_labels_dir))
    return label_to_videos

def get_labels(selected_json_path):
    selected_label_names = load_from_json(selected_json_path)
    label_dir = os.path.dirname(selected_json_path)
    all_labels = load_from_json(os.path.join(label_dir, "all_labels.json"))
    selected_labels = {name: all_labels[name] for name in selected_label_names}
    return selected_labels

def print_rare_labels(video_data_dict, valid_labels_dict, rare_threshold=30, save_dir="video_labels"):
    # print all rare labels in markdown format
    save_path = os.path.join(save_dir, f"rare_labels_under_{rare_threshold}.md")
    video_data_list = list(video_data_dict.values())
    label_to_videos_dict = {}
    for label_name, label in valid_labels_dict.items():
        label_to_videos = {
            "label": label_name,
            "label_name": label.label,
            "definition": label.def_question[0],
            "pos": [data.workflows[0].video_name for data in label.pos(video_data_list)],
            "neg": [data.workflows[0].video_name for data in label.neg(video_data_list)]
        }
        label_to_videos_dict[label_name] = label_to_videos
    
    # Sort labels by number of positive examples
    sorted_labels = sorted(label_to_videos_dict.items(), key=lambda x: len(x[1]["pos"]), reverse=True)
    sorted_labels = {label_name: label_to_videos for label_name, label_to_videos in sorted_labels}
    with open(save_path, "w") as f:
        f.write("# Rare Labels\n")
        f.write(f"Labels with less than {rare_threshold} positive examples\n")
        f.write("| Definition | Positive Examples | Negative Examples | Label Name |\n")
        f.write("| --- | --- | --- | --- |\n")
        for label_name, label_data in sorted_labels.items():
            if len(label_data["pos"]) < rare_threshold:
                definition = label_data['definition'].split("\n")[0]  # Ensure single-line definition
                f.write(f"| {definition} | {len(label_data['pos'])} | {len(label_data['neg'])} | {label_name} |\n")
    print(f"Saved rare labels to {save_path}")
    

def main():
    parser = argparse.ArgumentParser(description="Get labels and video data.")
    parser.add_argument("--json_path", type=str,
                        default="video_data/20250218_1042/videos.json",
                        help="Path to the JSON file containing video data.")
    parser.add_argument("--label_collections", nargs="+", type=str,
                        default=["cam_motion", "cam_setup"],
                        help="List of labelbox project to use.")
    parser.add_argument("--video_dir", type=str,
                        default="videos",
                        help="Output directory to save the downloaded videos.")
    parser.add_argument("--video_labels_dir", type=str,
                        default="video_labels",
                        help="Output directory to save the video labels JSON files.")
    parser.add_argument("--rare_threshold", type=int,
                        default=30,
                        help="Threshold for rare labels.")
    args = parser.parse_args()
    
    label_to_videos = get_label_video_mapping(
        args.json_path,
        label_collections=args.label_collections,
        video_labels_dir=args.video_labels_dir,
        video_dir=args.video_dir
    )
    

if __name__ == "__main__":
    main()
