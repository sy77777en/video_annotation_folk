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
    
    # Load videos from specified batch files if provided
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
    
    # Get the last batch number or index from the filenames based on naming mode
    last_batch_or_index = 0
    
    for batch_file in args.batch_files:
        try:
            if args.naming_mode == "batch":
                # For batchX.json format
                batch_num = int(os.path.basename(batch_file).replace("batch", "").replace(".json", ""))
                last_batch_or_index = max(last_batch_or_index, batch_num)
            else:
                # For overlap_X_to_Y.json format
                # Count URLs in this file
                full_path = os.path.join(args.existing_dir, batch_file)
                urls_in_file = len(load_json_file(full_path))
                total_urls += urls_in_file
                
                # Extract the end number from overlap_X_to_Y.json for verification
                end_num = int(os.path.basename(batch_file).split("_to_")[1].replace(".json", ""))
                start_num = int(os.path.basename(batch_file).split("_to_")[0].replace("overlap_", ""))
                
                # Verify that the file contains the expected number of URLs
                expected_urls = end_num - start_num
                if urls_in_file != expected_urls:
                    print(f"Warning: File {batch_file} contains {urls_in_file} URLs but name suggests {expected_urls}")
                
                last_batch_or_index = max(last_batch_or_index, end_num)
        except (ValueError, IndexError) as e:
            print(f"Error processing file {batch_file}: {e}")
            continue
    
    return existing_videos, invalid_videos, last_batch_or_index

def process_new_videos(args):
    # Load existing videos
    existing_videos, existing_invalid, last_batch_or_index = get_existing_videos(args)
    
    # Load new videos
    new_video = load_json_file(os.path.join(args.new_dir, args.valid_filename))
    
    # Load and process invalid videos only if filename provided
    new_invalid_videos = []
    if args.invalid_filename:
        new_invalid = load_json_file(os.path.join(args.new_dir, args.invalid_filename))
        new_invalid_videos = [v for v in new_invalid if v not in existing_invalid]
        print(f"Found {len(new_invalid_videos)} new invalid videos")
    
    # Find new videos that aren't in existing batches
    new_valid_videos = [v for v in new_video if v not in existing_videos]
    print(f"\nFound {len(new_valid_videos)} new valid videos")
    
    # Create new batches
    for i in range(0, len(new_valid_videos), args.batch_size):
        batch = new_valid_videos[i:i + args.batch_size]
        
        # Use appropriate naming convention based on mode
        if args.naming_mode == "batch":
            last_batch_or_index += 1
            batch_file = os.path.join(args.new_dir, f"batch{last_batch_or_index}.json")
        elif args.naming_mode == "overlap":
            # For overlap mode, calculate start and end indices continuing from last index
            start_idx = last_batch_or_index
            end_idx = start_idx + len(batch)
            last_batch_or_index = end_idx
            batch_file = os.path.join(args.new_dir, f"overlap_{start_idx}_to_{end_idx}.json")
        elif args.naming_mode == "nonoverlap":  # nonoverlap mode
            # For nonoverlap mode, calculate start and end indices continuing from last index
            start_idx = last_batch_or_index
            end_idx = start_idx + len(batch)
            last_batch_or_index = end_idx
            batch_file = os.path.join(args.new_dir, f"{start_idx}_to_{end_idx}.json")
        
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
    parser.add_argument("--existing-dir", type=str, default="caption/video_urls/20250227_0507ground_and_setup",
                        help="Directory containing existing batch files")
    parser.add_argument("--new-dir", type=str, default="caption/video_urls/20250406_setup_and_motion",
                        help="Directory for new batch files")
    
    # File names
    parser.add_argument("--valid-filename", type=str, default="overlap_all.json",
                        help="Filename for valid videos")
    parser.add_argument("--invalid-filename", type=str, #default=None,
                        default="invalid_videos.json",
                        help="Optional filename for invalid videos")
    
    #     # Batch files
    # parser.add_argument("--batch-files", nargs="+", type=str,
    #                     default=[
    #                         "batch1.json",
    #                         "batch2.json",
    #                         "batch3.json",
    #                         "batch4.json",
    #                         "batch5.json",
    #                         "batch6.json",
    #                         "batch7.json",
    #                         "batch8.json",
    #                         "batch9.json",
    #                         "batch10.json"
    #                     ],
    #                     help="List of batch files to process (relative to existing-dir)")
    # Batch files - make it optional
    parser.add_argument("--batch-files", nargs="*", type=str,
                        default=[],
                        help="Optional list of batch files to process (relative to existing-dir)")
    
    # Batch configuration
    parser.add_argument("--batch-size", type=int, default=10,
                        help="Number of videos per batch")
    
    # Naming mode
    parser.add_argument("--naming-mode", type=str, choices=["batch", "overlap", "nonoverlap"], default="overlap",
                        help="Naming convention for batch files: 'batch' for batchX.json, 'overlap' for overlap_X_to_Y.json, or 'nonoverlap' for nonoverlap_X_to_Y.json")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    process_new_videos(args) 