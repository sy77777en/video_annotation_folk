import json
import os
import argparse
from pathlib import Path

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File {file_path} not found")
        return []

def save_json_file(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def get_existing_videos(args):
    # Load all existing batch files
    existing_videos = set()
    
    # Load videos from specified batch files
    if args.batch_files:
        print(f"Loading {len(args.batch_files)} batch files")
        for batch_file in args.batch_files:
            full_path = os.path.join(args.existing_dir, batch_file)
            videos = load_json_file(full_path)
            existing_videos.update(videos)
    
    # Load existing invalid videos if filename provided
    invalid_videos = set()
    if args.invalid_filename:
        invalid_file = os.path.join(args.existing_dir, args.invalid_filename)
        invalid_videos = set(load_json_file(invalid_file))
    
    # Get the last batch number from the filenames
    last_batch = 0
    for batch_file in args.batch_files:
        try:
            batch_num = int(os.path.basename(batch_file).replace("batch", "").replace(".json", ""))
            last_batch = max(last_batch, batch_num)
        except ValueError:
            continue
    
    return existing_videos, invalid_videos, last_batch

def process_new_videos(args):
    # Load existing videos
    existing_videos, existing_invalid, last_batch_num = get_existing_videos(args)
    
    # Load new videos
    new_lighting = load_json_file(os.path.join(args.new_dir, args.valid_filename))
    
    # Load and process invalid videos only if filename provided
    new_invalid_videos = []
    if args.invalid_filename:
        new_invalid = load_json_file(os.path.join(args.new_dir, args.invalid_filename))
        new_invalid_videos = [v for v in new_invalid if v not in existing_invalid]
        print(f"Found {len(new_invalid_videos)} new invalid videos")
    
    # Find new videos that aren't in existing batches
    new_valid_videos = [v for v in new_lighting if v not in existing_videos]
    print(f"\nFound {len(new_valid_videos)} new valid videos")
    
    # Create new batches
    current_batch = last_batch_num
    for i in range(0, len(new_valid_videos), args.batch_size):
        current_batch += 1
        batch = new_valid_videos[i:i + args.batch_size]
        batch_file = os.path.join(args.new_dir, f"batch{current_batch}.json")
        save_json_file(batch, batch_file)
        print(f"Created {batch_file} with {len(batch)} videos")
    
    # Save new invalid videos if filename provided
    if args.invalid_filename and new_invalid_videos:
        invalid_file = os.path.join(args.new_dir, args.invalid_filename)
        save_json_file(new_invalid_videos, invalid_file)
        print(f"Added {len(new_invalid_videos)} new invalid videos to {invalid_file}")

def parse_args():
    parser = argparse.ArgumentParser(description="Process and distribute videos into batches")
    
    # Directory structure
    parser.add_argument("--existing-dir", type=str, default="caption/video_urls/lighting_120_new",
                        help="Directory containing existing batch files")
    parser.add_argument("--new-dir", type=str, default="caption/video_urls/lighting_250_new",
                        help="Directory for new batch files")
    
    # File names
    parser.add_argument("--valid-filename", type=str, default="lighting_only.json",
                        help="Filename for valid videos")
    parser.add_argument("--invalid-filename", type=str, #default=None,
                        default="invalid_videos.json",
                        help="Optional filename for invalid videos")
    
    # Batch files
    parser.add_argument("--batch-files", nargs="+", type=str,
                        default=[
                            "batch1.json",
                            "batch2.json",
                            "batch3.json",
                            "batch4.json",
                            "batch5.json",
                            "batch6.json",
                            "batch7.json",
                            "batch8.json",
                            "batch9.json",
                            "batch10.json"
                        ],
                        help="List of batch files to process (relative to existing-dir)")
    
    # Batch configuration
    parser.add_argument("--batch-size", type=int, default=10,
                        help="Number of videos per batch")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    process_new_videos(args) 