#!/bin/bash

# Process new videos from the April dataset
python caption/process_new_videos.py \
    --new-dir "caption/video_urls/lighting_250_new" \
    --valid-filename "lighting_only.json" \
    --invalid-filename "caption/video_urls/lighting_120_new/invalid_videos.json" \
    --batch-files \
        "caption/video_urls/lighting_120_new/batch1.json" \
        "caption/video_urls/lighting_120_new/batch2.json" \
        "caption/video_urls/lighting_120_new/batch3.json" \
        "caption/video_urls/lighting_120_new/batch4.json" \
        "caption/video_urls/lighting_120_new/batch5.json" \
        "caption/video_urls/lighting_120_new/batch6.json" \
        "caption/video_urls/lighting_120_new/batch7.json" \
        "caption/video_urls/lighting_120_new/batch8.json" \
        "caption/video_urls/lighting_120_new/batch9.json" \
        "caption/video_urls/lighting_120_new/batch10.json" \
    --batch-size 10