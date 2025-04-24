# Video Annotation Process Documentation

## Overview

This documentation explains the complete workflow for processing video URLs, creating batch files, and updating the feedback applications for both the main project and the lighting project.

## 1. Generating Main Project URLs

### Using `load_xlsx.py`

1. **Purpose**: Extracts video URLs from Excel files and creates JSON files for overlapping and non-overlapping videos.

2. **Command**:
   ```bash
   python caption/load_xlsx.py --video_data video_data/20250406_setup_and_motion/videos.json
   ```

3. **Output Files**:
   - `caption/video_urls/20250406_setup_and_motion/overlap_all_X.json`: Contains all overlapping videos
   - `caption/video_urls/20250406_setup_and_motion/nonoverlap_all_X.json`: Contains all non-overlapping videos
   - `caption/video_urls/20250406_setup_and_motion/overlap_X_to_Y.json`: Split files for overlapping videos
   - `caption/video_urls/20250406_setup_and_motion/overlap_invalid.json`: Contains invalid videos from the overlap set
   - `caption/video_urls/20250406_setup_and_motion/nonoverlap_invalid.json`: Contains invalid videos from the non-overlap set
   - Excel files in `caption/excel_export/20250406_setup_and_motion/`

4. **File Naming Conventions**:
   - `overlap_all_X.json`: Contains X overlapping videos
   - `nonoverlap_all_X.json`: Contains X non-overlapping videos
   - `overlap_X_to_Y.json`: Contains videos from index X to Y
   - `overlap_invalid.json`: Contains invalid videos from the overlap set
   - `nonoverlap_invalid.json`: Contains invalid videos from the non-overlap set

5. **Invalid Video Handling**: 
   - `load_xlsx.py` now identifies and separates invalid videos (those with shot transitions) into separate files.
   - It checks each video for shot transition labels using the same approach as `prepare_lighting_urls.py`.
   - Invalid videos are removed from the overlap/nonoverlap files and saved to their respective invalid files.
   - The file counts are updated accordingly.

## 2. Generating Lighting Project URLs

### Using `prepare_lighting_urls.py`

1. **Purpose**: Creates JSON files specifically for the lighting project.

2. **Command**:
   ```bash
   python prepare_lighting_urls.py --json_path video_data/20250406lighting_only/videos.json --output_dir caption/video_urls/lighting_280_new
   ```

3. **Output Files**:
   - `caption/video_urls/lighting_280_new/lighting_only.json`: Contains lighting-specific videos
   - `caption/video_urls/lighting_280_new/invalid_videos.json`: Contains invalid videos (with shot transitions)
   - `caption/video_urls/lighting_280_new/all_labels.json`: Contains videos with all label collections

4. **File Naming Conventions**:
   - `lighting_only.json`: Contains all valid lighting videos
   - `invalid_videos.json`: Contains invalid videos (with shot transitions)
   - `all_labels.json`: Contains videos with all label collections

## 3. Processing New Videos

### Creating Shell Scripts in `process_new_videos/`

1. **Purpose**: Process new videos and create batch files while considering existing videos.

2. **Script Structure**:
   ```bash
   #!/bin/bash
   
   # Process new videos from the dataset
   python caption/process_new_videos.py \
       --new-dir "caption/video_urls/NEW_DIRECTORY" \
       --valid-filename "VALID_FILENAME.json" \
       --invalid-filename "FULL_PATH_TO_INVALID_FILE.json" \
       --invalid-filename-overlap "FULL_PATH_TO_OVERLAP_INVALID_FILE.json" \
       --invalid-filename-nonoverlap "FULL_PATH_TO_NONOVERLAP_INVALID_FILE.json" \
       --batch-files \
           "FULL_PATH_TO_BATCH1.json" \
           "FULL_PATH_TO_BATCH2.json" \
           ... \
       --batch-size 10 \
       --naming-mode [batch|overlap|nonoverlap]
   ```

3. **Parameters**:
   - `--new-dir`: Directory for new batch files
   - `--valid-filename`: Filename for valid videos in the new directory
   - `--invalid-filename`: Full path to the invalid file (optional)
   - `--invalid-filename-overlap`: Full path to the overlap invalid file (optional)
   - `--invalid-filename-nonoverlap`: Full path to the nonoverlap invalid file (optional)
   - `--batch-files`: Full paths to existing batch files (optional)
   - `--batch-size`: Number of videos per batch
   - `--naming-mode`: Naming convention for batch files

4. **Example Scripts**:
   - `main_april_15.sh`: For the main project
   - `lighting_april_14.sh`: For the lighting project
   - `nonoverlap_april_15.sh`: For non-overlapping videos
   - `lighting_april_16.sh`: For the lighting project with invalid file handling

## 4. Updating Feedback Applications

### For Main Project (`feedback_app.py`)

1. **Location**: `caption/feedback_app.py`

2. **Update Process**:
   - Open `feedback_app.py`
   - Find the `video_urls_files` list
   - Add the new batch files from the reminder output
   - Save the file

3. **Example**:
   ```python
   video_urls_files = [
       'video_urls/20250227_0507ground_and_setup/overlap_0_to_94.json',
       # ... existing files ...
       'video_urls/20250406_setup_and_motion/overlap_940_to_1034.json',
       'video_urls/20250406_setup_and_motion/overlap_1034_to_1128.json',
   ]
   ```

### For Lighting Project (`new_feedback_app.py`)

1. **Location**: `caption/new_feedback_app.py`

2. **Update Process**:
   - Open `new_feedback_app.py`
   - Find the `video_urls_files` list
   - Add the new batch files from the reminder output
   - Save the file

3. **Example**:
   ```python
   video_urls_files = [
       'video_urls/lighting_120_new/batch1.json',
       # ... existing files ...
       'video_urls/lighting_280_new/batch11.json',
       'video_urls/lighting_280_new/batch12.json',
   ]
   ```

## 5. Complete Workflow Example

### For Main Project:

1. Generate URLs:
   ```bash
   python caption/load_xlsx.py --video_data video_data/20250406_setup_and_motion/videos.json
   ```

2. Process new videos:
   ```bash
   chmod +x caption/process_new_videos/main_april_15.sh
   ./caption/process_new_videos/main_april_15.sh
   ```

3. Update feedback app:
   - Add the new files to `video_urls_files` in `feedback_app.py`

### For Lighting Project:

1. Generate URLs:
   ```bash
   python prepare_lighting_urls.py --json_path video_data/20250406lighting_only/videos.json --output_dir caption/video_urls/lighting_280_new
   ```

2. Process new videos:
   ```bash
   chmod +x caption/process_new_videos/lighting_april_16.sh
   ./caption/process_new_videos/lighting_april_16.sh
   ```

3. Update feedback app:
   - Add the new files to `video_urls_files` in `new_feedback_app.py`

## 6. Important Notes

1. **File Paths**: Always use full paths for batch files and invalid filename in shell scripts.

2. **Naming Modes**:
   - `batch`: Creates files like `batch1.json`, `batch2.json`, etc.
   - `overlap`: Creates files like `overlap_0_to_94.json`, `overlap_94_to_188.json`, etc.
   - `nonoverlap`: Creates files like `0_to_94.json`, `94_to_188.json`, etc.

3. **Reminder Output**: The script will output a reminder with the new files that need to be added to the feedback app.

4. **Invalid Files**: The script will copy the invalid files to the new directory with the same filenames.

## 7. Recent Improvements

1. **Invalid Video Handling in `load_xlsx.py`**: 
   - `load_xlsx.py` now identifies and separates invalid videos (those with shot transitions) into separate files.
   - It uses the same approach as `prepare_lighting_urls.py` to check for shot transition labels.
   - The implementation:
     - Checks each video for shot transition labels
     - Moves videos with shot transitions to `overlap_invalid.json` or `nonoverlap_invalid.json`
     - Removes these videos from the overlap/nonoverlap files
     - Updates the file counts accordingly

2. **Enhanced `process_new_videos.py`**:
   - Added support for processing overlap and nonoverlap invalid files
   - New command-line arguments:
     - `--invalid-filename-overlap`: For specifying the path to overlap invalid videos
     - `--invalid-filename-nonoverlap`: For specifying the path to nonoverlap invalid videos
   - The script now handles all three types of invalid files (general, overlap, and nonoverlap) 