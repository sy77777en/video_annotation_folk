from video_data import VideoData, CameraMotionData, CameraSetupData
import json
import argparse


def to_video_data(video_list):
    video_data_dict = []
    for video in video_list:
        try:
            tmp_data = VideoData()
            tmp_data.video_name = video['video_name']
            tmp_data.video_url = video['video_url']
            tmp_data.cam_motion = CameraMotionData.create(**video['cam_motion'])
            tmp_data.cam_setup = CameraSetupData.create(**video['cam_setup'])
            tmp_data.add_workflow(video['workflows'])
            video_data_dict.append(tmp_data)
        except Exception as e:
            # print(video['video_name'])
            # print(e)
            continue
    return video_data_dict

def main():
    parser = argparse.ArgumentParser(description="Process video data from a JSON file.")
    parser.add_argument("--json_path", type=str, required=True, help="Path to the JSON file containing video data.")

    # 解析命令行参数
    args = parser.parse_args()
    with open(args.json_path, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    video_data_list = to_video_data(loaded_data)
    video_data_dict = {video.video_name: video for video in video_data_list}


if __name__ == '__main__':
    main()
