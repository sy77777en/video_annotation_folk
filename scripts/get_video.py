import os
import sys
sys.path.append("/Users/censiyuan/Desktop/2025CVPR_VideoAnnotation/main_branch/video_annotation")
import json
import argparse
from process_json import json_to_video_data
from collections import defaultdict


video_question_dict = {
    "Has Forward Movement (Relative to Ground, Bird’s/Worm’s Eye Views Included)": "has_forward_wrt_ground_birds_worms_included",
    "Has Forward Movement (Relative to Ground, Bird’s/Worm’s Eye Views Not Included)": "has_forward_wrt_ground",
    "Only Forward Movement (Relative to Ground, Bird’s/Worm’s Eye Views Included)": "only_forward_wrt_ground_birds_worms_included",
    "Only Forward Movement (Relative to Ground, Bird’s/Worm’s Eye Views Not Included)": "only_forward_wrt_ground",
    "Has Backward Movement (Relative to Ground, Bird's/Worm's Eye Views Included)": "has_backward_wrt_ground_birds_worms_included",
    "Has Backward Movement (Relative to Ground, Bird's/Worm's Eye Views Not Included)": "has_backward_wrt_ground",
    "Only Backward Movement (Relative to Ground, Bird's/Worm's Eye Views Included)": "only_backward_wrt_ground_birds_worms_included",
    "Only Backward Movement (Relative to Ground, Bird's/Worm's Eye Views Not Included)": "only_backward_wrt_ground",
    "Has Downward Movement (Relative to Ground, Bird's/Worm's Eye Views Included)": "has_downward_wrt_ground_birds_worms_included",
    "Has Downward Movement (Relative to Ground, Bird's/Worm's Eye Views Not Included)": "has_downward_wrt_ground",
    "Only Downward Movement (Relative to Ground, Bird's/Worm's Eye Views Included)": "only_downward_wrt_ground_birds_worms_included",
    "Only Downward Movement (Relative to Ground, Bird's/Worm's Eye Views Not Included)": "only_downward_wrt_ground",
    "Has Upward Movement (Relative to Ground, Bird's/Worm's Eye Views Included)": "has_upward_wrt_ground_birds_worms_included",
    "Has Upward Movement (Relative to Ground, Bird's/Worm's Eye Views Not Included)": "has_upward_wrt_ground",
    "Only Upward Movement (Relative to Ground, Bird's/Worm's Eye Views Included)": "only_upward_wrt_ground_birds_worms_included",
    "Only Upward Movement (Relative to Ground, Bird's/Worm's Eye Views Not Included)": "only_upward_wrt_ground",
    "Has Leftward Movement": "has_leftward",
    "Only Leftward Movement": "only_leftward",
    "Has Rightward Movement": "has_rightward",
    "Only Rightward Movement": "only_rightward",
    "Has Pan Left Movement": "has_pan_left",
    "Only Pan Left Movement": "only_pan_left",
    "Has Pan Right Movement": "has_pan_right",
    "Only Pan Right Movement": "only_pan_right",
    "Has Tilt Down Movement": "has_tilt_down",
    "Only Tilt Down Movement": "only_tilt_down",
    "Has Tilt Up Movement": "has_tilt_up",
    "Only Tilt Up Movement": "only_tilt_up",
    "Has Zoom In (Relative to Camera)": "has_zoom_in",
    "Only Zoom In (Relative to Camera)": "only_zoom_in",
    "Has Zoom Out (Relative to Camera)": "has_zoom_out",
    "Only Zoom Out (Relative to Camera)": "only_zoom_out"
}


def get_video(json_file):
    res = defaultdict(lambda: defaultdict(list))

    # if question in video_question_dict:
    #     labels = video_question_dict[question]
    # else:
    #     print("Error: you should choose a valid question")
    #     return res
    video_data_dict = json_to_video_data(json_file)

    for question, labels in video_question_dict.items():
        if labels == "has_forward_wrt_ground_birds_worms_included":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.forward is True
                neg = video_data.cam_motion.forward is False
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        # elif labels == "has_forward_wrt_ground":
        elif labels == "only_forward_wrt_ground_birds_worms_included":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.forward is True and video_data.cam_motion.check_if_no_motion(exclude=['forward'])
                neg = video_data.cam_motion.forward is False or not video_data.cam_motion.check_if_no_motion(exclude=['forward'])
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        # elif labels == "only_forward_wrt_ground":
        #     pos =
        #     neg =
        elif labels == "has_backward_wrt_ground_birds_worms_included":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.backward is True
                neg = video_data.cam_motion.backward is False
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        # elif labels == "has_backward_wrt_ground":
        #     pos =
        #     neg =
        elif labels == "only_backward_wrt_ground_birds_worms_included":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.backward is True and video_data.cam_motion.check_if_no_motion(exclude=['backward'])
                neg = video_data.cam_motion.backward is False or not video_data.cam_motion.check_if_no_motion(exclude=['backward'])
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        # elif labels == "only_backward_wrt_ground":
        #     pos =
        #     neg =
        elif labels == "has_downward_wrt_ground_birds_worms_included":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.down is True
                neg = video_data.cam_motion.down is False
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        # elif labels == "has_downward_wrt_ground":
        #     pos =
        #     neg =
        elif labels == "only_downward_wrt_ground_birds_worms_included":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.down is True and video_data.cam_motion.check_if_no_motion(exclude=['down'])
                neg = video_data.cam_motion.down is False or not video_data.cam_motion.check_if_no_motion(exclude=['down'])
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        # elif labels == "only_downward_wrt_ground":
        #     pos =
        #     neg =
        elif labels == "has_upward_wrt_ground_birds_worms_included":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.up is True
                neg = video_data.cam_motion.up is False
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        # elif labels == "has_upward_wrt_ground":
        #     pos =
        #     neg =
        elif labels == "only_upward_wrt_ground_birds_worms_included":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.up is True and video_data.cam_motion.check_if_no_motion(exclude=['up'])
                neg = video_data.cam_motion.up is False or not video_data.cam_motion.check_if_no_motion(exclude=['up'])
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        # elif labels == "only_upward_wrt_ground":
        #     pos =
        #     neg =
        elif labels == "has_leftward":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.left is True
                neg = video_data.cam_motion.left is False
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "only_leftward":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.left is True and video_data.cam_motion.check_if_no_motion(exclude=['left'])
                neg = video_data.cam_motion.left is True and video_data.cam_motion.check_if_no_motion(exclude=['left'])
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "has_rightward":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.right is True
                neg = video_data.cam_motion.right is False
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "only_rightward":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.right is True and video_data.cam_motion.check_if_no_motion(exclude=['right'])
                neg = video_data.cam_motion.right is False or not video_data.cam_motion.check_if_no_motion(exclude=['right'])
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "has_pan_left":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.pan_left is True
                neg = video_data.cam_motion.pan_left is False
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "only_pan_left":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.pan_left is True and video_data.cam_motion.check_if_no_motion(exclude=['pan_left'])
                neg = video_data.cam_motion.pan_left is False or not video_data.cam_motion.check_if_no_motion(exclude=['pan_left'])
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "has_pan_right":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.pan_right is True
                neg = video_data.cam_motion.pan_right is False
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "only_pan_right":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.pan_right is True and video_data.cam_motion.check_if_no_motion(exclude=['pan_right'])
                neg = video_data.cam_motion.pan_right is False or not video_data.cam_motion.check_if_no_motion(exclude=['pan_right'])
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "has_tilt_down":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.tilt_down is True
                neg = video_data.cam_motion.tilt_down is False
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "only_tilt_down":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.tilt_down is True and video_data.cam_motion.check_if_no_motion(exclude=['tilt_down'])
                neg = video_data.cam_motion.tilt_down is False and not video_data.cam_motion.check_if_no_motion(exclude=['tilt_down'])
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "has_tilt_up":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.tilt_up is True
                neg = video_data.cam_motion.tilt_up is False
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "only_tilt_up":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.tilt_up is True and video_data.cam_motion.check_if_no_motion(exclude=['tilt_up'])
                neg = video_data.cam_motion.tilt_up is False or not video_data.cam_motion.check_if_no_motion(exclude=['tilt_up'])
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "has_zoom_in":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.zoom_in is True
                neg = video_data.cam_motion.zoom_in is False
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "only_zoom_in":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.zoom_in is True and video_data.cam_motion.check_if_no_motion(exclude=['zoom_in'])
                neg = video_data.cam_motion.zoom_in is False or not video_data.cam_motion.check_if_no_motion(exclude=['zoom_in'])
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "has_zoom_out":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.zoom_out is True
                neg = video_data.cam_motion.zoom_out is False
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
        elif labels == "only_zoom_out":
            for video_name, video_data in video_data_dict.items():
                pos = video_data.cam_motion.zoom_out is True and video_data.cam_motion.check_if_no_motion(exclude=['zoom_out'])
                neg = video_data.cam_motion.zoom_out is False and not video_data.cam_motion.check_if_no_motion(exclude=['zoom_out'])
                if pos:
                    res[labels]["pos"].append(video_name)
                if neg:
                    res[labels]["neg"].append(video_name)
    return res


def main():
    parser = argparse.ArgumentParser(description="Process video data from a JSON file.")
    parser.add_argument("--json_path", type=str,
                        default="video_data/20250219_0338/videos.json",
                        help="Path to the JSON file containing video data.")
    args = parser.parse_args()
    labels_dict = get_video(args.json_path)
    for key, values in labels_dict.items():
        print(key)
        print(len(values['pos']), len(values['neg']))

if __name__ == "__main__":
    main()
