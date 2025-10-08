#!/usr/bin/env python3
"""
Caption Statistics Analyzer - analyze_caption_stats.py

Analyzes word count statistics for final_caption, initial_feedback, 
and final_feedback across different caption types from exported caption files.
"""

import json
import argparse
import numpy as np
from pathlib import Path
from collections import defaultdict


def count_words(text):
    """
    Count words/characters in a text string.
    For Chinese text, counts characters (excluding spaces and punctuation).
    For English text, counts space-separated words.
    """
    if not text or not isinstance(text, str):
        return 0
    
    # Check if text contains Chinese characters
    chinese_char_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    
    # If more than 30% of non-space characters are Chinese, treat as Chinese text
    non_space_chars = len([c for c in text if not c.isspace()])
    if non_space_chars > 0 and chinese_char_count / non_space_chars > 0.3:
        # Count Chinese characters (excluding spaces and common punctuation)
        return sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    else:
        # Count English words (space-separated tokens)
        return len(text.split())


def analyze_field_statistics(data_dict, field_name):
    """
    Analyze word count statistics for a specific field across all caption types.
    
    Args:
        data_dict: Dictionary of {caption_type: [(word_count, text, video_id)]}
        field_name: Name of the field being analyzed
    
    Returns:
        Dictionary with statistics and examples for each caption type
    """
    stats = {}
    
    for caption_type, data_tuples in data_dict.items():
        if not data_tuples:
            stats[caption_type] = {
                "count": 0,
                "mean": 0,
                "std": 0,
                "min": 0,
                "max": 0,
                "min_example": None
            }
            continue
        
        # Extract word counts
        word_counts = [wc for wc, _, _ in data_tuples]
        
        # Find minimum example
        min_tuple = min(data_tuples, key=lambda x: x[0])
        min_word_count, min_text, min_video_id = min_tuple
        
        stats[caption_type] = {
            "count": len(word_counts),
            "mean": float(np.mean(word_counts)),
            "std": float(np.std(word_counts)),
            "min": int(np.min(word_counts)),
            "max": int(np.max(word_counts)),
            "min_example": {
                "word_count": min_word_count,
                "text": min_text,
                "video_id": min_video_id
            }
        }
    
    return stats


def collect_word_counts(export_file):
    """
    Collect word counts for final_caption, initial_feedback, and final_feedback
    from an exported caption file.
    
    Returns:
        Six dictionaries: 
        - final_caption_counts, initial_feedback_counts, final_feedback_counts (word count lists)
        - final_caption_texts, initial_feedback_texts, final_feedback_texts (actual text strings)
        Each maps caption_type to list of (word_count, text, video_id) tuples
    """
    # Load the export file
    with open(export_file, 'r') as f:
        video_data_list = json.load(f)
    
    final_caption_data = defaultdict(list)
    initial_feedback_data = defaultdict(list)
    final_feedback_data = defaultdict(list)
    
    # Process each video
    for video_data in video_data_list:
        video_id = video_data.get("video_id", "unknown")
        captions = video_data.get("captions", {})
        
        for caption_type, task_data in captions.items():
            # Skip if not completed
            if task_data.get("status") == "not_completed":
                continue
            
            # Get caption_data (main entry)
            caption_data = task_data.get("caption_data", {})
            
            # Collect final_caption word count and text
            final_caption = caption_data.get("final_caption", "")
            if final_caption:
                word_count = count_words(final_caption)
                final_caption_data[caption_type].append((word_count, final_caption, video_id))
            
            # Collect initial_feedback word count and text
            initial_feedback = caption_data.get("initial_feedback", "")
            if initial_feedback:
                word_count = count_words(initial_feedback)
                initial_feedback_data[caption_type].append((word_count, initial_feedback, video_id))
            
            # Collect final_feedback word count and text
            final_feedback = caption_data.get("final_feedback", "")
            if final_feedback:
                word_count = count_words(final_feedback)
                final_feedback_data[caption_type].append((word_count, final_feedback, video_id))
    
    return final_caption_data, initial_feedback_data, final_feedback_data


def print_statistics_table(stats_dict, field_name):
    """Print a formatted table of statistics with minimum examples."""
    print(f"\n{'='*80}")
    print(f"{field_name.upper()} - Word Count Statistics")
    print(f"{'='*80}")
    print(f"{'Caption Type':<20} {'Count':>8} {'Mean':>10} {'Std':>10} {'Min':>8} {'Max':>8}")
    print(f"{'-'*80}")
    
    # Sort by caption type for consistent ordering
    caption_type_order = ["subject", "scene", "motion", "spatial", "camera", "color", "lighting", "effects"]
    
    for caption_type in caption_type_order:
        if caption_type in stats_dict:
            stats = stats_dict[caption_type]
            print(f"{caption_type:<20} {stats['count']:>8} {stats['mean']:>10.2f} "
                  f"{stats['std']:>10.2f} {stats['min']:>8} {stats['max']:>8}")
    
    # Print minimum examples
    print(f"\n{'-'*80}")
    print(f"MINIMUM LENGTH EXAMPLES")
    print(f"{'-'*80}")
    
    for caption_type in caption_type_order:
        if caption_type in stats_dict and stats_dict[caption_type]['min_example']:
            min_ex = stats_dict[caption_type]['min_example']
            print(f"\n{caption_type.upper()} (Video: {min_ex['video_id']}, {min_ex['word_count']} words):")
            # Wrap text at 80 characters for readability
            text = min_ex['text']
            if len(text) > 77:
                print(f"  {text[:77]}...")
            else:
                print(f"  {text}")
            # Show full text if it's longer
            if len(text) > 77:
                remaining = text[77:]
                while remaining:
                    chunk = remaining[:78]
                    print(f"  {chunk}")
                    remaining = remaining[78:]


def save_statistics_json(output_file, final_caption_stats, initial_feedback_stats, final_feedback_stats):
    """Save all statistics to a JSON file."""
    results = {
        "final_caption": final_caption_stats,
        "initial_feedback": initial_feedback_stats,
        "final_feedback": final_feedback_stats
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nStatistics saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze word count statistics for exported caption data"
    )
    
    parser.add_argument(
        "export_file",
        type=str,
        help="Path to exported JSON file (e.g., all_videos_with_captions_20251004_0625.json)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file for statistics (default: same directory as input with _stats.json suffix)"
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    export_file = Path(args.export_file)
    if not export_file.exists():
        print(f"Error: File not found: {export_file}")
        return
    
    print(f"Analyzing caption statistics from: {export_file}")
    
    # Collect word counts
    print("\nCollecting word counts...")
    final_caption_data, initial_feedback_data, final_feedback_data = collect_word_counts(export_file)
    
    # Calculate statistics
    print("Calculating statistics...")
    final_caption_stats = analyze_field_statistics(final_caption_data, "final_caption")
    initial_feedback_stats = analyze_field_statistics(initial_feedback_data, "initial_feedback")
    final_feedback_stats = analyze_field_statistics(final_feedback_data, "final_feedback")
    
    # Print results
    print_statistics_table(final_caption_stats, "final_caption")
    print_statistics_table(initial_feedback_stats, "initial_feedback")
    print_statistics_table(final_feedback_stats, "final_feedback")
    
    # Save to JSON
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = export_file.parent / f"{export_file.stem}_stats.json"
    
    save_statistics_json(output_file, final_caption_stats, initial_feedback_stats, final_feedback_stats)
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()