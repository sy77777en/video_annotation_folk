#!/usr/bin/env python3
"""
Complete Caption Export Script - caption/export.py

Exports video captions with proper status categorization and complete workflow data.
Handles all four status types and preserves complete annotation workflow.
Uses DEFAULT_VIDEO_URLS_FILES from feedback_app.py for consistency.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Import only from merge_captions.py for easy migration, plus DEFAULT_VIDEO_URLS_FILES
from merge_captions import (
    load_json, get_video_id, get_filename, load_data, FOLDER, 
    FEEDBACK_FILE_POSTFIX, PREV_FEEDBACK_FILE_POSTFIX, load_config,
    get_video_status
)

# Import DEFAULT_VIDEO_URLS_FILES from feedback_app.py
try:
    from feedback_app import DEFAULT_VIDEO_URLS_FILES
except ImportError:
    # Fallback if import fails
    DEFAULT_VIDEO_URLS_FILES = []


class CaptionExportError(Exception):
    """Custom exception for caption export issues"""
    pass


# Use the same mapping from merge_captions.py
CONFIG_TO_CAPTION = {
    "Subject Description Caption": "subject",
    "Scene Composition and Dynamics Caption": "scene",
    "Subject Motion and Dynamics Caption": "motion",
    "Spatial Framing and Dynamics Caption": "spatial",
    "Camera Framing and Dynamics Caption": "camera"
}


def determine_precise_status(video_id, config_output_dir):
    """
    Determine the precise status of a video caption.
    
    Returns:
        str: One of "not_completed", "completed_not_reviewed", "approved", "rejected"
        str: Error message if edge case detected, None otherwise
    """
    status, current_file, prev_file, current_user, prev_user = get_video_status(video_id, config_output_dir)
    
    # The status from get_video_status already uses the correct names
    if status == "not_completed":
        return "not_completed", None
    elif status == "completed_not_reviewed":
        return "completed_not_reviewed", None
    elif status == "approved":
        return "approved", None
    elif status == "rejected":
        # Check for edge case: rejected but not improved yet
        review_file = get_filename(video_id, config_output_dir, "_review.json")
        if os.path.exists(review_file) and current_file and prev_file:
            try:
                with open(current_file, 'r') as f:
                    current_data = json.load(f)
                with open(prev_file, 'r') as f:
                    prev_data = json.load(f)
                with open(review_file, 'r') as f:
                    review_data = json.load(f)
                
                current_user = current_data.get("user")
                prev_user = prev_data.get("user")
                reviewer = review_data.get("reviewer_name", "Unknown")
                
                if current_user == prev_user:
                    error_msg = (f"Caption rejected by {reviewer} but annotator {current_user} "
                               f"hasn't provided improved version yet")
                    return "rejected_not_improved", error_msg
                    
            except Exception:
                pass
                
        return "rejected", None
    
    return "unknown", f"Unknown status: {status}"


def extract_complete_workflow_data(feedback_data):
    """
    Extract complete workflow data from feedback file.
    Preserves ALL important fields organized by workflow stages.
    """
    if not feedback_data:
        return {}
    
    # Determine workflow type
    initial_rating = feedback_data.get("initial_caption_rating_score")
    workflow_type = "perfect_precaption" if initial_rating == 5 else "improved_precaption"
    
    return {
        # Metadata
        "user": feedback_data.get("user", ""),
        "timestamp": feedback_data.get("timestamp", ""),
        "workflow_type": workflow_type,
        
        # Pre-caption stage (ALWAYS present)
        "pre_caption": feedback_data.get("pre_caption", ""),
        "pre_caption_prompt": feedback_data.get("pre_caption_prompt", ""),
        "pre_caption_llm": feedback_data.get("pre_caption_llm", ""),
        "pre_caption_mode": feedback_data.get("pre_caption_mode", ""),
        "initial_caption_rating_score": feedback_data.get("initial_caption_rating_score"),
        "feedback_is_needed": feedback_data.get("feedback_is_needed"),
        
        # Feedback and final caption stage (includes everything after pre-caption)
        "initial_feedback": feedback_data.get("initial_feedback", ""),
        "gpt_feedback": feedback_data.get("gpt_feedback", ""),
        "gpt_feedback_llm": feedback_data.get("gpt_feedback_llm", ""),
        "gpt_feedback_prompt": feedback_data.get("gpt_feedback_prompt", ""),
        # "feedback_rating": feedback_data.get("feedback_rating", ""),
        "feedback_rating_score": feedback_data.get("feedback_rating_score"),
        "final_feedback": feedback_data.get("final_feedback", ""),
        "gpt_caption": feedback_data.get("gpt_caption", ""),
        "gpt_caption_prompt": feedback_data.get("gpt_caption_prompt", ""),
        "gpt_caption_llm": feedback_data.get("gpt_caption_llm", ""),
        # "caption_rating": feedback_data.get("caption_rating", ""),
        "caption_rating_score": feedback_data.get("caption_rating_score"),
        "final_caption": feedback_data.get("final_caption", "")
    }


def extract_review_metadata(review_file_path):
    """Extract reviewer metadata from review file."""
    if not os.path.exists(review_file_path):
        return {}
    
    try:
        with open(review_file_path, 'r') as f:
            review_data = json.load(f)
        
        return {
            "reviewer": review_data.get("reviewer_name", ""),
            "review_timestamp": review_data.get("review_timestamp", ""),
            "reviewer_double_check": review_data.get("reviewer_double_check", True)
        }
    except Exception as e:
        print(f"Warning: Error loading review metadata: {e}")
        return {}


def extract_caption_data_by_status(video_id, config_output_dir, config_name):
    """
    Extract caption data organized by precise status.
    
    Returns:
        dict: Caption data structured by status type
    """
    precise_status, error_msg = determine_precise_status(video_id, config_output_dir)
    
    if error_msg:
        raise CaptionExportError(f"Video {video_id}, Config {config_name}: {error_msg}")
    
    result = {"status": precise_status}
    
    if precise_status == "not_completed":
        return result
    
    # Load current feedback data
    current_feedback_data = None
    current_file = get_filename(video_id, config_output_dir, FEEDBACK_FILE_POSTFIX)
    if os.path.exists(current_file):
        try:
            current_feedback_data = load_data(video_id, output_dir=config_output_dir, file_postfix="_feedback.json")
        except Exception as e:
            print(f"Warning: Error loading current feedback for {video_id}: {e}")
    
    # Load review metadata if applicable
    review_metadata = {}
    if precise_status in ["approved", "rejected"]:
        review_file = get_filename(video_id, config_output_dir, "_review.json")
        review_metadata = extract_review_metadata(review_file)
    
    if precise_status == "completed_not_reviewed":
        # Single entry: annotator's work
        result["caption_data"] = extract_complete_workflow_data(current_feedback_data)
        
    elif precise_status == "approved":
        # Single entry: annotator's work that was approved
        caption_data = extract_complete_workflow_data(current_feedback_data)
        caption_data.update(review_metadata)
        result["caption_data"] = caption_data
        
    elif precise_status == "rejected":
        # Two entries: reviewer's version (main) + annotator's version (negative example)
        
        # Load previous feedback data (original annotator's version)
        prev_feedback_data = None
        prev_file = get_filename(video_id, config_output_dir, PREV_FEEDBACK_FILE_POSTFIX)
        if os.path.exists(prev_file):
            try:
                prev_feedback_data = load_data(video_id, output_dir=config_output_dir, file_postfix="_feedback_prev.json")
            except Exception as e:
                print(f"Warning: Error loading previous feedback for {video_id}: {e}")
        
        # Main entry: reviewer's improved version
        reviewer_data = extract_complete_workflow_data(current_feedback_data)
        reviewer_data.update(review_metadata)
        if prev_feedback_data:
            reviewer_data["original_annotator"] = prev_feedback_data.get("user", "")
        result["caption_data"] = reviewer_data
        
        # Negative example: original annotator's rejected version
        if prev_feedback_data:
            result["negative_example"] = extract_complete_workflow_data(prev_feedback_data)
    
    return result


def collect_all_videos_by_status(video_urls, output_dir, configs):
    """
    Collect data for all videos organized by status.
    
    Returns:
        dict: {video_id: {video_url, captions: {caption_type: status_data}}}
    """
    all_videos_data = {}
    errors = []
    
    for video_url in video_urls:
        video_id = get_video_id(video_url)
        
        video_data = {
            "video_id": video_id,
            "video_url": video_url,
            "captions": {}
        }
        
        for config in configs:
            config_name = config["name"]
            caption_type = CONFIG_TO_CAPTION.get(config_name)
            if not caption_type:
                continue
                
            config_output_dir = os.path.join(FOLDER, output_dir, config["output_name"])
            if not os.path.exists(config_output_dir):
                video_data["captions"][caption_type] = {"status": "not_completed"}
                continue
            
            try:
                caption_data = extract_caption_data_by_status(video_id, config_output_dir, config_name)
                video_data["captions"][caption_type] = caption_data
                    
            except CaptionExportError as e:
                errors.append(str(e))
                print(f"❌ ERROR: {e}")
            except Exception as e:
                print(f"⚠️  Warning: Unexpected error for {video_id}, {config_name}: {e}")
                video_data["captions"][caption_type] = {"status": "error", "error": str(e)}
        
        all_videos_data[video_id] = video_data
    
    if errors:
        print(f"\n🚨 CRITICAL ERRORS DETECTED:")
        print(f"Found {len(errors)} videos with rejected captions that haven't been improved:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more")
        raise CaptionExportError(f"Found {len(errors)} rejected captions that haven't been improved")
    
    return all_videos_data


def organize_by_precise_status(all_videos_data):
    """
    Organize videos by precise status categories.
    
    Returns:
        dict: {status_category: [video_data]}
    """
    status_categories = {
        "not_completed": [],
        "completed_not_reviewed": [],
        "approved": [],
        "rejected": [],
        "all_with_captions": []
    }
    
    for video_data in all_videos_data.values():
        # Check what statuses this video has across caption types
        video_statuses = set()
        has_any_captions = False
        
        for caption_data in video_data["captions"].values():
            status = caption_data.get("status", "not_completed")
            video_statuses.add(status)
            if status != "not_completed":
                has_any_captions = True
        
        if has_any_captions:
            status_categories["all_with_captions"].append(video_data)
        
        # Add to specific status categories based on what's present
        for status in video_statuses:
            if status in status_categories:
                status_categories[status].append(video_data)
    
    return status_categories


def discover_videos_from_output(output_dir, configs):
    """
    Discover all videos that have caption files in the output directory.
    
    Returns:
        set: Set of video_ids found across all config directories
    """
    all_video_ids = set()
    
    for config in configs:
        config_output_dir = os.path.join(FOLDER, output_dir, config["output_name"])
        if not os.path.exists(config_output_dir):
            continue
            
        # Find all feedback files in this config directory
        for filename in os.listdir(config_output_dir):
            if filename.endswith(FEEDBACK_FILE_POSTFIX):
                video_id = filename.replace(FEEDBACK_FILE_POSTFIX, "")
                all_video_ids.add(video_id)
    
    return all_video_ids


def save_status_files(status_categories, export_dir):
    """Save separate JSON files for each status category."""
    os.makedirs(export_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    saved_files = {}
    
    for status, video_list in status_categories.items():
        if video_list:  # Only save if we have data
            filename = f"{status}_{timestamp}.json"
            filepath = os.path.join(export_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(video_list, f, indent=2)
            
            saved_files[status] = filepath
            print(f"✅ Exported {len(video_list)} videos to {filename}")
        else:
            print(f"⚠️  No videos found for status: {status}")
    
    return saved_files


def generate_comprehensive_statistics(all_videos_data):
    """Generate comprehensive statistics by status and caption type."""
    stats = {
        "export_timestamp": datetime.now().isoformat(),
        "total_videos": len(all_videos_data),
        "by_status": defaultdict(int),
        "by_caption_type": {},
        "workflow_analysis": defaultdict(int),
        "quality_metrics": defaultdict(list)
    }
    
    # Analyze each caption type
    for caption_type in CONFIG_TO_CAPTION.values():
        type_stats = defaultdict(int)
        
        for video_data in all_videos_data.values():
            if caption_type in video_data["captions"]:
                caption_info = video_data["captions"][caption_type]
                status = caption_info.get("status", "not_started")
                type_stats[status] += 1
                stats["by_status"][status] += 1
                
                # Analyze workflow types and quality
                if "caption_data" in caption_info:
                    caption_data = caption_info["caption_data"]
                    workflow_type = caption_data.get("workflow_type", "unknown")
                    stats["workflow_analysis"][workflow_type] += 1
                    
                    # Collect quality metrics
                    initial_rating = caption_data.get("initial_caption_rating_score")
                    if initial_rating is not None:
                        stats["quality_metrics"]["initial_ratings"].append(initial_rating)
                    
                    final_rating = caption_data.get("caption_rating_score")
                    if final_rating is not None:
                        stats["quality_metrics"]["final_ratings"].append(final_rating)
        
        stats["by_caption_type"][caption_type] = dict(type_stats)
    
    # Calculate averages
    if stats["quality_metrics"]["initial_ratings"]:
        stats["quality_metrics"]["avg_initial_rating"] = sum(stats["quality_metrics"]["initial_ratings"]) / len(stats["quality_metrics"]["initial_ratings"])
    if stats["quality_metrics"]["final_ratings"]:
        stats["quality_metrics"]["avg_final_rating"] = sum(stats["quality_metrics"]["final_ratings"]) / len(stats["quality_metrics"]["final_ratings"])
    
    return stats


def print_status_examples():
    """Print clear examples of each status type across the 5 caption tasks."""
    print("\n📋 EXPORT FORMAT EXAMPLES")
    print("=" * 60)
    print("Shows how the 5 caption tasks are organized by status")
    
    print("\n1️⃣ COMPLETED NOT REVIEWED (Single Entry per Task):")
    example_not_reviewed = {
        "video_id": "video_001",
        "video_url": "https://example.com/video_001.mp4",
        "captions": {
            "subject": {
                "status": "completed_not_reviewed",
                "caption_data": {
                    "user": "john_doe",
                    "timestamp": "2025-06-29T10:30:00",
                    "workflow_type": "improved_precaption",
                    
                    # Pre-caption stage
                    "pre_caption": "A person walking in a park",
                    "pre_caption_prompt": "Describe the main subject in this video",
                    "pre_caption_llm": "gpt-4o-2024-08-06",
                    "pre_caption_mode": "Text Only",
                    "initial_caption_rating_score": 3,
                    "feedback_is_needed": True,
                    
                    # Feedback and final caption stage
                    "initial_feedback": "Add more detail about the person and setting",
                    "gpt_feedback": "Please describe the person more specifically and add details about the park setting",
                    "gpt_feedback_llm": "gpt-4o-2024-08-06",
                    "feedback_rating_score": 5,
                    "final_feedback": "Please describe the person more specifically and add details about the park setting",
                    "gpt_caption": "A person wearing casual clothes walking briskly through a park",
                    # ... complete workflow data
                    "final_caption": "A person wearing casual clothes walking briskly through a tree-lined suburban park"
                }
            },
            "scene": {
                "status": "completed_not_reviewed", 
                "caption_data": {
                    "user": "john_doe",
                    "timestamp": "2025-06-29T10:35:00",
                    "workflow_type": "perfect_precaption",
                    "pre_caption": "Outdoor park environment with mature trees, grass areas, and paved walkways",
                    "initial_caption_rating_score": 5,
                    "feedback_is_needed": False,
                    # ... complete workflow data
                    "final_caption": "Outdoor park environment with mature trees, grass areas, and paved walkways"
                }
            }
        }
    }
    print(json.dumps(example_not_reviewed, indent=2))
    
    print("\n2️⃣ APPROVED (Approved Across Multiple Tasks):")
    example_approved = {
        "video_id": "video_002",
        "video_url": "https://example.com/video_002.mp4",
        "captions": {
            "motion": {
                "status": "approved",
                "caption_data": {
                    "user": "alice_smith",
                    "timestamp": "2025-06-29T11:45:00",
                    "reviewer": "jane_doe",
                    "review_timestamp": "2025-06-29T14:15:00",
                    "reviewer_double_check": True,
                    "workflow_type": "improved_precaption",
                    "pre_caption": "Person walking along path",
                    "initial_caption_rating_score": 3,
                    "feedback_is_needed": True,
                    "initial_feedback": "Add details about pace and rhythm",
                    # ... complete workflow data
                    "final_caption": "Walking at a steady, moderate pace with occasional brief pauses"
                }
            },
            "camera": {
                "status": "approved",
                "caption_data": {
                    "user": "alice_smith",
                    "timestamp": "2025-06-29T11:50:00",
                    "reviewer": "jane_doe",
                    "review_timestamp": "2025-06-29T14:20:00", 
                    "reviewer_double_check": True,
                    "workflow_type": "perfect_precaption",
                    "pre_caption": "Static wide shot from a fixed position capturing the entire walking area",
                    "initial_caption_rating_score": 5,
                    "feedback_is_needed": False,
                    # ... complete workflow data
                    "final_caption": "Static wide shot from a fixed position capturing the entire walking area"
                }
            }
        }
    }
    print(json.dumps(example_approved, indent=2))
    
    print("\n3️⃣ REJECTED (Improved + Negative Example):")
    example_rejected = {
        "video_id": "video_003",
        "video_url": "https://example.com/video_003.mp4",
        "captions": {
            "spatial": {
                "status": "rejected",
                "caption_data": {
                    # REVIEWER'S IMPROVED VERSION
                    "user": "jane_reviewer",
                    "timestamp": "2025-06-29T16:20:00",
                    "reviewer": "jane_reviewer", 
                    "review_timestamp": "2025-06-29T15:30:00",
                    "reviewer_double_check": False,
                    "original_annotator": "bob_smith",
                    "workflow_type": "improved_precaption",
                    
                    # Reviewer might use different pre-caption
                    "pre_caption": "Wide shot of person in park setting",
                    "pre_caption_prompt": "Describe the spatial framing and positioning in this video",
                    "pre_caption_llm": "gpt-4o-2024-08-06",
                    "initial_caption_rating_score": 2,
                    "feedback_is_needed": True,
                    "initial_feedback": "Specify composition and environmental context more clearly",
                    # ... complete improved workflow data
                    "final_caption": "Wide establishing shot capturing subject in center-frame with balanced composition showing surrounding park environment"
                },
                "negative_example": {
                    # ORIGINAL ANNOTATOR'S REJECTED VERSION
                    "user": "bob_smith",
                    "timestamp": "2025-06-29T12:15:00",
                    "workflow_type": "improved_precaption",
                    "pre_caption": "Person in a park",
                    "pre_caption_prompt": "Describe the spatial framing and positioning in this video",
                    "initial_caption_rating_score": 2,
                    "feedback_is_needed": True,
                    "initial_feedback": "Add more detail about the shot",
                    # ... complete rejected workflow data
                    "final_caption": "Shot of person walking in park area"
                }
            }
        }
    }
    print(json.dumps(example_rejected, indent=2))
    
    print("\n4️⃣ MULTI-TASK VIDEO (All 5 Caption Tasks):")
    multi_task_example = {
        "video_id": "video_004",
        "video_url": "https://example.com/video_004.mp4",
        "captions": {
            "subject": {
                "status": "approved",
                "caption_data": {
                    "user": "alice_smith",
                    "reviewer": "jane_doe",
                    "review_timestamp": "2025-06-29T14:15:00",
                    # ... complete workflow data
                    "final_caption": "A person walking with a small dog on a leash"
                }
            },
            "scene": {
                "status": "completed_not_reviewed",
                "caption_data": {
                    "user": "bob_smith", 
                    "timestamp": "2025-06-29T11:20:00",
                    # ... complete workflow data
                    "final_caption": "Outdoor residential park with mature trees and paved walkways"
                }
            },
            "motion": {
                "status": "rejected",
                "caption_data": {
                    "user": "jane_reviewer",
                    "reviewer": "jane_reviewer",
                    "original_annotator": "charlie_doe",
                    # ... complete improved workflow data
                    "final_caption": "Walking at a leisurely pace with occasional pauses for the dog"
                },
                "negative_example": {
                    "user": "charlie_doe",
                    # ... complete rejected workflow data
                    "final_caption": "Person and dog walking"
                }
            },
            "spatial": {
                "status": "not_completed"
            },
            "camera": {
                "status": "approved",
                "caption_data": {
                    "user": "diana_kim",
                    "reviewer": "jane_doe",
                    "review_timestamp": "2025-06-29T16:30:00",
                    # ... complete workflow data
                    "final_caption": "Static wide shot from slightly elevated position"
                }
            }
        }
    }
    print(json.dumps(multi_task_example, indent=2))


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Export video captions with complete status categorization")
    
    # Same arguments as feedback_app.py and merged_app.py
    parser.add_argument("--configs", type=str, default="all_configs.json",
                      help="Path to the configs JSON file")
    parser.add_argument(
        "--video_urls_files",
        nargs="*",
        type=str,
        default=DEFAULT_VIDEO_URLS_FILES,
        help="List of paths to video URLs files (default: uses DEFAULT_VIDEO_URLS_FILES from feedback_app.py)",
    )
    parser.add_argument("--output", type=str, default="output_captions",
                      help="Path to the output directory containing captions")
    parser.add_argument("--export_dir", type=str, default="exported_captions_complete",
                      help="Directory to save exported caption files")
    parser.add_argument("--only_reviewed", action="store_true", default=False,
                      help="If set, only export captions that have been reviewed")
    parser.add_argument("--ignore_errors", action="store_true", default=False,
                      help="Continue export even if rejected-but-not-improved captions are found")
    
    args = parser.parse_args()
    
    print("🎥 Complete Caption Export Script Starting...")
    print(f"📂 Output Directory: {args.output}")
    print(f"📋 Config File: {args.configs}")
    print(f"💾 Export Directory: {args.export_dir}")
    
    # Load configs first
    try:
        configs = load_config(FOLDER / args.configs)
        configs = [load_config(FOLDER / config) for config in configs]
        print(f"⚙️  Loaded {len(configs)} caption configs")
    except Exception as e:
        print(f"❌ Error loading configs: {e}")
        return
    
    # Get video URLs either from files or by discovering from output directory
    video_urls = []
    if args.video_urls_files:
        print(f"📁 Loading videos from {len(args.video_urls_files)} URL files...")
        for urls_file in args.video_urls_files:
            try:
                file_videos = load_json(FOLDER / urls_file)
                video_urls.extend(file_videos)
                print(f"  - {urls_file}: {len(file_videos)} videos")
            except Exception as e:
                print(f"⚠️  Error loading {urls_file}: {e}")
        print(f"📊 Total videos from URL files: {len(video_urls)}")
    else:
        print("🔍 No video URL files provided, discovering videos from output directory...")
        discovered_video_ids = discover_videos_from_output(args.output, configs)
        # Convert video IDs back to dummy URLs for processing
        video_urls = [f"dummy_url/{video_id}.mp4" for video_id in discovered_video_ids]
        print(f"📊 Discovered {len(video_urls)} videos from output directory")
    
    if not video_urls:
        print("❌ No videos found to export")
        return
    
    # Collect all video data by status
    print("\n🔍 Analyzing video caption data by status...")
    try:
        all_videos_data = collect_all_videos_by_status(video_urls, args.output, configs)
    except CaptionExportError as e:
        if args.ignore_errors:
            print(f"⚠️  Ignoring errors and continuing export...")
            return
        else:
            print(f"❌ Export failed due to data integrity issues.")
            print(f"Fix the rejected captions or use --ignore_errors to continue anyway.")
            return
    
    # Filter by review status if requested
    if args.only_reviewed:
        print("🔍 Filtering for only reviewed captions...")
        filtered_data = {}
        for video_id, video_data in all_videos_data.items():
            has_reviewed = any(
                caption_data.get("status") in ["approved", "rejected"]
                for caption_data in video_data["captions"].values()
            )
            if has_reviewed:
                filtered_data[video_id] = video_data
        all_videos_data = filtered_data
        print(f"📊 {len(all_videos_data)} videos have reviewed captions")
    
    # Organize by status and save
    print(f"\n📤 Organizing and exporting data by status...")
    status_categories = organize_by_precise_status(all_videos_data)
    saved_files = save_status_files(status_categories, args.export_dir)
    
    # Generate and save statistics
    print("\n📈 Generating comprehensive statistics...")
    stats = generate_comprehensive_statistics(all_videos_data)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stats_file = os.path.join(args.export_dir, f"comprehensive_statistics_{timestamp}.json")
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Print summary
    print(f"\n📊 EXPORT SUMMARY BY CAPTION TASKS")
    print(f"{'='*60}")
    print(f"Total Videos: {stats['total_videos']}")
    
    print(f"\nOverall Status Distribution:")
    for status, count in stats["by_status"].items():
        if count > 0:
            print(f"  - {status.replace('_', ' ').title()}: {count}")
    
    print(f"\nPer Caption Task Breakdown:")
    task_names = {
        "subject": "Subject Description",
        "scene": "Scene Composition", 
        "motion": "Subject Motion",
        "spatial": "Spatial Framing",
        "camera": "Camera Framing"
    }
    
    for caption_type, task_name in task_names.items():
        if caption_type in stats["by_caption_type"]:
            task_stats = stats["by_caption_type"][caption_type]
            total_task = sum(task_stats.values())
            print(f"\n  📋 {task_name} Task ({total_task} videos):")
            for status, count in task_stats.items():
                if count > 0:
                    percentage = (count/total_task)*100
                    print(f"    - {status.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
    
    print(f"\nWorkflow Type Analysis:")
    for workflow_type, count in stats["workflow_analysis"].items():
        if count > 0:
            print(f"  - {workflow_type.replace('_', ' ').title()}: {count}")
    
    if "avg_initial_rating" in stats["quality_metrics"]:
        print(f"\nQuality Metrics Across All Tasks:")
        print(f"  - Average Initial Rating: {stats['quality_metrics']['avg_initial_rating']:.2f}/5")
        if "avg_final_rating" in stats["quality_metrics"]:
            print(f"  - Average Final Rating: {stats['quality_metrics']['avg_final_rating']:.2f}/5")
    
    print(f"\n📁 Export Files Created:")
    for status, filepath in saved_files.items():
        print(f"  - {status.replace('_', ' ').title()}: {os.path.basename(filepath)}")
    print(f"  - Comprehensive Statistics: {os.path.basename(stats_file)}")
    
    # Print export format examples
    print_status_examples()
    
    print(f"\n✅ Caption Export Completed Successfully!")
    print(f"📁 Export Directory: {args.export_dir}")
    print(f"📚 Complete Documentation: comprehensive_status_documentation.md")
    print(f"🎯 Exported {len(all_videos_data)} videos across 5 caption tasks with complete workflow data")


if __name__ == "__main__":
    main()