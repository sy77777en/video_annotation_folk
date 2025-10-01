#!/usr/bin/env python3
"""
Critique Generation Script - caption/generate_critiques.py

Generates critiques using app.py-style folder structure with incremental processing.
Only processes videos with changed caption_data or configuration parameters.

Features:
- Config-based caption type discovery
- Selective critique type generation (parallel execution support)
- Incremental processing (skip unchanged)
- Detailed dry run analysis with accurate counting
- App.py-compatible folder structure
- Complete change detection
- Proper skip status handling and correction
"""

import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from glob import glob
from dotenv import load_dotenv
from huggingface_hub import HfApi

# Import from existing modular structure
from caption.config import get_config
from caption.core.data_manager import DataManager
from llm import get_llm
from caption_policy.prompt_generator import (
    SubjectPolicy, ScenePolicy, SubjectMotionPolicy, 
    SpatialPolicy, CameraPolicy
)

# Import existing mappings for DRY principles
from caption.export import CONFIG_TO_CAPTION

# Prompt templates - aligned with test_critique_generation.py
INSERTION_ERROR_CRITIQUE_PROMPT = """Please modify the following feedback by adding one extra irrelevant or incorrect detail that was not present in the original critique.

Caption Instruction:
{caption_instruction}

Original Caption: {caption}

Original Feedback: {feedback}

Instructions:
1. Insert one additional detail at a random position in the critique that is either irrelevant to the caption task or factually incorrect about the caption
2. Make the addition feel natural and integrated with the original feedback. Inserted feedback should provide concrete details related to the caption instruction, not unrelated visual content or vague suggestions (e.g., asking to mention aspects without specifying what they are)
3. If the original feedback is empty, add one detail that is not include in the original caption and it's incorrect about what's shown.
4. Return only the modified feedback paragraph without any additional text or explanations
5. Avoid repeating any content from the original caption
6. Do not include non-visual elements (e.g., background music, narration)
7. Provide explicit information, not ambiguous details
8. Please try to use affirmative sentence rather than negative or interrogative one
9. Please do not delete the original feedback content, only insert
10. Do not use negative statement (e.g., 'there is no …' or 'avoid mentioning ...') in your inserted feedback"""

REPLACEMENT_ERROR_CRITIQUE_PROMPT = """Please modify the following feedback by replacing one correct detail with wrong or misleading information.

Caption Instruction:
{caption_instruction}

Original Caption: {caption}

Original Feedback: {feedback}

Instructions:
1. Identify one factual detail or suggestion in the original feedback
2. Replace this detail with an incorrect alternative that sounds plausible but is wrong
3. Keep the overall structure and tone of the original feedback
4. Return only the modified feedback paragraph without any additional text or explanations
5. Avoid repeating any content from the original caption
6. Do not include non-visual elements (e.g., background music, narration)
7. Provide explicit information, not ambiguous details
8. If the feedback includes phrases such as 'not xxx', please keep them, as they indicate errors in the original caption"""

DELETION_ERROR_CRITIQUE_PROMPT = """Please modify the following feedback by removing one important detail to make it incomplete.

Caption Instruction:
{caption_instruction}

Original Caption: {caption}

Original Feedback: {feedback}

Instructions:
1. Remove one key detail, suggestion, or explanation from the original feedback only if it is sufficiently long
2. If the original feedback consists of only a single sentence or item, do not simply shorten it, but replace it with 'The caption is accurate and requires no edits, so it should remain exactly the same.'
3. Return only the modified feedback paragraph without any additional text or explanations
4. If the feedback is presented as a numbered list (e.g., 1. xxxx 2. xxxx 3. xxxx …), then when deleting, remove one item at random rather than automatically deleting the last entry
5. Identify the portions of the feedback that conflict with the caption. These conflicting elements are relatively significant and can be prioritized for deletion, but delete only one full element from the original feedback"""

NONCONSTRUCTIVE_CRITIQUE_PROMPT = """Please modify the following feedback to only point out problems without providing any constructive suggestions or solutions.

Caption Instruction:
{caption_instruction}

Original Caption: {caption}

Original Feedback: {feedback}

Instructions:
1. Convert all constructive suggestions in the feedback into criticism only: state only what is wrong in the caption that conflicts with the feedback, without mentioning what is correct.
2. Remove all helpful guidance or improvement suggestions. If the feedback is only guidance or suggestions, replace it with: 'The caption is accurate and requires no edits, so it should remain exactly the same.'
3. Return only the non-constructive feedback paragraph, with no extra text or explanation.
4. When feedback suggests adding something (not changing one thing to another), rephrase it to say the caption is missing that thing, stated generally without details.
5. If the feedback only provides the corrected version without explaining the issues, identify the problematic parts in the caption and state which parts are wrong."""

VIDEO_MODEL_CRITIQUE_PROMPT = """Please provide detailed feedback on how well this caption follows the given instruction. Carefully watch the video and analyze the caption against the instruction requirements.

Caption Instruction:
{caption_instruction}

Caption: {caption}

Instructions:
1. Carefully watch the video and review the caption against the specific requirements in the caption instruction
2. Identify any missing elements, inaccuracies, or areas for improvement based on what you observe in the video
3. Provide specific, actionable suggestions for how to improve the caption
4. Be thorough and constructive in your analysis
5. If the caption is already excellent, simply state 'The caption is accurate and requires no edits, so it should remain exactly the same.'
6. Return only your feedback paragraph without any additional text or explanations
7. If you discover any missing elements in the caption—details present in the video but omitted—you should point out which element has been left out
8. If you find any factual errors in the caption that conflict with the actual video, you should identify where the error occurs and explain how it should be corrected
9. If the caption is overly long and contains information unrelated to the Caption Instruction or is significantly redundant, you should point out those parts and explain that they need to be deleted
10. Do not offer feedback on things not specified in the Caption Instruction. Do not be wordy; keep suggestions concise, direct, and constructive"""

BLIND_MODEL_CRITIQUE_PROMPT = """Please provide feedback on this caption by imagining you have watched the video. Generate a critique by assuming you have visual access to the content (you can imagine anything in the video).

Caption Instruction:
{caption_instruction}

Caption: {caption}

Instructions:
1. Pretend you have watched the video and generate feedback based on your imagined visual content
2. Create specific critique points about what you imagine might be missing or incorrect in the caption
3. Provide suggestions for improvement based on your imagined video content
4. Make the feedback substantial and detailed
5. You can imagine any visual elements that seem plausible for this type of content
6. Return only your feedback paragraph without any additional text or explanations"""

WORST_CAPTION_GENERATION_PROMPT = """Please generate a completely new and incorrect caption that replaces the original caption entirely. The new caption should be plausible-sounding but factually wrong about what's shown in the video.

Caption Instruction:
{caption_instruction}

Original Caption: {caption}

Instructions:
1. Generate a completely new caption that follows the format and structure suggested by the Caption Instruction
2. The new caption should be entirely different from the original - do not reuse any specific details, objects, actions, or descriptions from the original caption
3. Replace all factual content with incorrect or irrelevant alternatives that sound plausible but are wrong
4. Maintain a similar length and level of detail as the original caption
5. The new caption should still attempt to address the Caption Instruction's requirements, but with completely incorrect information
6. Make the incorrect details specific and concrete rather than vague
7. Return only the completely new incorrect caption without any additional text or explanations
8. Do not include non-visual elements (e.g., background music, narration)
9. Ensure the new caption sounds natural and coherent, even though it's factually wrong"""

# Critique task configurations
CRITIQUE_TASKS = {
    "insertion_error_critique": {
        "prompt": INSERTION_ERROR_CRITIQUE_PROMPT,
        "prompt_name": "INSERTION_ERROR_CRITIQUE_PROMPT",
        "model": "gpt-4.1-2025-04-14",
        "mode": "Text Only",
        "supports_video": False,
        "uses_feedback": True,
        "skip_perfect": False
    },
    "replacement_error_critique": {
        "prompt": REPLACEMENT_ERROR_CRITIQUE_PROMPT,
        "prompt_name": "REPLACEMENT_ERROR_CRITIQUE_PROMPT", 
        "model": "gpt-4.1-2025-04-14",
        "mode": "Text Only",
        "supports_video": False,
        "uses_feedback": True,
        "skip_perfect": True
    },
    "deletion_error_critique": {
        "prompt": DELETION_ERROR_CRITIQUE_PROMPT,
        "prompt_name": "DELETION_ERROR_CRITIQUE_PROMPT",
        "model": "gpt-4.1-2025-04-14", 
        "mode": "Text Only",
        "supports_video": False,
        "uses_feedback": True,
        "skip_perfect": True
    },
    "nonconstructive_critique": {
        "prompt": NONCONSTRUCTIVE_CRITIQUE_PROMPT,
        "prompt_name": "NONCONSTRUCTIVE_CRITIQUE_PROMPT",
        "model": "gemini-2.5-pro",
        "mode": "Text Only",
        "supports_video": False,
        "uses_feedback": True,
        "skip_perfect": True
    },
    "video_model_critique": {
        "prompt": VIDEO_MODEL_CRITIQUE_PROMPT,
        "prompt_name": "VIDEO_MODEL_CRITIQUE_PROMPT",
        "model": "gemini-2.5-pro",
        "mode": "Video",
        "supports_video": True,
        "uses_feedback": False,
        "skip_perfect": False
    },
    "blind_model_critique": {
        "prompt": BLIND_MODEL_CRITIQUE_PROMPT,
        "prompt_name": "BLIND_MODEL_CRITIQUE_PROMPT",
        "model": "gemini-2.5-pro",
        "mode": "Text Only",
        "supports_video": False,
        "uses_feedback": False,
        "skip_perfect": False
    },
    "worst_caption_generation": {
        "prompt": WORST_CAPTION_GENERATION_PROMPT,
        "prompt_name": "WORST_CAPTION_GENERATION_PROMPT",
        "model": "gpt-4.1-2025-04-14",
        "mode": "Text Only",
        "supports_video": False,
        "uses_feedback": False,
        "skip_perfect": False
    }
}


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Generate critiques using app.py folder structure")
    parser.add_argument("--config-type", type=str, default="main", 
                       choices=["main", "lighting"],
                       help="Configuration type to use")
    parser.add_argument("--critique-type", type=str, choices=list(CRITIQUE_TASKS.keys()),
                       help="Specific critique type to generate (enables parallel execution)")
    parser.add_argument("--export-folder", type=str, 
                       help="Process specific export folder (optional)")
    parser.add_argument("--export-pattern", type=str, default="caption_export/export_20250917_0354",
                       help="Pattern to find export folders")
    parser.add_argument("--output-dir", type=str, default="output_critiques",
                       help="Base output directory for critiques")
    parser.add_argument("--dry-run", action="store_true", default=False,
                       help="Show what would be processed without generating")
    parser.add_argument("--verbose", action="store_true", default=False,
                       help="Show detailed processing information")
    parser.add_argument("--force-regenerate", action="store_true", default=False,
                       help="Force regeneration of all successful critiques (respects skip rules)")
    parser.add_argument("--new-only", action="store_true", default=False,
                       help="Only process videos without existing critique files")
    parser.add_argument("--max-retries", type=int, default=3,
                       help="Maximum retry attempts for failed generations")
    parser.add_argument("--export-json", action="store_true", default=True,
                       help="Export consolidated JSON file with all critiques (default: True)")
    parser.add_argument("--hf-dataset", type=str, default="zhiqiulin/caption_export",
                       help="HuggingFace dataset repository to upload to")
    return parser.parse_args()


class CritiqueGenerator:
    """Critique generation with app.py-style structure and parallel execution support"""
    
    def __init__(self, config_type: str, output_dir: str):
        self.config_type = config_type
        self.app_config = get_config(config_type)
        self.folder_path = Path(__file__).parent
        self.root_path = self.folder_path.parent
        
        # Fix output directory to be relative to caption folder like app.py
        self.output_dir = self.folder_path / output_dir
        
        # Load environment variables for HuggingFace
        load_dotenv()
        
        # Initialize core components
        self.data_manager = DataManager(self.folder_path, self.root_path)
        
        # Get available caption types and create mappings from configs
        self._load_config_mappings()
        
        # Initialize caption programs for getting instructions
        self.caption_programs = {
            "subject_description": SubjectPolicy(),
            "scene_composition_dynamics": ScenePolicy(),
            "subject_motion_dynamics": SubjectMotionPolicy(),
            "spatial_framing_dynamics": SpatialPolicy(),
            "camera_framing_dynamics": CameraPolicy(),
        }
        
        # Load secrets
        self.secrets = self._load_secrets()
    
    def _load_config_mappings(self):
        """Load config mappings to get proper folder structure from app.py"""
        configs = self.data_manager.load_config(self.app_config.configs_file)
        configs = [self.data_manager.load_config(config) for config in configs]
        
        # Create mappings from config data
        self.caption_type_to_output_name = {}  # "subject" -> "subject_description"
        self.caption_type_to_task = {}         # "subject" -> "subject_description"
        self.available_caption_types = []
        
        for config in configs:
            caption_type = CONFIG_TO_CAPTION.get(config["name"])
            if caption_type:
                self.caption_type_to_output_name[caption_type] = config["output_name"]
                self.caption_type_to_task[caption_type] = config["task"]
                self.available_caption_types.append(caption_type)
    
    def _get_available_caption_types(self) -> List[str]:
        """Get available caption types from config - now handled in _load_config_mappings"""
        return self.available_caption_types
    
    def _load_secrets(self) -> Dict[str, str]:
        """Load API secrets from .streamlit/secrets.toml, .env file, or environment"""
        secrets = {}
        
        # Try to load from .streamlit/secrets.toml (Streamlit format)
        streamlit_secrets_file = self.root_path / ".streamlit" / "secrets.toml"
        if streamlit_secrets_file.exists():
            try:
                import toml
                with open(streamlit_secrets_file) as f:
                    streamlit_secrets = toml.load(f)
                secrets.update({
                    "openai_key": streamlit_secrets.get("openai_key", ""),
                    "gemini_key": streamlit_secrets.get("gemini_key", "")
                })
            except ImportError:
                print("Warning: toml package not found. Install with: pip install toml")
            except Exception as e:
                print(f"Warning: Could not load .streamlit/secrets.toml: {e}")
        
        # Try to load from .env file
        env_file = self.root_path / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        secrets[key] = value.strip('"\'')
        
        # Override with environment variables
        secrets.update({
            "openai_key": os.getenv("OPENAI_API_KEY", secrets.get("OPENAI_API_KEY", secrets.get("openai_key", ""))),
            "gemini_key": os.getenv("GEMINI_API_KEY", secrets.get("GEMINI_API_KEY", secrets.get("gemini_key", "")))
        })
        
        # Validate required keys
        if not secrets.get("openai_key"):
            raise ValueError("Missing openai_key in .streamlit/secrets.toml, OPENAI_API_KEY in environment, or .env file")
        if not secrets.get("gemini_key"):
            raise ValueError("Missing gemini_key in .streamlit/secrets.toml, GEMINI_API_KEY in environment, or .env file")
            
        return secrets
    
    def discover_export_folders(self, export_folder: Optional[str] = None, export_pattern: str = "caption_export/export_20250917_0354") -> List[Path]:
        """Discover export folders to process - now defaults to single folder"""
        if export_folder:
            folder_path = Path(export_folder)
            if folder_path.is_dir():
                return [folder_path]
            else:
                print(f"Warning: Specified export folder {export_folder} does not exist")
                return []
        
        # Check if export_pattern is a direct path (single folder mode)
        pattern_path = Path(export_pattern)
        if pattern_path.is_dir():
            return [pattern_path]
        
        # Fallback to glob pattern matching for backward compatibility
        export_folders = []
        for folder_path in glob(export_pattern):
            folder = Path(folder_path)
            if folder.is_dir():
                export_folders.append(folder)
        
        return sorted(export_folders)
    
    def load_export_data(self, export_folder: Path) -> List[Dict[str, Any]]:
        """Load export data from folder"""
        # Look for all_videos_with_captions_*.json files
        files = list(export_folder.glob("all_videos_with_captions_*.json"))
        
        if not files:
            print(f"Warning: No export files found in {export_folder}")
            return []
        
        # Use the first file found
        export_file = files[0]
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(data, list):
            return data
        else:
            return list(data.values())
    
    def discover_videos_to_process(self, export_folder: Optional[str] = None, 
                                 export_pattern: str = "caption_export/export_20250917_0354") -> List[Tuple[str, str, Dict[str, Any], str, str]]:
        """Discover all videos that need critique processing"""
        videos_to_process = []
        
        export_folders = self.discover_export_folders(export_folder, export_pattern)
        
        for folder in export_folders:
            export_data = self.load_export_data(folder)
            
            for video_data in export_data:
                video_id = video_data["video_id"]
                video_url = video_data["video_url"]
                
                # Only process caption types available in this config
                for caption_type in self.available_caption_types:
                    if caption_type in video_data.get("captions", {}):
                        caption_info = video_data["captions"][caption_type]
                        # ONLY process approved or rejected captions - these are the only ones that should have critiques
                        if caption_info.get("status") in ["approved", "rejected"]:
                            videos_to_process.append((
                                video_id, caption_type, caption_info["caption_data"], 
                                str(folder), video_url
                            ))
        
        return videos_to_process
    
    def get_critique_file_path(self, video_id: str, caption_type: str, critique_type: str) -> Path:
        """Get the file path for a critique following app.py structure"""
        # Use the proper output folder name from config (e.g., "subject_description" not "subject")
        output_folder_name = self.caption_type_to_output_name[caption_type]
        return self.output_dir / critique_type / output_folder_name / f"{video_id}_critique.json"
    
    def load_existing_critique(self, video_id: str, caption_type: str, critique_type: str) -> Optional[Dict[str, Any]]:
        """Load existing critique file if it exists"""
        file_path = self.get_critique_file_path(video_id, caption_type, critique_type)
        
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load {file_path}: {e}")
        
        return None
    
    def should_skip_critique(self, critique_type: str, caption_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Determine if critique generation should be skipped due to perfect score"""
        task_config = CRITIQUE_TASKS[critique_type]
        
        # Skip if configured to skip perfect scores
        if task_config["skip_perfect"]:
            initial_rating = caption_data.get("initial_caption_rating_score")
            if initial_rating == 5:
                return True, f"Perfect score (5/5) - {critique_type} skips perfect scores"
        
        return False, "Not skipped"
    
    def save_skipped_critique(self, video_id: str, caption_type: str, critique_type: str,
                             caption_data: Dict[str, Any], export_folder: str) -> bool:
        """Save a skipped critique marker file"""
        
        file_path = self.get_critique_file_path(video_id, caption_type, critique_type)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        task_config = CRITIQUE_TASKS[critique_type]
        
        skip_data = {
            "video_id": video_id,
            "caption_type": caption_type,
            "critique_type": critique_type,
            "status": "skipped",
            "skip_reason": "Perfect score (5/5) - this critique type skips perfect scores",
            "generation_timestamp": datetime.now().isoformat(),
            "prompt_name": task_config["prompt_name"],
            "model": task_config["model"],
            "mode": task_config["mode"],
            "source_caption_data": caption_data,
            "source_export_folder": export_folder
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(skip_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving skipped critique to {file_path}: {e}")
            return False
    
    def needs_regeneration(self, existing_critique: Dict[str, Any], 
                          new_caption_data: Dict[str, Any], 
                          critique_type: str,
                          force_regenerate: bool = False) -> Tuple[bool, str]:
        """Determine if critique needs to be regenerated (for non-skipped critiques only)"""
        
        # If no existing critique, need to generate
        if not existing_critique:
            return True, "No existing critique found"
        
        # If existing critique failed, always regenerate
        if existing_critique.get("status") == "failed":
            return True, "Previous generation failed"
        
        # If previously skipped but now shouldn't be, regenerate
        if existing_critique.get("status") == "skipped":
            return True, "Previously skipped, but no longer meets skip criteria"
        
        # Always compare entire caption_data - this is the primary check
        if existing_critique.get("source_caption_data") != new_caption_data:
            return True, "Caption data changed"
        
        # Check if generation parameters changed
        current_config = CRITIQUE_TASKS[critique_type]
        config_fields = ["prompt_name", "model", "mode"]
        for field in config_fields:
            if existing_critique.get(field) != current_config[field]:
                return True, f"Generation parameter changed: {field}"
        
        # Apply force_regenerate only for successful critiques
        if force_regenerate and existing_critique.get("status") == "success":
            return True, "Force regeneration requested"
        
        return False, "No changes detected"
    
    def get_caption_instruction_for_task(self, task: str) -> str:
        """Get the caption instruction for the task using PromptGenerator"""
        try:
            if task in self.caption_programs:
                caption_program = self.caption_programs[task]
                return caption_program.get_prompt_without_video_info()
            else:
                return f"Please provide a detailed caption for {task.replace('_', ' ')}."
        except Exception as e:
            print(f"Warning: Could not load caption instruction for {task}: {e}")
            return f"Please provide a detailed caption for {task.replace('_', ' ')}."
    
    def generate_critique_response(self, prompt_template: str, final_feedback: str, 
                                 pre_caption: str, caption_instruction: str,
                                 model_name: str, supports_video: bool, uses_feedback: bool,
                                 video_url: str = "", final_caption: str = "") -> str:
        """Generate critique using LLM"""
        
        # Prepare the final prompt by substituting placeholders
        if uses_feedback:
            final_prompt = prompt_template.format(
                caption_instruction=caption_instruction,
                caption=pre_caption,
                feedback=final_feedback
            )
        else:
            # For complete_replacement_critique, use final_caption instead of pre_caption
            caption_to_use = final_caption if final_caption else pre_caption
            final_prompt = prompt_template.format(
                caption_instruction=caption_instruction,
                caption=caption_to_use
            )
        
        # Get LLM instance
        llm = get_llm(model=model_name, secrets=self.secrets)
        
        # Generate response
        if supports_video and video_url:
            # For video-enabled tasks (Gemini with video)
            response = llm.generate(
                prompt=final_prompt,
                video=video_url,
                extracted_frames=[],  # Use entire video
                temperature=0.0
            )
        else:
            # For text-only tasks
            response = llm.generate(final_prompt)
        
        # Handle empty or whitespace-only responses
        if not response or not response.strip():
            raise Exception("LLM returned an empty response")
        
        return response.strip()
    
    def auto_generate_improved_caption(self, original_caption: str, generated_feedback: str, 
                                     critique_type: str, video_url: str = "") -> str:
        """Auto-generate improved caption"""
        
        # Load the caption improvement prompt
        caption_prompt_path = self.folder_path / "prompts" / "caption_prompt.txt"
        
        if caption_prompt_path.exists():
            with open(caption_prompt_path, 'r') as f:
                caption_prompt_template = f.read()
        else:
            # Fallback prompt if file doesn't exist
            caption_prompt_template = """Given a video caption and user feedback, please provide an improved version of the caption that addresses the feedback. Note that the user feedback could be poorly written, so please try your best to guess what it means.

Original caption: {pre_caption}
User feedback: {feedback}

Respond with the improved caption only, without quotation marks or JSON formatting."""

        # Fill in the actual prompt with real values
        filled_caption_prompt = caption_prompt_template.format(
            pre_caption=original_caption, 
            feedback=generated_feedback
        )

        # For Video Model Critique, use Gemini with video
        if critique_type == "video_model_critique":
            caption_llm = get_llm(model="gemini-2.5-pro", secrets=self.secrets)
            if video_url:
                improved_caption = caption_llm.generate(
                    prompt=filled_caption_prompt,
                    video=video_url,
                    extracted_frames=[],
                    temperature=0.0
                )
            else:
                improved_caption = caption_llm.generate(filled_caption_prompt)
        else:
            # Use GPT-4 for caption improvement
            caption_llm = get_llm(model="gpt-4o-2024-08-06", secrets=self.secrets)
            improved_caption = caption_llm.generate(filled_caption_prompt)
        
        return improved_caption.strip()
    
    def save_critique(self, video_id: str, caption_type: str, critique_type: str,
                     caption_data: Dict[str, Any], export_folder: str,
                     generated_critique: str, revised_caption: str) -> bool:
        """Save critique to file following app.py structure"""
        
        file_path = self.get_critique_file_path(video_id, caption_type, critique_type)
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare critique data
        task_config = CRITIQUE_TASKS[critique_type]
        
        # Special handling for worst_caption_generation
        if critique_type == "worst_caption_generation":
            critique_data = {
                "video_id": video_id,
                "caption_type": caption_type,
                "critique_type": critique_type,
                
                # Generation metadata
                "generation_timestamp": datetime.now().isoformat(),
                "model": task_config["model"],
                "prompt_name": task_config["prompt_name"],
                "mode": task_config["mode"],
                
                # Store entire caption_data for change detection
                "source_caption_data": caption_data,
                "source_export_folder": export_folder,
                
                # Generated content - different structure
                "bad_caption": generated_critique,  # The generated critique IS the bad caption
                
                # Processing status
                "status": "success"
            }
        else:
            critique_data = {
                "video_id": video_id,
                "caption_type": caption_type,
                "critique_type": critique_type,
                
                # Generation metadata
                "generation_timestamp": datetime.now().isoformat(),
                "model": task_config["model"],
                "prompt_name": task_config["prompt_name"],
                "mode": task_config["mode"],
                
                # Store entire caption_data for change detection
                "source_caption_data": caption_data,
                "source_export_folder": export_folder,
                
                # Generated content
                "generated_critique": generated_critique,
                "revised_caption_by_generated_critique": revised_caption,
                
                # Processing status
                "status": "success"
            }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(critique_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving critique to {file_path}: {e}")
            return False
    
    def process_single_critique(self, video_id: str, caption_type: str, critique_type: str,
                              caption_data: Dict[str, Any], export_folder: str, video_url: str,
                              max_retries: int, dry_run: bool = False, verbose: bool = False,
                              force_regenerate: bool = False, new_only: bool = False) -> Tuple[str, str]:
        """Process a single critique with proper skip status handling"""
        
        # Step 1: Determine if this should be skipped based on current caption data
        should_skip_now, skip_reason = self.should_skip_critique(critique_type, caption_data)
        
        # Step 2: Load existing critique if it exists
        existing_critique = self.load_existing_critique(video_id, caption_type, critique_type)
        
        # Step 3: Determine what needs to happen
        if should_skip_now:
            # This critique SHOULD be skipped
            
            if not existing_critique:
                # Case A1: No existing file - create skipped file
                if dry_run:
                    return "would_create_skip", skip_reason
                else:
                    success = self.save_skipped_critique(
                        video_id, caption_type, critique_type, caption_data, export_folder
                    )
                    return "skipped_new" if success else "failed", skip_reason
            
            else:
                existing_status = existing_critique.get("status")
                caption_data_changed = (existing_critique.get("source_caption_data") != caption_data)
                
                if existing_status == "skipped" and not caption_data_changed:
                    # Case A2: Already skipped, no changes
                    return "skipped", "Already skipped, no changes"
                
                else:
                    # Case A3 & A4: Need to update to skipped (either caption changed or wrong status)
                    if dry_run:
                        reason = "Caption changed but still skipped" if caption_data_changed else "Wrong status, needs update to skipped"
                        return "would_update_to_skip", reason
                    else:
                        success = self.save_skipped_critique(
                            video_id, caption_type, critique_type, caption_data, export_folder
                        )
                        return "updated_to_skip" if success else "failed", "Updated to skipped status"
        
        else:
            # This critique should NOT be skipped - needs actual generation
            
            # Check if needs regeneration
            needs_regen, regen_reason = self.needs_regeneration(
                existing_critique, caption_data, critique_type, force_regenerate
            )
            
            # Handle new_only mode
            if new_only and not needs_regen:
                return "skipped", "new_only mode: existing file found"
            
            if not needs_regen:
                return "skipped", f"No changes: {regen_reason}"
            
            # Dry run reporting
            if dry_run:
                if "No existing critique found" in regen_reason:
                    return "generate", regen_reason
                elif "Previous generation failed" in regen_reason:
                    return "regenerate_failed", regen_reason
                else:
                    return "regenerate", regen_reason
            
            # Actually generate critique
            # Get task name for instruction lookup using config mapping
            task_name = self.caption_type_to_task[caption_type]
            caption_instruction = self.get_caption_instruction_for_task(task_name)
            
            # Extract required data
            pre_caption = caption_data.get("pre_caption", "")
            final_caption = caption_data.get("final_caption", "")
            final_feedback = caption_data.get("final_feedback", "")
            
            task_config = CRITIQUE_TASKS[critique_type]
            
            # Retry logic
            for attempt in range(max_retries + 1):
                try:
                    if verbose:
                        print(f"    Attempt {attempt + 1}: Generating {critique_type}...")
                    
                    # Generate critique
                    critique_response = self.generate_critique_response(
                        prompt_template=task_config["prompt"],
                        final_feedback=final_feedback,
                        pre_caption=pre_caption,
                        caption_instruction=caption_instruction,
                        model_name=task_config["model"],
                        supports_video=task_config["supports_video"],
                        uses_feedback=task_config["uses_feedback"],
                        video_url=video_url,
                        final_caption=final_caption
                    )
                    
                    # For worst_caption_generation, the critique_response IS the bad caption (no revision step)
                    if critique_type == "worst_caption_generation":
                        revised_caption = critique_response
                    else:
                        # Generate revised caption for other critique types
                        revised_caption = self.auto_generate_improved_caption(
                            original_caption=pre_caption,
                            generated_feedback=critique_response,
                            critique_type=critique_type,
                            video_url=video_url
                        )
                    
                    # Save critique
                    success = self.save_critique(
                        video_id, caption_type, critique_type, caption_data, 
                        export_folder, critique_response, revised_caption
                    )
                    
                    if success:
                        return "success", regen_reason
                    else:
                        raise Exception("Failed to save critique file")
                    
                except Exception as e:
                    if verbose:
                        print(f"    Attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries:
                        return "failed", f"All {max_retries + 1} attempts failed: {str(e)}"
                    # Wait before retry
                    time.sleep(2)
    
    def collect_all_critiques_for_export(self) -> Dict[str, Any]:
        """Collect all generated critiques into export format"""
        export_data = {}
        
        # Traverse the output directory structure
        for critique_type_dir in self.output_dir.iterdir():
            if not critique_type_dir.is_dir():
                continue
                
            critique_type = critique_type_dir.name
            
            for output_folder_dir in critique_type_dir.iterdir():
                if not output_folder_dir.is_dir():
                    continue
                    
                output_folder_name = output_folder_dir.name  # e.g., "subject_description"
                
                # Find the caption_type that corresponds to this output folder
                caption_type = None
                for ct, output_name in self.caption_type_to_output_name.items():
                    if output_name == output_folder_name:
                        caption_type = ct
                        break
                
                if not caption_type:
                    continue  # Skip if we can't map back to caption type
                
                for critique_file in output_folder_dir.glob("*_critique.json"):
                    try:
                        with open(critique_file, 'r', encoding='utf-8') as f:
                            critique_data = json.load(f)
                        
                        video_id = critique_data["video_id"]
                        status = critique_data.get("status")
                        
                        # Skip failed critiques from export
                        if status == "failed":
                            continue
                        
                        # Initialize nested structure
                        if video_id not in export_data:
                            export_data[video_id] = {
                                "video_id": video_id,
                                "captions": {}
                            }
                        
                        if caption_type not in export_data[video_id]["captions"]:
                            export_data[video_id]["captions"][caption_type] = {}
                        
                        # Add critique data - handle different structures
                        if status == "skipped":
                            export_data[video_id]["captions"][caption_type][critique_type] = {
                                "status": "skipped",
                                "skip_reason": critique_data.get("skip_reason", ""),
                                "timestamp": critique_data["generation_timestamp"]
                            }
                        elif critique_type == "worst_caption_generation":
                            export_data[video_id]["captions"][caption_type][critique_type] = {
                                "status": status,
                                "model": critique_data["model"],
                                "prompt_name": critique_data["prompt_name"],
                                "mode": critique_data["mode"],
                                "bad_caption": critique_data["bad_caption"],
                                "timestamp": critique_data["generation_timestamp"]
                            }
                        else:
                            export_data[video_id]["captions"][caption_type][critique_type] = {
                                "status": status,
                                "model": critique_data["model"],
                                "prompt_name": critique_data["prompt_name"],
                                "mode": critique_data["mode"],
                                "generated_critique": critique_data["generated_critique"],
                                "revised_caption_by_generated_critique": critique_data["revised_caption_by_generated_critique"],
                                "timestamp": critique_data["generation_timestamp"]
                            }
                        
                    except Exception as e:
                        print(f"Warning: Could not load critique file {critique_file}: {e}")
        
        return export_data
    
    def export_consolidated_json(self, target_export_folder: Path) -> Optional[Path]:
        """Export consolidated JSON file to the target export folder"""
        if not target_export_folder.exists():
            print(f"Warning: Target export folder {target_export_folder} does not exist")
            return None
        
        # Collect all critiques
        export_data = self.collect_all_critiques_for_export()
        
        if not export_data:
            print("No critique data found to export")
            return None
        
        # Extract timestamp from export folder name (e.g., "export_20250917_0354" -> "20250917_0354")
        folder_name = target_export_folder.name
        if folder_name.startswith("export_") and len(folder_name) > 7:
            timestamp = folder_name[7:]  # Remove "export_" prefix
        else:
            # Fallback to current timestamp if can't extract from folder name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        filename = f"all_videos_with_captions_and_critiques_{timestamp}.json"
        output_file = target_export_folder / filename
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"Exported consolidated critiques to: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"Error exporting consolidated JSON: {e}")
            return None
    
    def upload_to_huggingface(self, local_file: Path, hf_dataset: str) -> bool:
        """Upload the critique file to HuggingFace dataset"""
        try:
            # Get HuggingFace token from environment
            hf_token = os.getenv("HF_TOKEN")
            if not hf_token:
                print("Warning: HF_TOKEN not found in environment. Skipping HuggingFace upload.")
                return False
            
            # Initialize HuggingFace API
            api = HfApi()
            
            # Upload to same directory structure as original export
            parent_folder = local_file.parent.name  # e.g., "export_20250917_0354"
            remote_path = f"{parent_folder}/{local_file.name}"
            
            print(f"Uploading to HuggingFace dataset: {hf_dataset}")
            print(f"Local file: {local_file}")
            print(f"Remote path: {remote_path}")
            
            api.upload_file(
                path_or_fileobj=str(local_file),
                path_in_repo=remote_path,
                repo_id=hf_dataset,
                repo_type="dataset",
                token=hf_token
            )
            
            print(f"Successfully uploaded to https://huggingface.co/datasets/{hf_dataset}")
            print(f"File visible at: https://huggingface.co/datasets/{hf_dataset}/blob/main/{remote_path}")
            return True
            
        except Exception as e:
            print(f"Error uploading to HuggingFace: {e}")
            print("Processing completed locally, but HuggingFace upload failed.")
            return False
    
    def check_all_critiques_completed(self) -> bool:
        """Check if all critiques are successfully completed for all videos and all critique types"""
        
        # First, discover all videos that should have critiques
        videos_to_process = self.discover_videos_to_process()
        if not videos_to_process:
            return True  # No videos to process
        
        # Get all expected critique types
        all_critique_types = list(CRITIQUE_TASKS.keys())
        
        # Track what we actually have
        videos_with_critiques = set()
        critique_coverage = {}  # {video_id: {caption_type: {critique_type: status}}}
        
        # Scan all existing critique files
        for critique_type_dir in self.output_dir.iterdir():
            if not critique_type_dir.is_dir():
                continue
                
            critique_type = critique_type_dir.name
            if critique_type not in all_critique_types:
                continue  # Skip unknown critique types
                
            for caption_type_dir in critique_type_dir.iterdir():
                if not caption_type_dir.is_dir():
                    continue
                    
                output_folder_name = caption_type_dir.name  # e.g., "subject_description"
                
                # Find the caption_type that corresponds to this output folder
                caption_type = None
                for ct, output_name in self.caption_type_to_output_name.items():
                    if output_name == output_folder_name:
                        caption_type = ct
                        break
                
                if not caption_type:
                    continue  # Skip if we can't map back to caption type
                    
                for critique_file in caption_type_dir.glob("*_critique.json"):
                    try:
                        with open(critique_file, 'r', encoding='utf-8') as f:
                            critique_data = json.load(f)
                        
                        video_id = critique_data["video_id"]
                        status = critique_data.get("status", "unknown")
                        
                        # Initialize nested structure
                        if video_id not in critique_coverage:
                            critique_coverage[video_id] = {}
                        if caption_type not in critique_coverage[video_id]:
                            critique_coverage[video_id][caption_type] = {}
                        
                        critique_coverage[video_id][caption_type][critique_type] = status
                        videos_with_critiques.add(video_id)
                        
                        # If any critique failed, we're not complete
                        if status == "failed":
                            return False
                            
                    except Exception as e:
                        print(f"Warning: Could not check critique file {critique_file}: {e}")
                        return False
        
        # Now check if ALL expected videos have ALL expected critique types
        for video_id, caption_type, caption_data, export_folder, video_url in videos_to_process:
            if video_id not in critique_coverage:
                # This video has no critiques at all
                return False
                
            if caption_type not in critique_coverage[video_id]:
                # This caption type has no critiques
                return False
            
            # Check each critique type for this video-caption combination
            for critique_type in all_critique_types:
                # Check if this critique type should be skipped
                task_config = CRITIQUE_TASKS[critique_type]
                if task_config["skip_perfect"]:
                    initial_rating = caption_data.get("initial_caption_rating_score")
                    if initial_rating == 5:
                        # This critique type should be skipped for perfect scores
                        # Either it should be missing (not generated) or marked as skipped
                        if critique_type in critique_coverage[video_id][caption_type]:
                            status = critique_coverage[video_id][caption_type][critique_type]
                            if status not in ["success", "skipped"]:
                                return False
                        # If missing, that's fine for skipped critique types
                        continue
                
                # For non-skipped critique types, we must have a successful critique
                if critique_type not in critique_coverage[video_id][caption_type]:
                    # Missing required critique
                    return False
                    
                status = critique_coverage[video_id][caption_type][critique_type]
                if status not in ["success", "skipped"]:
                    # Failed or unknown status
                    return False
        
        return True
    
    def analyze_critique_coverage(self, videos_to_process: List[Tuple[str, str, Dict[str, Any], str, str]], 
                                critique_types_to_process: List[str]) -> Dict[str, Any]:
        """Analyze and predict critique generation coverage with detailed breakdown"""
        
        analysis = {
            "total_approved_rejected": len(videos_to_process),
            "available_caption_types": self.available_caption_types,
            "critique_types_to_process": critique_types_to_process,
            "by_critique_type": {},
            "by_caption_type": {},
            "perfect_score_captions": 0,
            "non_perfect_captions": 0
        }
        
        # Analyze by caption type
        caption_type_counts = {}
        for _, caption_type, caption_data, _, _ in videos_to_process:
            if caption_type not in caption_type_counts:
                caption_type_counts[caption_type] = {"total": 0, "perfect": 0, "non_perfect": 0}
            
            caption_type_counts[caption_type]["total"] += 1
            
            if caption_data.get("initial_caption_rating_score") == 5:
                caption_type_counts[caption_type]["perfect"] += 1
                analysis["perfect_score_captions"] += 1
            else:
                caption_type_counts[caption_type]["non_perfect"] += 1
                analysis["non_perfect_captions"] += 1
        
        analysis["by_caption_type"] = caption_type_counts
        
        # Analyze by critique type
        for critique_type in critique_types_to_process:
            task_config = CRITIQUE_TASKS[critique_type]
            skip_perfect = task_config["skip_perfect"]
            
            type_analysis = {
                "skip_perfect_scores": skip_perfect,
                "total_potential": len(videos_to_process),
                "will_skip_perfect": 0,
                "will_process": 0,
                "by_caption_type": {}
            }
            
            # Count what will be processed vs skipped
            for _, caption_type, caption_data, _, _ in videos_to_process:
                is_perfect = caption_data.get("initial_caption_rating_score") == 5
                
                if caption_type not in type_analysis["by_caption_type"]:
                    type_analysis["by_caption_type"][caption_type] = {
                        "total": 0, "will_process": 0, "will_skip_perfect": 0
                    }
                
                type_analysis["by_caption_type"][caption_type]["total"] += 1
                
                if skip_perfect and is_perfect:
                    type_analysis["will_skip_perfect"] += 1
                    type_analysis["by_caption_type"][caption_type]["will_skip_perfect"] += 1
                else:
                    type_analysis["will_process"] += 1
                    type_analysis["by_caption_type"][caption_type]["will_process"] += 1
            
            analysis["by_critique_type"][critique_type] = type_analysis
        
        return analysis
    
    def print_detailed_analysis(self, analysis: Dict[str, Any], verbose: bool = False):
        """Print detailed analysis of what will be processed"""
        
        print(f"Critique Generation Analysis:")
        print(f"============================")
        print(f"Config Type: {self.config_type}")
        print(f"Available Caption Types: {', '.join(analysis['available_caption_types'])}")
        print(f"Critique Types to Process: {', '.join(analysis['critique_types_to_process'])}")
        print()
        
        print(f"Caption Data Summary:")
        print(f"- Total approved/rejected captions: {analysis['total_approved_rejected']}")
        print(f"- Perfect score captions (5/5): {analysis['perfect_score_captions']}")
        print(f"- Non-perfect captions: {analysis['non_perfect_captions']}")
        print()
        
        # Caption type breakdown
        print(f"By Caption Type:")
        for caption_type, counts in analysis["by_caption_type"].items():
            output_name = self.caption_type_to_output_name[caption_type]
            print(f"  {caption_type} ({output_name}):")
            print(f"    Total: {counts['total']} | Perfect: {counts['perfect']} | Non-perfect: {counts['non_perfect']}")
        print()
        
        # Critique type breakdown
        print(f"Critique Processing Breakdown:")
        for critique_type, type_data in analysis["by_critique_type"].items():
            skip_note = " (skips perfect scores)" if type_data["skip_perfect_scores"] else ""
            print(f"  {critique_type}{skip_note}:")
            print(f"    Will process: {type_data['will_process']}")
            print(f"    Will skip (perfect): {type_data['will_skip_perfect']}")
            print(f"    Total potential: {type_data['total_potential']}")
            
            if verbose:
                print(f"    By caption type:")
                for cap_type, cap_data in type_data["by_caption_type"].items():
                    print(f"      {cap_type}: {cap_data['will_process']} process, {cap_data['will_skip_perfect']} skip")
            print()
        
        # Overall summary
        total_operations = sum(type_data["total_potential"] for type_data in analysis["by_critique_type"].values())
        total_will_process = sum(type_data["will_process"] for type_data in analysis["by_critique_type"].values())
        total_will_skip = sum(type_data["will_skip_perfect"] for type_data in analysis["by_critique_type"].values())
        
        print(f"Overall Summary:")
        print(f"- Total possible operations: {total_operations}")
        print(f"- Operations that will process: {total_will_process}")
        print(f"- Operations that will skip (perfect scores): {total_will_skip}")
        print(f"- Effective processing rate: {total_will_process}/{total_operations} ({100*total_will_process/total_operations:.1f}%)")
    
    def run_analysis(self, export_folder: Optional[str] = None, export_pattern: str = "caption_export/export_20250917_0354",
                    dry_run: bool = False, verbose: bool = False, force_regenerate: bool = False,
                    new_only: bool = False, max_retries: int = 3, export_json: bool = False, 
                    hf_dataset: Optional[str] = None, critique_type_filter: Optional[str] = None):
        """Run the complete analysis and processing"""
        
        # Discover videos to process
        videos_to_process = self.discover_videos_to_process(export_folder, export_pattern)
        
        if not videos_to_process:
            print("No videos with approved/rejected captions found to process")
            return
        
        # Determine which critique types to process
        critique_types_to_process = [critique_type_filter] if critique_type_filter else list(CRITIQUE_TASKS.keys())
        
        # Generate detailed analysis
        analysis = self.analyze_critique_coverage(videos_to_process, critique_types_to_process)
        self.print_detailed_analysis(analysis, verbose)
        
        if dry_run:
            print(f"DRY RUN - Detailed Processing Preview:")
            print(f"====================================")
        
        # Group by export folder for analysis
        by_export_folder = {}
        for video_id, caption_type, caption_data, export_folder_name, video_url in videos_to_process:
            if export_folder_name not in by_export_folder:
                by_export_folder[export_folder_name] = []
            by_export_folder[export_folder_name].append((video_id, caption_type, caption_data, video_url))
        
        if verbose or dry_run:
            print(f"\nProcessing Export Folder:")
            for folder, items in by_export_folder.items():
                unique_videos = len(set(item[0] for item in items))
                print(f"  - {folder} ({unique_videos} videos, {len(items)} caption tasks)")
            print()
        
        # Process each video-caption combination
        operation_counts = {
            "generate": 0, 
            "regenerate": 0, 
            "regenerate_failed": 0,
            "would_create_skip": 0,
            "would_update_to_skip": 0,
            "skipped": 0,
            "skipped_new": 0,
            "updated_to_skip": 0,
            "success": 0, 
            "failed": 0
        }
        
        # Process with progress tracking for large datasets
        processed_count = 0
        total_to_process = len(videos_to_process) * len(critique_types_to_process)
        
        for video_id, caption_type, caption_data, export_folder_name, video_url in videos_to_process:
            for critique_type in critique_types_to_process:
                processed_count += 1
                
                # Show progress every 500 operations for large datasets (no individual details)
                if not dry_run and processed_count % 500 == 0:
                    print(f"Progress: {processed_count}/{total_to_process} operations ({100*processed_count/total_to_process:.1f}%)")
                
                status, reason = self.process_single_critique(
                    video_id, caption_type, critique_type, caption_data, 
                    export_folder_name, video_url, max_retries, dry_run, verbose,
                    force_regenerate, new_only
                )
                
                operation_counts[status] += 1
        
        # Final summary
        total_operations = sum(operation_counts.values())
        
        print(f"\n{'DRY RUN ' if dry_run else ''}Processing Summary:")
        print(f"==========================")
        print(f"Total video-caption combinations processed: {len(videos_to_process)}")
        print(f"Total critique operations: {total_operations}")
        
        if not dry_run:
            print(f"- Successful generations: {operation_counts['success']}")
            print(f"- Failed generations: {operation_counts['failed']}")
            print(f"- New skipped files created: {operation_counts['skipped_new']}")
            print(f"- Files updated to skipped: {operation_counts['updated_to_skip']}")
        else:
            print(f"- Would generate new: {operation_counts['generate']}")
            print(f"- Would regenerate (changed): {operation_counts['regenerate']}")
            print(f"- Would regenerate (failed): {operation_counts['regenerate_failed']}")
            print(f"- Would create as skipped: {operation_counts['would_create_skip']}")
            print(f"- Would update to skipped: {operation_counts['would_update_to_skip']}")
        
        print(f"- Already correct (no changes): {operation_counts['skipped']}")
        
        # Export and upload logic (only if not dry run and export_json is True)
        if not dry_run and export_json and (operation_counts["success"] > 0 or operation_counts["skipped_new"] > 0 or operation_counts["updated_to_skip"] > 0):
            print(f"\nExport and Upload:")
            
            # Check if all critiques completed successfully
            all_completed = self.check_all_critiques_completed()
            
            if all_completed:
                print("All critiques completed successfully (no failures)")
                
                # Find the most recent export folder to export to
                export_folders = self.discover_export_folders(export_folder, export_pattern)
                if export_folders:
                    target_folder = export_folders[-1]  # Use most recent
                    
                    # Export consolidated JSON
                    exported_file = self.export_consolidated_json(target_folder)
                    
                    if exported_file and hf_dataset:
                        # Upload to HuggingFace
                        success = self.upload_to_huggingface(exported_file, hf_dataset)
                        if success:
                            print("Upload to HuggingFace completed successfully")
                        else:
                            print("HuggingFace upload failed, but file saved locally")
                    elif exported_file:
                        print("Consolidated JSON exported successfully")
                else:
                    print("No export folder found for consolidated export")
            else:
                print("Some critiques failed or are incomplete.")
                print("Rerun the script to automatically retry failed critiques.")
                print("(Failed critiques are automatically regenerated on subsequent runs)")


def main():
    """Main entry point"""
    args = parse_args()
    
    try:
        generator = CritiqueGenerator(args.config_type, args.output_dir)
        generator.run_analysis(
            export_folder=args.export_folder,
            export_pattern=args.export_pattern,
            dry_run=args.dry_run,
            verbose=args.verbose,
            force_regenerate=args.force_regenerate,
            new_only=args.new_only,
            max_retries=args.max_retries,
            export_json=args.export_json,
            hf_dataset=args.hf_dataset,
            critique_type_filter=args.critique_type
        )
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())