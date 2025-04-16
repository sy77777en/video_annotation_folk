#!/bin/bash

# Process new videos from the April dataset
python caption/process_new_videos.py \
    --existing-dir "caption/video_urls/20250227_0507ground_and_setup" \
    --new-dir "caption/video_urls/20250406_setup_and_motion" \
    --valid-filename "overlap_all_1062.json" \
    --batch-files \
        "overlap_0_to_94.json" \
        "overlap_94_to_188.json" \
        "overlap_188_to_282.json" \
        "overlap_282_to_376.json" \
        "overlap_376_to_470.json" \
        "overlap_470_to_564.json" \
        "overlap_564_to_658.json" \
        "overlap_658_to_752.json" \
        "overlap_752_to_846.json" \
        "overlap_846_to_940.json" \
    --batch-size 10 \
    --naming-mode overlap