# Video Caption Export System Documentation

## Overview: The 5 Caption Tasks

The video caption system processes videos through **5 distinct caption tasks**, each focusing on different aspects of video content:

### **Caption Tasks**
| Task | Code | Focus | Example |
|------|------|-------|---------|
| **Subject Description** | `subject` | Main subjects/objects in the video | `"A person walking with a dog"` |
| **Scene Composition and Dynamics** | `scene` | Environment, setting, overall composition | `"Outdoor park setting with trees and pathways"` |
| **Subject Motion and Dynamics** | `motion` | How subjects move and behave | `"Walking at a steady pace, occasionally stopping"` |
| **Spatial Framing and Dynamics** | `spatial` | Camera positioning and spatial relationships | `"Medium shot following the subject from behind"` |
| **Camera Framing and Dynamics** | `camera` | Camera movement and framing techniques | `"Steady handheld tracking shot with slight camera shake"` |

Each video can be processed through all 5 tasks independently, and each task follows the same annotation workflow but produces focused captions for its specific aspect.

## Status Categories

Each caption task for each video has one of these statuses:

### 1. **Not Completed** (`not_completed`)
- **Description**: No annotation work has begun for this task
- **File State**: No `_feedback.json` file exists
- **Export**: Not included in exports

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

## Workflow Stages

Every caption entry (whether from annotator or reviewer) contains data from these two stages:

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
Feedback iteration and final caption generation (includes everything after pre-caption).

#### **Complete Field Reference:**
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

## Export Format

### **Video Structure**
Each exported video contains captions for multiple tasks:

```json
{
  "video_id": "video_001",
  "video_url": "https://example.com/video_001.mp4",
  "captions": {
    "subject": { /* task-specific caption data */ },
    "scene": { /* task-specific caption data */ },
    "motion": { /* task-specific caption data */ },
    "spatial": { /* task-specific caption data */ },
    "camera": { /* task-specific caption data */ }
  }
}
```

## Output Files

The export script creates separate JSON files for each status category:

### **Status-Based Exports**
- `not_completed_YYYYMMDD_HHMMSS.json` - Videos with no annotation work begun
- `completed_not_reviewed_YYYYMMDD_HHMMSS.json` - Videos ready for review
- `approved_YYYYMMDD_HHMMSS.json` - High-quality approved captions
- `rejected_YYYYMMDD_HHMMSS.json` - Improved captions with negative examples
- `all_with_captions_YYYYMMDD_HHMMSS.json` - All videos with any completed captions

### **Statistics Report**
- `comprehensive_statistics_YYYYMMDD_HHMMSS.json` - Detailed progress and quality metrics

## Usage

### **Basic Usage**
```bash
# Export all videos using default video URL files from feedback_app.py
python caption/export.py --export_dir my_exports
```

### **Custom Usage**
```bash
# Export only reviewed captions with custom export directory
python caption/export.py --only_reviewed --export_dir my_exports
```

### **Key Features**
- **Automatic Video Discovery**: Uses `DEFAULT_VIDEO_URLS_FILES` from `feedback_app.py` by default
- **Edge Case Detection**: Identifies and reports rejected captions that haven't been improved
- **Quality Metrics**: Comprehensive statistics on progress and annotation quality