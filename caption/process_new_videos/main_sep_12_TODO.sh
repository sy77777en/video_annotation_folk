#!/bin/bash

# Process new overlapping videos from the September dataset
python caption/process_new_videos.py \
    --new-dir "caption/video_urls/20250911_setup_and_motion" \
    --valid-filename "overlap_all_XXX.json" \
    --invalid-filename "caption/video_urls/20250911_setup_and_motion/overlap_invalid.json" \
    --batch-files \
        "caption/video_urls/20250227_0507ground_and_setup/overlap_0_to_94.json" \
        "caption/video_urls/20250227_0507ground_and_setup/overlap_94_to_188.json" \
        "caption/video_urls/20250227_0507ground_and_setup/overlap_188_to_282.json" \
        "caption/video_urls/20250227_0507ground_and_setup/overlap_282_to_376.json" \
        "caption/video_urls/20250227_0507ground_and_setup/overlap_376_to_470.json" \
        "caption/video_urls/20250227_0507ground_and_setup/overlap_470_to_564.json" \
        "caption/video_urls/20250227_0507ground_and_setup/overlap_564_to_658.json" \
        "caption/video_urls/20250227_0507ground_and_setup/overlap_658_to_752.json" \
        "caption/video_urls/20250227_0507ground_and_setup/overlap_752_to_846.json" \
        "caption/video_urls/20250227_0507ground_and_setup/overlap_846_to_940.json" \
        "caption/video_urls/20250406_setup_and_motion/overlap_940_to_950.json" \
        "caption/video_urls/20250406_setup_and_motion/overlap_950_to_960.json" \
        "caption/video_urls/20250406_setup_and_motion/overlap_960_to_970.json" \
        "caption/video_urls/20250406_setup_and_motion/overlap_970_to_980.json" \
        "caption/video_urls/20250406_setup_and_motion/overlap_980_to_990.json" \
        "caption/video_urls/20250406_setup_and_motion/overlap_990_to_1000.json" \
        "caption/video_urls/20250406_setup_and_motion/overlap_1000_to_1010.json" \
        "caption/video_urls/20250406_setup_and_motion/overlap_1010_to_1020.json" \
    --batch-size 10 \
    --naming-mode overlap