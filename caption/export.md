# Video Caption Export System Documentation

## Overview: The Caption Task System

The video caption system processes videos through **5 distinct caption tasks**, each focusing on different aspects of video content:

### **Caption Tasks**
| Task | Code | Focus | Example |
|------|------|-------|---------|
| **Subject Description** | `subject` | Main subjects/objects in the video | `"A person walking with a dog"` |
| **Scene Composition and Dynamics** | `scene` | Environment, setting, overall composition | `"Outdoor park setting with trees and pathways"` |
| **Subject Motion and Dynamics** | `motion` | How subjects move and behave | `"Walking at a steady pace, occasionally stopping"` |
| **Spatial Framing and Dynamics** | `spatial` | Camera positioning and spatial relationships | `"Medium shot following the subject from behind"` |
| **Camera Framing and Dynamics** | `camera` | Camera movement and framing techniques | `"Steady handheld tracking shot with slight camera shake"` |

Each video can be processed through all 5 tasks independently. Each task follows the same annotation workflow but produces focused captions for its specific aspect.

## Task-Level Status Categories

Each caption task for each video has one of these statuses:

### 1. **Not Completed** (`not_completed`)
- **Description**: No annotation work has begun for this task
- **File State**: No `_feedback.json` file exists
- **Export**: Status marker only

### 2. **Completed Not Reviewed** (`completed_not_reviewed`) 
- **Description**: Annotator has completed the caption task, waiting for reviewer
- **File State**: `_feedback.json` exists, no `_review.json` file
- **Export**: Single entry with annotator's complete workflow

### 3. **Approved** (`approved`)
- **Description**: Reviewer approved the annotator's caption for this task
- **File State**: `_feedback.json` + `_review.json` with `reviewer_double_check: true`
- **Export**: Single entry (annotator's work that was approved)

### 4. **Rejected** (`rejected`)
- **Description**: Reviewer rejected annotator's caption and provided improved version for this task
- **File State**: `_feedback.json` (reviewer's version) + `_feedback_prev.json` (annotator's version) + `_review.json` with `reviewer_double_check: false`
- **Export**: Two entries - reviewer's improved version + annotator's rejected version as negative example

## Workflow Data Structure

Every caption entry contains complete workflow data from both annotation stages:

### **Stage 1: Pre-Caption Generation**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `pre_caption` | string | AI-generated initial caption | `"A person walking in a park"` |
| `pre_caption_prompt` | string | Prompt used to generate pre-caption | `"Describe the main subject activity in this video"` |
| `pre_caption_llm` | string | Model used for pre-caption | `"gpt-4o-2024-08-06"` |
| `pre_caption_mode` | string | Generation mode (Text/Image/Video) | `"Video"` |
| `initial_caption_rating_score` | integer | User's 1-5 rating of pre-caption | `3` |
| `feedback_is_needed` | boolean | Whether improvement workflow needed | `true` |

### **Stage 2: Feedback and Final Caption**

| Field | Type | Present When | Description |
|-------|------|--------------|-------------|
| `initial_feedback` | string | `feedback_is_needed` | User's raw feedback on pre-caption |
| `gpt_feedback` | string | `feedback_is_needed` | AI-polished version of feedback |
| `gpt_feedback_llm` | string | `feedback_is_needed` | Model used for feedback polishing |
| `gpt_feedback_prompt` | string | `feedback_is_needed` | Prompt used for feedback polishing |
| `feedback_rating_score` | integer | `feedback_is_needed` | User's 1-5 rating of polished feedback |
| `final_feedback` | string | `feedback_is_needed` | Final feedback used for caption generation |
| `gpt_caption` | string | `feedback_is_needed` | AI-generated improved caption |
| `gpt_caption_prompt` | string | `feedback_is_needed` | Prompt used for caption improvement |
| `gpt_caption_llm` | string | `feedback_is_needed` | Model used for caption generation |
| `caption_rating_score` | integer | `feedback_is_needed` | User's 1-5 rating of generated caption |
| `final_caption` | string | Always | Final caption text (either pre-caption or improved version) |

### **Review Metadata (Approved/Rejected Tasks)**

| Field | Type | Description |
|-------|------|-------------|
| `reviewer` | string | Name of the reviewer |
| `review_timestamp` | string | When the review occurred |
| `reviewer_double_check` | boolean | True if approved, False if rejected |
| `original_annotator` | string | Original annotator's name (rejected tasks only) |

## Export Structure

Each video contains task-level data organized by caption type:

```json
{
  "video_id": "video_001",
  "video_url": "https://example.com/video_001.mp4",
  "captions": {
    "subject": { 
      "status": "approved",
      "caption_data": { /* complete workflow data with review metadata */ }
    },
    "scene": { 
      "status": "completed_not_reviewed",
      "caption_data": { /* complete workflow data */ }
    },
    "motion": { 
      "status": "rejected",
      "caption_data": { /* reviewer's improved version */ },
      "negative_example": { /* annotator's rejected version */ }
    },
    "spatial": { 
      "status": "not_completed" 
    },
    "camera": { 
      "status": "approved",
      "caption_data": { /* complete workflow data with review metadata */ }
    }
  }
}
```

## Export Files

The export system creates files organized by meaningful completion levels:

### **Core Export Files**
- `all_videos_with_captions_YYYYMMDD_HHMMSS.json` - All videos with any completed caption tasks
- `reviewed_videos_YYYYMMDD_HHMMSS.json` - Videos with any reviewed tasks (approved OR rejected)
- `not_completed_videos_YYYYMMDD_HHMMSS.json` - Videos with no annotation work begun
- `comprehensive_statistics_YYYYMMDD_HHMMSS.json` - Detailed progress and quality metrics

## Why This Approach Works Better

### **Task-Level Analysis vs Video-Level Categorization**
Videos typically have mixed completion status across their 5 tasks. For example:
- Subject: approved
- Scene: rejected  
- Motion: completed_not_reviewed
- Spatial: not_completed
- Camera: approved

Forcing such videos into a single "approved" or "rejected" category loses critical information and creates misleading categorizations.

### **Meaningful File Organization**
The export files are organized by completion levels that support real analysis needs:

- **all_videos_with_captions.json**: For general dataset analysis and model training
- **reviewed_videos.json**: For quality-assured data where human review has occurred
- **not_completed_videos.json**: For tracking remaining annotation work

## Usage

### **Basic Usage**
```bash
# Export all videos using default configuration
python caption/export.py --export_dir my_exports
```

### **Configuration Options**
```bash
# Use lighting project configuration
python caption/export.py --config-type lighting --export_dir lighting_exports

# Export only videos with reviewed tasks
python caption/export.py --only_reviewed --export_dir reviewed_exports

# Continue export even if edge cases found
python caption/export.py --ignore_errors --export_dir my_exports
```

### **Key Features**
- **Task-Level Organization**: Preserves the multi-dimensional nature of caption data
- **Complete Workflow Preservation**: Captures all annotation and review metadata
- **Negative Examples**: Includes rejected captions for training contrast
- **Edge Case Detection**: Identifies rejected captions that haven't been improved
- **Comprehensive Statistics**: Detailed progress tracking and quality metrics

## Data Analysis Examples

### **Finding High-Quality Captions**
```python
import json

# Load the main export file
with open('all_videos_with_captions_20250910_143022.json', 'r') as f:
    videos = json.load(f)

# Extract all approved captions
approved_captions = []
for video in videos:
    for task_name, task_data in video["captions"].items():
        if task_data.get("status") == "approved":
            approved_captions.append({
                "video_id": video["video_id"],
                "task": task_name,
                "caption": task_data["caption_data"]["final_caption"],
                "workflow_type": task_data["caption_data"]["workflow_type"]
            })

print(f"Found {len(approved_captions)} approved captions")
```

### **Analyzing Review Progress by Task**
```python
# Count completion by task type
task_progress = {}
for video in videos:
    for task_name, task_data in video["captions"].items():
        if task_name not in task_progress:
            task_progress[task_name] = {"total": 0, "completed": 0, "reviewed": 0}
        
        task_progress[task_name]["total"] += 1
        
        status = task_data.get("status", "not_completed")
        if status != "not_completed":
            task_progress[task_name]["completed"] += 1
        if status in ["approved", "rejected"]:
            task_progress[task_name]["reviewed"] += 1

# Print progress report
for task, stats in task_progress.items():
    completion_rate = (stats["completed"] / stats["total"]) * 100
    review_rate = (stats["reviewed"] / stats["completed"]) * 100 if stats["completed"] > 0 else 0
    print(f"{task}: {completion_rate:.1f}% completed, {review_rate:.1f}% reviewed")
```

### **Extracting Training Data with Negative Examples**
```python
# Get training pairs (positive and negative examples)
training_pairs = []
for video in videos:
    for task_name, task_data in video["captions"].items():
        if task_data.get("status") == "rejected" and "negative_example" in task_data:
            training_pairs.append({
                "video_id": video["video_id"],
                "task": task_name,
                "positive_caption": task_data["caption_data"]["final_caption"],
                "negative_caption": task_data["negative_example"]["final_caption"],
                "reviewer": task_data["caption_data"]["reviewer"]
            })

print(f"Found {len(training_pairs)} positive/negative training pairs")
```

## Export Examples

### **Mixed Status Video (Common Scenario)**
```json
{
  "video_id": "video_123",
  "video_url": "https://example.com/video_123.mp4",
  "captions": {
    "subject": {
      "status": "approved",
      "caption_data": {
        "user": "alice_smith",
        "timestamp": "2025-06-29T11:45:00",
        "reviewer": "jane_doe",
        "review_timestamp": "2025-06-29T14:15:00",
        "reviewer_double_check": true,
        "workflow_type": "improved_precaption",
        "pre_caption": "Person with dog",
        "pre_caption_llm": "gpt-4o-2024-08-06",
        "initial_caption_rating_score": 3,
        "feedback_is_needed": true,
        "initial_feedback": "Add more specific details about clothing and setting",
        "gpt_feedback": "Please describe the person's clothing and the park environment more specifically",
        "final_feedback": "Add clothing details and park setting description",
        "gpt_caption": "Person in blue jacket walking small brown dog on leash through park",
        "final_caption": "Person in blue jacket walking small brown dog on leash through sunny suburban park"
      }
    },
    "scene": {
      "status": "rejected",
      "caption_data": {
        "user": "jane_reviewer",
        "timestamp": "2025-06-29T16:20:00",
        "reviewer": "jane_reviewer",
        "review_timestamp": "2025-06-29T15:30:00",
        "reviewer_double_check": false,
        "original_annotator": "bob_smith",
        "workflow_type": "improved_precaption",
        "pre_caption": "Park environment with trees and pathways",
        "initial_caption_rating_score": 2,
        "feedback_is_needed": true,
        "initial_feedback": "Need more environmental detail and atmosphere",
        "final_caption": "Suburban park setting with mature oak trees, paved walking paths, and well-maintained grassy areas under clear sky"
      },
      "negative_example": {
        "user": "bob_smith",
        "timestamp": "2025-06-29T12:15:00",
        "workflow_type": "improved_precaption",
        "pre_caption": "Outdoor area",
        "initial_caption_rating_score": 2,
        "feedback_is_needed": true,
        "initial_feedback": "Add more detail about the setting",
        "final_caption": "Park with trees and pathways"
      }
    },
    "motion": {
      "status": "completed_not_reviewed",
      "caption_data": {
        "user": "charlie_doe",
        "timestamp": "2025-06-29T13:30:00",
        "workflow_type": "perfect_precaption",
        "pre_caption": "Walking at steady pace with dog occasionally sniffing ground and pausing",
        "initial_caption_rating_score": 5,
        "feedback_is_needed": false,
        "final_caption": "Walking at steady pace with dog occasionally sniffing ground and pausing"
      }
    },
    "spatial": {
      "status": "not_completed"
    },
    "camera": {
      "status": "approved",
      "caption_data": {
        "user": "diana_kim",
        "timestamp": "2025-06-29T14:45:00",
        "reviewer": "jane_doe",
        "review_timestamp": "2025-06-29T16:30:00",
        "reviewer_double_check": true,
        "workflow_type": "improved_precaption",
        "pre_caption": "Wide shot",
        "initial_caption_rating_score": 2,
        "feedback_is_needed": true,
        "initial_feedback": "Specify camera position and framing details",
        "final_caption": "Static wide shot from slightly elevated position capturing the full scene with balanced composition"
      }
    }
  }
}
```

This example demonstrates why task-level organization is essential - this single video has 5 different completion states across its caption tasks, making video-level categorization meaningless.