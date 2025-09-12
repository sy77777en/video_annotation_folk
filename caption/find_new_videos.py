#!/usr/bin/env python3

import json
import sys
import os
from pathlib import Path

def load_json_file(file_path):
    """Load JSON file and return list of URLs"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File {file_path} not found")
        return []

def load_main_config():
    """Load the main configuration dynamically"""
    try:
        # Add the project root to Python path
        script_dir = Path(__file__).parent
        project_root = script_dir.parent if script_dir.name == 'caption' else script_dir
        sys.path.insert(0, str(project_root))
        
        # Import the config
        from caption.config.main_config import DEFAULT_VIDEO_URLS_FILES
        
        print(f"Loaded {len(DEFAULT_VIDEO_URLS_FILES)} file paths from main_config.py")
        return DEFAULT_VIDEO_URLS_FILES
        
    except ImportError as e:
        print(f"Error importing main_config.py: {e}")
        print("Make sure you're running this script from the project root or caption/ directory")
        sys.exit(1)

def get_all_existing_videos():
    """Get all videos from both overlap and nonoverlap sets"""
    
    # Load file paths from main_config.py
    video_url_files = load_main_config()
    
    all_existing = set()
    
    # Load all videos from the config files
    print("Loading existing videos from main_config.py...")
    for file_path in video_url_files:
        # Skip invalid files to avoid errors
        if 'invalid' in file_path:
            print(f"  Skipping invalid file: {file_path}")
            continue
            
        # Add caption/ prefix if not present
        if not file_path.startswith('caption/'):
            full_path = f"caption/{file_path}"
        else:
            full_path = file_path
            
        videos = load_json_file(full_path)
        all_existing.update(videos)
        print(f"  Loaded {len(videos)} videos from {file_path}")
    
    print(f"Total existing videos: {len(all_existing)}")
    return all_existing

def find_new_videos(new_videos_file):
    """Find videos that are truly new (not in overlap or nonoverlap sets)"""
    
    # Get all existing videos
    all_existing = get_all_existing_videos()
    
    # Load new videos from September dataset
    print(f"\nLoading new videos from {new_videos_file}...")
    
    # Try both overlap and nonoverlap files from September dataset
    new_overlap_file = f"caption/video_urls/20250911_setup_and_motion/overlap_all_*.json"
    new_nonoverlap_file = f"caption/video_urls/20250911_setup_and_motion/nonoverlap_all_*.json"
    
    # Load the specific file provided
    new_videos = load_json_file(new_videos_file)
    print(f"Loaded {len(new_videos)} potential new videos")
    
    # Find truly new videos
    truly_new = [video for video in new_videos if video not in all_existing]
    
    print(f"\nFound {len(truly_new)} truly new videos:")
    for i, video in enumerate(truly_new, 1):
        print(f"{i:3d}. {video}")
    
    return truly_new

def main():
    if len(sys.argv) != 2:
        print("Usage: python find_new_videos.py <path_to_new_videos_json>")
        print("Example: python find_new_videos.py caption/video_urls/20250911_setup_and_motion/overlap_all_XXX.json")
        sys.exit(1)
    
    new_videos_file = sys.argv[1]
    truly_new = find_new_videos(new_videos_file)
    
    # Print first 7 for your immediate need
    if len(truly_new) >= 7:
        print(f"\nFirst 7 new videos for padding to 1190:")
        for i, video in enumerate(truly_new[:7], 1):
            print(f"{i}. {video}")
        
        # Save the first 7 to a file for easy copy-paste
        with open('first_7_new_videos.json', 'w') as f:
            json.dump(truly_new[:7], f, indent=2)
        print(f"\nSaved first 7 videos to: first_7_new_videos.json")
    else:
        print(f"\nOnly found {len(truly_new)} new videos, need at least 7.")

if __name__ == "__main__":
    main()