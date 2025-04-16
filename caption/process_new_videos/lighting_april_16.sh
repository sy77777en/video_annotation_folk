#!/bin/bash

# Process new videos from the April dataset
python caption/process_new_videos.py \
    --new-dir "caption/video_urls/lighting_280_new" \
    --valid-filename "lighting_only.json" \
    --invalid-filename "caption/video_urls/lighting_250_new/invalid_videos.json" \
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
        "caption/video_urls/lighting_250_new/batch11.json" \
        "caption/video_urls/lighting_250_new/batch12.json" \
        "caption/video_urls/lighting_250_new/batch13.json" \
        "caption/video_urls/lighting_250_new/batch14.json" \
        "caption/video_urls/lighting_250_new/batch15.json" \
        "caption/video_urls/lighting_250_new/batch16.json" \
        "caption/video_urls/lighting_250_new/batch17.json" \
        "caption/video_urls/lighting_250_new/batch18.json" \
        "caption/video_urls/lighting_250_new/batch19.json" \
        "caption/video_urls/lighting_250_new/batch20.json" \
    --batch-size 10