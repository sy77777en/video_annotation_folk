import streamlit as st
import difflib
import os
import re
from feedback_app import (
    load_video_data, get_video_id, load_json, 
    get_filename, load_data, FOLDER, FEEDBACK_FILE_POSTFIX, PREV_FEEDBACK_FILE_POSTFIX,
    load_config, extract_frames, file_check, config_names_to_short_names, ANNOTATORS
)
from feedback_diff_app import (
    get_video_status, split_into_words, highlight_differences, 
    get_video_format_func, login_page, format_timestamp, main as feedback_diff_main
)
from lighting_app import parse_args, caption_programs
from datetime import datetime
import argparse
from caption_policy.vanilla_program import (
    RawColorPolicy,
    RawLightingSetupPolicy,
    RawLightingEffectsPolicy,
)

def main(args):
    # Call the main function from feedback_diff_app.py with our args
    feedback_diff_main(args)

if __name__ == "__main__":
    args = parse_args()
    main(args) 