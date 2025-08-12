import os
import json
import pandas as pd
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

# Import functions from the new modular structure
from caption.config import get_config
from caption.core.data_manager import DataManager

# Use functions from load_xlsx for Excel operations
from caption.load_xlsx import (
    load_captions_from_xlsx,
    get_caption_dict_by_filename,
    extract_filename,
    format_excel_file,
)


def is_task_reviewed(video_id, task, task_to_output_dir, folder, app_config, data_manager):
    """Check if a specific task has been reviewed (approved) for a video."""
    output_name = task_to_output_dir.get(task)
    if not output_name:
        return False
    
    output_dir = folder / app_config.output_dir / output_name
    # Use the correct reviewer file naming convention
    reviewer_filename = data_manager.get_filename(
        video_id, output_dir=output_dir, file_postfix="_review.json"
    )
    
    if os.path.exists(reviewer_filename):
        try:
            reviewer_data = data_manager.load_data(
                video_id, output_dir=output_dir, file_postfix="_review.json"
            )
            return reviewer_data.get("reviewer_double_check", False)
        except Exception as e:
            print(f"Error loading reviewer data for {video_id}, task {task}: {e}")
            return False
    return False
    """Convert a HuggingFace dataset resolve URL to a web viewable URL."""
    # Example input: https://huggingface.co/datasets/zhiqiulin/video_captioning/resolve/main/ce8071e2668c089f109b31ffaf1ca7a29a277bb87f6b5c4770dadf6d1fd3c5e7.1.mp4
    # Example output: https://huggingface.co/datasets/zhiqiulin/video_captioning/blob/main/ce8071e2668c089f109b31ffaf1ca7a29a277bb87f6b5c4770dadf6d1fd3c5e7.1.mp4

    # Check if it's a HuggingFace URL
    if "huggingface.co/datasets" in url:
        # Replace 'resolve' with 'blob' to make it web viewable
        return url.replace("/resolve/", "/blob/")
    return url


def get_caption_task_names(config_type: str) -> Dict[str, str]:
    """Get the appropriate caption task names based on config type."""
    if config_type == "lighting":
        return {
            "raw_color_composition_dynamics": "Color Composition",
            "raw_lighting_setup_dynamics": "Lighting Setup", 
            "raw_lighting_effects_dynamics": "Lighting Effects",
        }
    else:  # main project
        return {
            "subject_description": "Subject Description",
            "scene_composition_dynamics": "Scene Composition and Dynamics",
            "subject_motion_dynamics": "Subject Motion and Dynamics",
            "spatial_framing_dynamics": "Spatial Framing and Dynamics",
            "camera_framing_dynamics": "Camera Framing and Dynamics",
        }


def get_default_output_excel(config_type: str) -> str:
    """Get the default output Excel filename based on config type."""
    if config_type == "lighting":
        return "caption/output_caption_xlsx/lighting_caption_collection.xlsx"
    else:
        return "caption/output_caption_xlsx/main_caption_collection.xlsx"


def count_and_collect_captions(args):
    """Count completed videos and collect captions into a consolidated Excel file."""
    # Get the directory where this script is located
    folder = Path(__file__).parent
    
    # Initialize data manager
    data_manager = DataManager(folder, folder.parent)
    
    # Get config using new system
    app_config = get_config(args.config_type)
    
    # Load configs using new system
    configs = data_manager.load_config(app_config.configs_file)
    configs = [data_manager.load_config(config) for config in configs]
    config_dict = {config["name"]: config for config in configs}
    
    # Map tasks to their output directory names
    task_to_output_dir = {config["task"]: config["output_name"] for config in configs}
    
    # Get caption task names based on config type
    caption_task_names = get_caption_task_names(args.config_type)
    
    # Load Adobe Excel data
    adobe_captions_data = []
    for excel_file in args.adobe_excel_files:
        adobe_captions_data.extend(load_captions_from_xlsx(excel_file))
    
    print(f"\nLoaded {len(adobe_captions_data)} Adobe caption records from {len(args.adobe_excel_files)} files")
    
    # Debug: Show a sample of the Adobe data structure
    if adobe_captions_data:
        print("Sample Adobe data keys:", list(adobe_captions_data[0].keys()))
        if 'stock_url' in adobe_captions_data[0]:
            sample_filename = data_manager.get_video_id(adobe_captions_data[0]['stock_url']) if adobe_captions_data[0]['stock_url'] else "No URL"
            print(f"Sample filename from Adobe data: {sample_filename}")
    
    # Get first Excel file to extract its structure
    template_df = pd.read_excel(args.adobe_excel_files[0], engine='openpyxl')
    adobe_columns = list(template_df.columns)
    print(f"Adobe Excel columns: {adobe_columns}")
    
    # Define new columns for our captions
    new_columns = list(caption_task_names.values())
    
    # Add review status column
    new_columns.append("Review Status")
    
    # Create DataFrame with combined columns
    all_columns = adobe_columns + new_columns
    result_df = pd.DataFrame(columns=all_columns)
    
    # Track statistics
    total_videos = 0
    completed_videos = 0
    skipped_videos = 0
    no_adobe_count = 0
    processed_videos = 0  # Videos that were actually processed (not skipped)
    reviewed_videos = 0  # Videos that have all tasks reviewed (approved)
    task_completion = {task: 0 for task in caption_task_names.keys()}
    task_reviewed = {task: 0 for task in caption_task_names.keys()}
    
    # Use video URLs from config if not overridden
    video_urls_files = args.video_urls_files or app_config.video_urls_files
    
    # Process each video URLs file
    for urls_file in video_urls_files:
        file_path = folder / urls_file
        print(f"\nProcessing videos from {urls_file}...")
        
        # Load video URLs using data manager
        video_urls = data_manager.load_json(urls_file)
        file_total = len(video_urls)
        file_completed = 0
        file_skipped = 0
        file_no_adobe = 0
        file_processed = 0
        file_reviewed = 0
        
        for video_url in video_urls:
            video_id = data_manager.get_video_id(video_url)
            total_videos += 1
            
            # Debug: Print first few video IDs to check format
            if total_videos <= 3:
                print(f"Debug - Video {total_videos}: URL={video_url}, ID={video_id}")
            
            # Get Adobe caption data for this video first to check if we should skip
            adobe_caption = get_caption_dict_by_filename(
                adobe_captions_data, video_id
            )
            
            # Debug: Check if we found Adobe data for first few videos
            if total_videos <= 3:
                print(f"Debug - Adobe data found for {video_id}: {adobe_caption is not None}")
                if adobe_caption:
                    print(f"Debug - Adobe data keys: {list(adobe_caption.keys())}")
            
            # Skip if no Adobe data and skip_without_adobe is set
            if not adobe_caption and args.skip_without_adobe:
                if total_videos <= 5:  # Only print for first few to avoid spam
                    print(f"Skipping video (no Adobe data): {video_id}")
                skipped_videos += 1
                file_skipped += 1
                continue
            
            # This video will be processed, so count it
            processed_videos += 1
            file_processed += 1
            
            # Track videos without Adobe data
            if not adobe_caption:
                no_adobe_count += 1
                file_no_adobe += 1
            
            # Check if all tasks are completed for this video
            all_tasks_completed = True
            all_tasks_reviewed = True
            video_captions = {}
            
            # Debug: Track review status for first few videos
            debug_review_info = {}
            
            for task, task_name in caption_task_names.items():
                output_name = task_to_output_dir.get(task)
                if not output_name:
                    print(f"WARNING: No output directory found for task {task}")
                    all_tasks_completed = False
                    all_tasks_reviewed = False
                    continue
                
                # Check if feedback exists for this task
                output_dir = folder / app_config.output_dir / output_name
                feedback_filename = data_manager.get_filename(
                    video_id, output_dir=output_dir, file_postfix="_feedback.json"
                )
                
                if os.path.exists(feedback_filename):
                    task_completion[task] += 1
                    
                    # Check if this task has been reviewed (approved)
                    reviewer_filename = data_manager.get_filename(
                        video_id, output_dir=output_dir, file_postfix="_review.json"
                    )
                    
                    is_reviewed = False
                    if os.path.exists(reviewer_filename):
                        try:
                            reviewer_data = data_manager.load_data(
                                video_id, output_dir=output_dir, file_postfix="_review.json"
                            )
                            is_reviewed = reviewer_data.get("reviewer_double_check", False)
                            if is_reviewed:
                                task_reviewed[task] += 1
                        except Exception as e:
                            if total_videos <= 3:  # Debug for first few videos
                                print(f"Error loading reviewer data for {video_id}, task {task}: {e}")
                    
                    # Debug info for first few videos
                    if total_videos <= 3:
                        debug_review_info[task] = {
                            'has_feedback': True,
                            'has_reviewer_file': os.path.exists(reviewer_filename),
                            'is_reviewed': is_reviewed,
                            'reviewer_file': reviewer_filename
                        }
                    
                    if not is_reviewed:
                        all_tasks_reviewed = False
                    
                    # Load feedback data using data manager
                    feedback_data = data_manager.load_data(
                        video_id, output_dir=output_dir, file_postfix="_feedback.json"
                    )
                    if feedback_data and "final_caption" in feedback_data:
                        video_captions[task_name] = feedback_data["final_caption"]
                    else:
                        all_tasks_completed = False
                else:
                    all_tasks_completed = False
                    all_tasks_reviewed = False
                    if total_videos <= 3:  # Debug for first few videos
                        debug_review_info[task] = {
                            'has_feedback': False,
                            'has_reviewer_file': False,
                            'is_reviewed': False
                        }
            
            # Debug: Print review info for first few videos
            if total_videos <= 3:
                print(f"Debug - Video {total_videos} ({video_id}) review status:")
                print(f"  All tasks completed: {all_tasks_completed}")
                print(f"  All tasks reviewed: {all_tasks_reviewed}")
                for task, info in debug_review_info.items():
                    print(f"  {task}: feedback={info['has_feedback']}, reviewer_file={info['has_reviewer_file']}, reviewed={info['is_reviewed']}")
                print()
            
            if all_tasks_completed:
                # Determine review status
                if all_tasks_reviewed:
                    review_status = "All Reviewed (Approved)"
                    reviewed_videos += 1
                    file_reviewed += 1
                else:
                    # Count how many tasks are reviewed
                    reviewed_count = sum(1 for task in caption_task_names.keys() 
                                       if is_task_reviewed(video_id, task, task_to_output_dir, folder, app_config, data_manager))
                    if reviewed_count == 0:
                        review_status = "Not Reviewed"
                    else:
                        review_status = f"Partially Reviewed ({reviewed_count}/5)"
                
                # Skip if only_reviewed is set and not all tasks are reviewed
                if args.only_reviewed and not all_tasks_reviewed:
                    if total_videos <= 5:  # Only print for first few to avoid spam
                        print(f"Skipping video (not fully reviewed): {video_id}")
                    continue
                
                file_completed += 1
                completed_videos += 1
                
                # Create row data combining Adobe data with our captions
                row_data = {}
                
                # Add Adobe data if available
                if adobe_caption:
                    # Map the caption fields to the original column names
                    for col in adobe_columns:
                        col_lower = col.lower()
                        if 'content_id' in col_lower and 'content_id' in adobe_caption:
                            row_data[col] = adobe_caption['content_id']
                        elif 'stock_url' in col_lower and 'stock_url' in adobe_caption:
                            # For lighting config, convert URLs to web viewable format
                            if args.config_type == "lighting":
                                row_data[col] = convert_to_huggingface_web_url(adobe_caption['stock_url'])
                            else:
                                row_data[col] = adobe_caption['stock_url']
                        elif ('summary' in col_lower or 'what is the video about' in col_lower) and 'summary_caption' in adobe_caption:
                            row_data[col] = adobe_caption['summary_caption']
                        elif (('subject' in col_lower and 'background' in col_lower) or 'who or what is in the image' in col_lower) and 'subject_background_caption' in adobe_caption:
                            row_data[col] = adobe_caption['subject_background_caption']
                        elif (('subject' in col_lower and 'action' in col_lower) or 'what are they doing' in col_lower) and 'subject_motion_caption' in adobe_caption:
                            row_data[col] = adobe_caption['subject_motion_caption']
                        elif ('camera' in col_lower or 'how is it captured' in col_lower) and 'camera_caption' in adobe_caption:
                            row_data[col] = adobe_caption['camera_caption']
                        else:
                            row_data[col] = ""
                else:
                    # If no Adobe data, use video_url/video_id for stock_url and content_id
                    for col in adobe_columns:
                        if "stock_url" in col.lower():
                            # For lighting, convert to web viewable URL
                            if args.config_type == "lighting":
                                row_data[col] = convert_to_huggingface_web_url(video_url)
                            else:
                                row_data[col] = video_url
                        elif "content_id" in col.lower():
                            row_data[col] = video_id
                        else:
                            row_data[col] = ""
                
                # Add our captions
                for task_name, caption in video_captions.items():
                    row_data[task_name] = caption
                
                # Add review status
                row_data["Review Status"] = review_status
                
                # Add to DataFrame
                result_df = pd.concat([result_df, pd.DataFrame([row_data])], ignore_index=True)
        
        print(f"File: {Path(urls_file).name}, Total: {file_total}, Processed: {file_processed}, Completed: {file_completed}, Reviewed: {file_reviewed}, No Adobe: {file_no_adobe}, Skipped: {file_skipped}")
    
    # Print overall statistics
    print(f"\nOverall Statistics:")
    print(f"Total Videos: {total_videos}")
    if args.skip_without_adobe:
        print(f"Skipped Videos (no Adobe data): {skipped_videos}")
    if no_adobe_count > 0:
        print(f"Videos Without Adobe Data (included): {no_adobe_count}")
    
    valid_videos = total_videos - skipped_videos
    if valid_videos > 0:
        print(f"Fully Completed Videos: {completed_videos} ({completed_videos/valid_videos*100:.2f}% of processed)")
        print("\nTask Completion:")
        for task, count in task_completion.items():
            print(f"  {caption_task_names[task]}: {count}/{valid_videos} ({count/valid_videos*100:.2f}%)")
    
    # Save to Excel
    output_dir = os.path.dirname(args.output_excel)
    if output_dir:  # Only create directory if there's a directory component
        os.makedirs(output_dir, exist_ok=True)
    result_df.to_excel(args.output_excel, index=False, engine='openpyxl')
    
    # Format Excel file
    format_excel_file(result_df, args.output_excel)
    
    print(f"\nResults saved to {args.output_excel}")
    print(f"Total rows in Excel: {len(result_df)}")


def main():
    # Create an ArgumentParser instance
    parser = argparse.ArgumentParser(description="Unified Caption Collection System")
    
    # Add config type argument
    parser.add_argument(
        "--config-type", 
        type=str, 
        default="main", 
        choices=["main", "lighting"],
        help="Configuration type to use (main or lighting)"
    )
    
    # Add arguments (with defaults that will be set based on config type)
    parser.add_argument(
        "--video_urls_files",
        nargs="*",  # Use * to allow empty list, will fall back to config default
        type=str,
        help="List of paths to video URLs files (uses config default if not specified)"
    )
    
    parser.add_argument(
        "--adobe_excel_files",
        nargs="+",
        type=str,
        default=["adobe_2_19.xlsx", "adobe_2_17.xlsx"],
        help="List of Adobe Excel files"
    )
    
    parser.add_argument(
        "--output_excel",
        type=str,
        help="Path to the output Excel file (uses config-based default if not specified)"
    )
    
    parser.add_argument(
        "--skip_without_adobe",
        action="store_true",
        help="Skip videos that don't have an Adobe caption entry"
    )
    
    parser.add_argument(
        "--only_reviewed",
        action="store_true",
        help="Only include videos where all five tasks have been reviewed (approved)"
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Set output_excel default based on config type if not provided
    if not args.output_excel:
        args.output_excel = get_default_output_excel(args.config_type)
    
    # Run the caption collection process
    count_and_collect_captions(args)


if __name__ == "__main__":
    main()