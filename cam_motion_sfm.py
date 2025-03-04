# Evaluate on camera-centric benchmark
# python cam_motion_sfm.py --sfm_method megasam_posed_videos
# python cam_motion_sfm.py --sfm_method cut3r_posed_videos
import argparse
import os
import sys
import json
from pathlib import Path

ROOT = Path("./")
VIDEO_ROOT = Path("./videos")

from benchmark import labels_as_dict, BinaryTask

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--root",
    type=str,
    help="The root directory for saved datasets",
    default=ROOT,
)
parser.add_argument(
    "--video_root",
    type=str,
    help="The root directory for saved videos",
    default=VIDEO_ROOT,
)
parser.add_argument(
    "--video_label_file",
    type=str,
    help="The video label to use",
    # default="video_labels/cam_motion-20250219_0338/label_names.json", @ noisy 4000
    # default="video_labels/cam_motion-cam_setup-20250218_1042/label_names.json", # good initial set of around 2000
    # default="video_labels/cam_motion-20250223_0313/label_names_subset.json", # only a subset of 300 videos
    # default="video_labels/cam_motion-20250223_2308/label_names_selected.json", # the full set of 2000 videos for cam-centric
    # default="video_labels/cam_motion-cam_setup-20250224_0130/label_names_selected.json", # the full set of 2384 videos for ground-centric + shotcomp
    default="video_labels/cam_motion-20250227_0326ground_and_camera/label_names_selected.json", # Finalized cam-centric benchmark
    nargs="?",
)
parser.add_argument(
    "--save_dir",
    type=str,
    help="The directory to save the results",
    default="./temp/",
)
parser.add_argument(
    "--sfm_dir",
    type=str,
    help="The directory to load the sfm data",
    default="sfm_outputs/",
)
parser.add_argument(
    "--sfm_method",
    type=str,
    help="The sfm method to use",
    default="megasam_posed_videos",
    # default="cut3r_posed_videos",
)
args = parser.parse_args()


video_label_str = "_".join(args.video_label_file.split("/")[-2:])[:-5]

SAVE_DIR = Path(args.save_dir) / f"{video_label_str}" 
if not SAVE_DIR.exists():
    SAVE_DIR.mkdir(parents=True)

all_labels = labels_as_dict(root=args.root, video_label_file=args.video_label_file, video_root=args.video_root)


print(f"Loaded {len(all_labels)} labels")
label_counts = {}
for label_name in all_labels:
    pos = len(all_labels[label_name]['pos'])
    neg = len(all_labels[label_name]['neg'])
    label_counts[label_name] = pos + neg

for label_name in all_labels:
    print(
        f"{all_labels[label_name]['label_name']:100s}: Positives: {len(all_labels[label_name]['pos']):10d}, Negatives: {len(all_labels[label_name]['neg']):10d}"
    )
    # Random chance AP is the ratio of positives to total samples
    print(
        f"Random Chance AP: {len(all_labels[label_name]['pos']) / label_counts[label_name]:.4f}"
    )


def combine_pose_diff_files(parent_dir):
    parent_path = Path(parent_dir)
    combined_data = {}

    # Iterate through all subdirectories
    for subfolder in [f for f in parent_path.iterdir() if f.is_dir()]:
        video_name = subfolder.name
        json_path = subfolder / "pose_diff.json"

        # Check if pose_diff.json exists in this subfolder
        if json_path.exists():
            try:
                # Load the JSON file
                with open(json_path, "r") as file:
                    json_data = json.load(file)

                # Add to the combined dictionary with video name as key
                combined_data[video_name] = json_data
                # print(f"Loaded {video_name}/pose_diff.json")
            except json.JSONDecodeError:
                print(f"Error: Could not parse JSON in {json_path}")
            except Exception as e:
                print(f"Error reading {json_path}: {e}")

    print(f"Total videos processed: {len(combined_data)}")
    return combined_data


# def save_combined_data(combined_data, output_file="combined_pose_data.json"):
#     with open(output_file, "w") as file:
#         json.dump(combined_data, file, indent=2)

#     print(f"Combined data saved to {output_file}")


parent_directory = Path(args.sfm_dir) / args.sfm_method

# Combine all pose_diff.json files
combined_data = combine_pose_diff_files(parent_directory)

# example of Jay's output {
#     "delta_x": -0.5157333612442017,
#     "delta_y": -0.1708381623029709,
#     "delta_z": 0.1114729717373848,
#     "delta_yaw": -0.12438342533492158,
#     "delta_pitch": 0.60178686397772,
#     "delta_roll": -0.22627989475546217,
#     "delta_zoom": 1.0,
# }

camera_movement_mapping = {
    "cam_motion.steadiness_and_movement.fixed_camera": "Static",
    "cam_motion.camera_centric_movement.zoom_in.has_zoom_in": "Zoom In",
    "cam_motion.camera_centric_movement.zoom_out.has_zoom_out": "Zoom Out",
    "cam_motion.camera_centric_movement.forward.has_forward_wrt_camera": "Move In",
    "cam_motion.camera_centric_movement.backward.has_backward_wrt_camera": "Move Out",
    "cam_motion.camera_centric_movement.upward.has_upward_wrt_camera": "Move Up",
    "cam_motion.camera_centric_movement.downward.has_downward_wrt_camera": "Move Down",
    "cam_motion.camera_centric_movement.rightward.has_rightward": "Move Right",
    "cam_motion.camera_centric_movement.leftward.has_leftward": "Move Left",
    "cam_motion.camera_centric_movement.pan_right.has_pan_right": "Pan Right",
    "cam_motion.camera_centric_movement.pan_left.has_pan_left": "Pan Left",
    "cam_motion.camera_centric_movement.tilt_up.has_tilt_up": "Tilt Up",
    "cam_motion.camera_centric_movement.tilt_down.has_tilt_down": "Tilt Down",
    "cam_motion.camera_centric_movement.roll_clockwise.has_roll_clockwise": "Roll Clockwise",
    "cam_motion.camera_centric_movement.roll_counterclockwise.has_roll_counterclockwise": "Roll Counterclockwise",
}

def static_score(item):
    return max(
        abs(item["delta_x"]),
        abs(item["delta_y"]),
        abs(item["delta_z"]),
        abs(item["delta_yaw"] / 180),
        abs(item["delta_pitch"] / 180),
        abs(item["delta_roll"] / 180),
    )

motion_to_score = {
  "Static": lambda item: static_score(item),
  "Zoom In": lambda item: item['delta_zoom'],
  "Zoom Out": lambda item: -item['delta_zoom'],
  "Move In": lambda item: item['delta_z'],
  "Move Out": lambda item: -item['delta_z'],
  "Move Up": lambda item: item['delta_y'],
  "Move Down": lambda item: -item['delta_y'],
  "Move Right": lambda item: item['delta_x'],
  "Move Left": lambda item: -item['delta_x'],
  "Pan Right": lambda item: item['delta_yaw'],
  "Pan Left": lambda item: -item['delta_yaw'],
  "Tilt Up": lambda item: item['delta_pitch'],
  "Tilt Down": lambda item: -item['delta_pitch'],
  "Roll Clockwise": lambda item: item['delta_roll'],
  "Roll Counterclockwise": lambda item: -item['delta_roll'],
}

# def static_score(item):
#     return max()

# print all value names
print(camera_movement_mapping.values())

raw_scores = [
    "delta_x"
    "delta_y"
    "delta_z"
    "delta_yaw"
    "delta_pitch"
    "delta_roll"
    "delta_zoom"
]

all_labels_scores = {}
missing_videos = []
for label_name in all_labels:
    LABEL_SAVE_DIR = SAVE_DIR / label_name
    if not LABEL_SAVE_DIR.exists():
        LABEL_SAVE_DIR.mkdir(parents=True)
    LABEL_SAVE_PATH = LABEL_SAVE_DIR / f"{args.sfm_method}_scores.pt"

    dataset = BinaryTask(label_dict=all_labels[label_name])

    videos = [item["images"][0] for item in dataset]
    video_names = []
    for video in videos:
        video_name = Path(video).stem
        video_names.append(video_name)

    video_items = []
    for video_name in video_names:
        if video_name not in combined_data:
            # print(f"Video {video_name} not found in pose data")
            video_items.append(None)
            continue
        video_items.append(combined_data[video_name])

    if not all([video_name in combined_data for video_name in video_names]):
        print(f"Missing video number is {len([video_name for video_name in video_names if video_name not in combined_data])}")
        missing_videos += [video_name + ".mp4" for video_name in video_names if video_name not in combined_data]
    
    import numpy as np
    label_name_nice = camera_movement_mapping[label_name]
    scores = []
    # raw_scores = {
    #     "delta_x": [],
    #     "delta_y": [],
    #     "delta_z": [],
    #     "delta_yaw": [],
    #     "delta_pitch": [],
    #     "delta_roll": [],
    #     "delta_zoom": [],
    # }
    # video_idx = -1
    for item in video_items:
        # video_idx += 1
        # if video_idx == 20 and label_name_nice == "Move Down":
        #     import pdb; pdb.set_trace()
        if item is None:
            scores.append(np.nan)
            # raw_scores["delta_x"].append(0)
            # raw_scores["delta_y"].append(0)
            # raw_scores["delta_z"].append(0)
            # raw_scores["delta_yaw"].append(0)
            # raw_scores["delta_pitch"].append(0)
            # raw_scores["delta_roll"].append(0)
            # raw_scores["delta_zoom"].append(1)
            continue
        scores.append(motion_to_score[label_name_nice](item))
        # raw_scores["delta_x"].append(item["delta_x"])
        # raw_scores["delta_y"].append(item["delta_y"])
        # # check if isnan
        # # if np.isnan(item["delta_y"]):
        # #     import pdb; pdb.set_trace()
        # raw_scores["delta_z"].append(item["delta_z"])
        # raw_scores["delta_yaw"].append(item["delta_yaw"])
        # raw_scores["delta_pitch"].append(item["delta_pitch"])
        # raw_scores["delta_roll"].append(item["delta_roll"])
        # raw_scores["delta_zoom"].append(item["delta_zoom"])
        
    scores = np.array(scores)
    # if label_name_nice == "Static":
    #     # first normalize each dimension to [-1, 1]
    #     for key in raw_scores:
    #         raw_scores[key] = np.array(raw_scores[key])
    #         print(f"Max {key}: {np.max(raw_scores[key])}")
    #         print(f"Min {key}: {np.min(raw_scores[key])}")
    #         print(f"Mean {key}: {np.mean(raw_scores[key])}")
    #         if np.max(raw_scores[key]) - np.min(raw_scores[key]) == 0:
    #             raw_scores[key] = np.zeros_like(raw_scores[key])
    #         else:
    #             raw_scores[key] = 2 * (raw_scores[key] - np.min(raw_scores[key])) / (np.max(raw_scores[key]) - np.min(raw_scores[key])) - 1
    #         print(f"After normalization, Max {key}: {np.max(raw_scores[key])}")
    #         print(f"After normalization, Min {key}: {np.min(raw_scores[key])}")
    #         print(f"After normalization, Mean {key}: {np.mean(raw_scores[key])}")
            
    #     # then take the maximum
    #     raw_scores_array = np.array(list(raw_scores.values()))
    #     scores = np.max(np.abs(raw_scores_array), axis=0)
    #     print(f"Max score: {np.max(scores)}")
    #     print(f"Min score: {np.min(scores)}")
    #     print(f"Mean score: {np.mean(scores)}")
    # elif label_name_nice == "Move Down":
    #     scores_without_nan = scores[~np.isnan(scores)]
    #     print(f"Max score: {np.max(scores_without_nan)}")
    #     print(f"Min score: {np.min(scores_without_nan)}")
    #     print(f"Mean score: {np.mean(scores_without_nan)}")
    #     scores_sorted = np.sort(scores_without_nan)
    #     import pdb; pdb.set_trace()
        # print(f"Max score: {np.max(scores)}")
        # print(f"Min score: {np.min(scores)}")
        # print(f"Mean score: {np.mean(scores)}")
        # import pdb; pdb.set_trace()

    results = dataset.evaluate_scores(
        scores,
        plot_path=LABEL_SAVE_DIR / f"{args.sfm_method}_pr_curve.jpeg",
    )
    all_labels_scores[label_name] = {
        "scores": scores,
        "results": results,
    }
    # torch.save(all_labels_scores[label_name], LABEL_SAVE_PATH)


# print by nice names:
print("Label Name".ljust(50), "AP".rjust(10), "ROC AUC".rjust(10), "F1".rjust(10), "Threshold".rjust(12))
print("-" * 100)
for label_name in all_labels:
    label_name_nice = camera_movement_mapping[label_name]
    ap = all_labels_scores[label_name]["results"]["ap"]
    roc_auc = all_labels_scores[label_name]["results"]["roc_auc"]
    optimal_f1 = all_labels_scores[label_name]["results"]["optimal_f1"]
    optimal_threshold = all_labels_scores[label_name]["results"]["optimal_threshold"]

    print(
        f"{label_name_nice:50s} {ap:>10.4f} {roc_auc:>10.4f} {optimal_f1:>10.4f} {optimal_threshold:>12.4f}"
    )

missing_videos = list(set(missing_videos))
with open("missing_videos.txt", "w") as f:
    f.write("\n".join(missing_videos))
print(f"Missing videos saved to 'missing_videos.txt'")
# Sort by best AP
# sorted_labels = sorted(all_labels_scores, key=lambda x: all_labels_scores[x]["results"]["ap"], reverse=True)
# print(f"Using Score Model: {args.score_model}")
# header = f"{args.score_model:50s} {'AP':>10} {'ROC AUC':>10} {'F1':>10} {'Threshold':>12}"
# separator = "-" * len(header)

# print(header)
# print(separator)

# for label_name, scores in all_labels_scores.items():
#     ap = scores["results"]["ap"]
#     roc_auc = scores["results"]["roc_auc"]
#     optimal_f1 = scores["results"]["optimal_f1"]
#     optimal_threshold = scores["results"]["optimal_threshold"]

#     print(
#         f"{label_name.rsplit('.')[-1]:50s} {ap:>10.4f} {roc_auc:>10.4f} {optimal_f1:>10.4f} {optimal_threshold:>12.4f}"
#     )
