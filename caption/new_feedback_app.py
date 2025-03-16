import argparse
from streamlit_feedback import streamlit_feedback
from caption_policy.vanilla_program import (
    VanillaSubjectPolicy,
    VanillaScenePolicy,
    VanillaColorPolicy,
    VanillaLightingSetupPolicy,
    VanillaLightingEffectsPolicy,
    # RawColorPolicy,
    # RawLightingSetupPolicy,
    # RawLightingEffectsPolicy,
)

# Argument parsing
def parse_args():
    parser = argparse.ArgumentParser(description="Video Caption Feedback System for Lighting")
    parser.add_argument("--configs", type=str, default="lighting_configs.json", help="Path to the JSON config file")
    # parser.add_argument("--video_urls_file", type=str, default="test_urls_all.json", help="Path to the test URLs file")
    parser.add_argument("--video_urls_file", type=str, default="test_urls_selected.json", help="Path to the test URLs file")
    parser.add_argument("--output", type=str, default="output_captions", help="Path to the output directory")
    parser.add_argument("--feedback_prompt", type=str, default="prompts/feedback_prompt.txt", help="Path to the feedback prompt file")
    parser.add_argument("--caption_prompt", type=str, default="prompts/caption_prompt.txt", help="Path to the caption prompt file")
    # parser.add_argument("--video_data", type=str, default="video_data/20250224_0130/videos.json", help="Path to the video data file")
    parser.add_argument("--video_data", type=str, default="video_data/20250227_0507ground_and_setup/videos.json", help="Path to the video data file")
    parser.add_argument("--label_collections", nargs="+", type=str, default=["cam_motion", "cam_setup"], help="List of label collections to load from the video data")
    return parser.parse_args()

# Load configuration
args = parse_args()

caption_programs = {
    "subject_description": VanillaSubjectPolicy(),
    "scene_composition_dynamics": VanillaScenePolicy(),
    "color_composition_dynamics": VanillaColorPolicy(),
    "lighting_setup_dynamics": VanillaLightingSetupPolicy(),
    "lighting_effects_dynamics": VanillaLightingEffectsPolicy(),
    # "raw_color_composition_dynamics": RawColorPolicy(),
    # "raw_lighting_setup_dynamics": RawLightingSetupPolicy(),
    # "raw_lighting_effects_dynamics": RawLightingEffectsPolicy(),
}


from feedback_app import main

if __name__ == "__main__":
    main(args, caption_programs)
