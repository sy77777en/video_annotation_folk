import argparse

# Argument parsing
def parse_args():
    parser = argparse.ArgumentParser(description="Video Caption Feedback System for Lighting")
    parser.add_argument("--configs", type=str, default="all_configs.json", help="Path to the JSON config file")
    # parser.add_argument("--video_urls_file", type=str, default="test_urls_all.json", help="Path to the test URLs file")
    parser.add_argument(
        "--video_urls_files",
        nargs="+",
        type=str,
        default=[
            "video_urls/new_annotator_exam/exam.json",
        ],
        help="List of paths to test URLs files",
    )
    parser.add_argument("--output", type=str, default="output_new_annotator_hewei", help="Path to the output directory")
    # parser.add_argument("--output", type=str, default="output_new_annotator_sunny", help="Path to the output directory")
    parser.add_argument("--feedback_prompt", type=str, default="prompts/feedback_prompt.txt", help="Path to the feedback prompt file")
    parser.add_argument("--caption_prompt", type=str, default="prompts/caption_prompt.txt", help="Path to the caption prompt file")
    parser.add_argument("--video_data", type=str, default="video_data/20250227_0507ground_and_setup/videos.json", help="Path to the video data file")
    # parser.add_argument("--video_data", type=str, default="video_data/20250324_1616_all_labels/videos.json", help="Path to the video data file")
    parser.add_argument("--label_collections", nargs="+", type=str, default=["cam_motion", "cam_setup"], help="List of label collections to load from the video data")
    return parser.parse_args()

# Load configuration
args = parse_args()


from feedback_app import main, caption_programs

if __name__ == "__main__":
    main(args, caption_programs)
