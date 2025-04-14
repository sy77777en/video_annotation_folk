import argparse
from streamlit_feedback import streamlit_feedback
from caption_policy.vanilla_program import (
    VanillaSubjectPolicy,
    VanillaScenePolicy,
    VanillaColorPolicy,
    VanillaLightingSetupPolicy,
    VanillaLightingEffectsPolicy,
    RawColorPolicy,
    RawLightingSetupPolicy,
    RawLightingEffectsPolicy,
)

# Argument parsing
def parse_args():
    parser = argparse.ArgumentParser(description="Video Caption Feedback System for Lighting")
    parser.add_argument("--configs", type=str, default="lighting_configs.json", help="Path to the JSON config file")
    # parser.add_argument("--video_urls_file", type=str, default="test_urls_all.json", help="Path to the test URLs file")
    parser.add_argument(
        "--video_urls_files",
        nargs="+",
        type=str,
        default=[
            # "video_urls/lighting_120_new/all_labels.json",
            # "video_urls/lighting_120_new/lighting_only.json",
            "video_urls/lighting_120_new/batch1.json",
            "video_urls/lighting_120_new/batch2.json",
            "video_urls/lighting_120_new/batch3.json",
            "video_urls/lighting_120_new/batch4.json",
            "video_urls/lighting_120_new/batch5.json",
            "video_urls/lighting_120_new/batch6.json",
            "video_urls/lighting_120_new/batch7.json",
            "video_urls/lighting_120_new/batch8.json",
            "video_urls/lighting_120_new/batch9.json",
            "video_urls/lighting_120_new/batch10.json",
            "video_urls/lighting_250_new/batch11.json",
            "video_urls/lighting_250_new/batch12.json",
            "video_urls/lighting_250_new/batch13.json",
            "video_urls/lighting_250_new/batch14.json",
            "video_urls/lighting_250_new/batch15.json",
            "video_urls/lighting_250_new/batch16.json",
            "video_urls/lighting_250_new/batch17.json",
            "video_urls/lighting_250_new/batch18.json",
            "video_urls/lighting_250_new/batch19.json",
            "video_urls/lighting_250_new/batch20.json",
            "video_urls/lighting_120_new/invalid_videos.json",
            "video_urls/lighting_250_new/invalid_videos.json",
        ],
        help="List of paths to test URLs files",
    )
    parser.add_argument("--output", type=str, default="output_captions", help="Path to the output directory")
    parser.add_argument("--feedback_prompt", type=str, default="prompts/feedback_prompt.txt", help="Path to the feedback prompt file")
    parser.add_argument("--caption_prompt", type=str, default="prompts/caption_prompt.txt", help="Path to the caption prompt file")
    # parser.add_argument("--video_data", type=str, default="video_data/20250224_0130/videos.json", help="Path to the video data file")
    # parser.add_argument("--video_data", type=str, default="video_data/20250324_1616_all_labels/videos.json", help="Path to the video data file")
    # parser.add_argument("--video_data", type=str, default="video_data/20250328_1455_lighting_120/videos.json", help="Path to the video data file") # Before April 14
    parser.add_argument("--video_data", type=str, default="video_data/20250406lighting_only/videos.json", help="Path to the video data file")
    # parser.add_argument("--label_collections", nargs="+", type=str, default=["cam_motion", "cam_setup", "lighting_setup"], help="List of label collections to load from the video data")
    parser.add_argument("--label_collections", nargs="+", type=str, default=["lighting_setup"], help="List of label collections to load from the video data")
    return parser.parse_args()

# Load configuration
args = parse_args()

caption_programs = {
    # "subject_description": VanillaSubjectPolicy(),
    # "scene_composition_dynamics": VanillaScenePolicy(),
    # "color_composition_dynamics": VanillaColorPolicy(),
    # "lighting_setup_dynamics": VanillaLightingSetupPolicy(),
    # "lighting_effects_dynamics": VanillaLightingEffectsPolicy(),
    "raw_color_composition_dynamics": RawColorPolicy(),
    "raw_lighting_setup_dynamics": RawLightingSetupPolicy(),
    "raw_lighting_effects_dynamics": RawLightingEffectsPolicy(),
}


from feedback_app import main

if __name__ == "__main__":
    main(args, caption_programs)
