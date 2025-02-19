from video_data import VideoData, CameraMotionData, CameraSetupData
import json
import argparse


def json_to_video_data(json_path):
    """Load video data from a JSON file and return a dictionary of VideoData objects."""
    with open(json_path, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    video_data_dict = {}
    for video in loaded_data:
        tmp_data = VideoData()
        tmp_data.cam_motion = video['cam_motion'] # will be converted to CameraMotionData automatically using setter()
        tmp_data.cam_setup =video['cam_setup']
        for key, value in video["workflows"].items():
            tmp_data.add_workflow(value)
        video_data_dict[tmp_data.workflows[0].video_name] = tmp_data
    return video_data_dict

def main():
    parser = argparse.ArgumentParser(description="Process video data from a JSON file.")
    parser.add_argument("--json_path", type=str,
                        default="video_data/20250218_1042/videos.json",
                        help="Path to the JSON file containing video data.")

    args = parser.parse_args()
    
    video_data_dict = json_to_video_data(args.json_path)
    print(f"Loaded {len(video_data_dict)} video data entries.")


if __name__ == '__main__':
    main()
