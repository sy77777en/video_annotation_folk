#!/bin/bash

# Process new non-overlapping videos from the April dataset
python caption/process_new_videos.py \
    --existing-dir "caption/video_urls/20250227_0507ground_and_setup" \
    --new-dir "caption/video_urls/20250406_setup_and_motion" \
    --valid-filename "nonoverlap_all_1268.json" \
    --batch-size 10 \
    --batch-files \
    --naming-mode nonoverlap 