# caption/test_llm.py
import streamlit as st
import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from caption.config import get_config
from caption.core.data_manager import DataManager  
from caption.core.video_utils import VideoUtils
from caption.core.ui_components import UIComponents

from llm import get_llm, get_all_llms
from caption_policy.prompt_generator import (
    SubjectPolicy, ScenePolicy, SubjectMotionPolicy, 
    SpatialPolicy, CameraPolicy, VanillaCameraMotionPolicy, 
    RawSpatialPolicy, RawSubjectMotionPolicy
)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="LLM Testing Interface for Video Captions")
    parser.add_argument("--config-type", type=str, default="main", 
                       choices=["main", "lighting"],
                       help="Configuration type to use")
    return parser.parse_args()


class LLMTestApp:
    """LLM testing application for video captions"""
    
    def __init__(self, config_type: str):
        self.app_config = get_config(config_type)
        self.folder_path = Path(__file__).parent  # caption/ directory  
        self.root_path = self.folder_path.parent  # Go up to project root
        
        # Initialize core components
        self.data_manager = DataManager(self.folder_path, self.root_path)
        self.video_utils = VideoUtils()
        self.ui = UIComponents()
        
        # Load JSON policy
        self.json_policy_path = self.root_path / "json_policy" / "json_policy.json"
        self.json_policy = self.load_json_policy()
        
        # Initialize caption programs for getting caption instructions
        self.caption_programs = {
            "subject_description": SubjectPolicy(),
            "scene_composition_dynamics": ScenePolicy(),
            "subject_motion_dynamics": SubjectMotionPolicy(),
            "spatial_framing_dynamics": SpatialPolicy(),
            "camera_framing_dynamics": CameraPolicy(),
        }
    
    def load_json_policy(self) -> Dict[str, Any]:
        """Load the JSON policy file"""
        try:
            if self.json_policy_path.exists():
                with open(self.json_policy_path, 'r') as f:
                    return json.load(f)
            else:
                st.warning(f"JSON policy file not found at {self.json_policy_path}")
                return {}
        except Exception as e:
            st.error(f"Error loading JSON policy: {e}")
            return {}
    
    def get_all_reviewed_videos(self) -> List[Dict[str, Any]]:
        """Get all videos that have been fully reviewed across all tasks"""
        reviewed_videos = []
        
        try:
            # Load configs
            configs = self.data_manager.load_config(self.app_config.configs_file)
            if isinstance(configs[0], str):
                configs = [self.data_manager.load_config(config) for config in configs]
            
            # Check all video URL files
            for video_urls_file in self.app_config.video_urls_files:
                try:
                    video_urls = self.data_manager.load_json(video_urls_file)
                    
                    # Extract sheet name from file path
                    sheet_name = Path(video_urls_file).stem  # Gets filename without extension
                    
                    for video_url in video_urls:
                        video_id = self.data_manager.get_video_id(video_url)
                        
                        # Check if all tasks are completed and reviewed
                        all_reviewed = True
                        video_captions = {}
                        reviewer_names = set()  # Track all reviewers for this video
                        
                        for config in configs:
                            config_output_dir = os.path.join(
                                self.data_manager.folder, 
                                self.app_config.output_dir, 
                                config["output_name"]
                            )
                            
                            status, current_file, prev_file, current_user, prev_user = self.data_manager.get_video_status(
                                video_id, config_output_dir
                            )
                            
                            if status != "approved":
                                all_reviewed = False
                                break
                            else:
                                # Load the final caption data
                                feedback_data = self.data_manager.load_data(
                                    video_id, config_output_dir, self.data_manager.FEEDBACK_FILE_POSTFIX
                                )
                                
                                # Load reviewer data
                                reviewer_data = self.data_manager.load_data(
                                    video_id, config_output_dir, self.data_manager.REVIEWER_FILE_POSTFIX
                                )
                                
                                reviewer_name = "Unknown"
                                if reviewer_data:
                                    reviewer_name = reviewer_data.get("reviewer_name", "Unknown")
                                    reviewer_names.add(reviewer_name)
                                
                                if feedback_data:
                                    video_captions[config["name"]] = {
                                        "final_caption": feedback_data.get("final_caption", ""),
                                        "annotator": feedback_data.get("user", "Unknown"),
                                        "reviewer": reviewer_name,
                                        "timestamp": feedback_data.get("timestamp", ""),
                                        "task": config["task"],
                                        "config": config
                                    }
                        
                        if all_reviewed and video_captions:
                            reviewed_videos.append({
                                "video_id": video_id,
                                "video_url": video_url,
                                "sheet_name": sheet_name,
                                "reviewers": list(reviewer_names),  # All unique reviewers for this video
                                "captions": video_captions
                            })
                            
                except Exception as e:
                    st.error(f"Error processing video file {video_urls_file}: {e}")
                    continue
                    
        except Exception as e:
            st.error(f"Error loading configurations: {e}")
        
        return reviewed_videos
    
    def render_video_selection_sidebar(self, reviewed_videos: List[Dict[str, Any]]):
        """Render video selection in sidebar"""
        st.sidebar.title("🎥 LLM Caption Testing")
        st.sidebar.markdown("### Select a video to test LLM prompts")
        
        if not reviewed_videos:
            st.sidebar.warning("No fully reviewed videos found.")
            return None
        
        # Create video options with sheet names
        video_options = {}
        for video_data in reviewed_videos:
            video_id = video_data["video_id"]
            sheet_name = video_data["sheet_name"]
            caption_count = len(video_data["captions"])
            display_name = f"{video_id} ({sheet_name}) - {caption_count} captions"
            video_options[display_name] = video_data
        
        selected_display = st.sidebar.selectbox(
            "Select Video:",
            list(video_options.keys()),
            key="selected_video"
        )
        
        if selected_display:
            return video_options[selected_display]
        return None
    
    def render_task_selection_sidebar(self, selected_video: Dict[str, Any]):
        """Render task selection in sidebar"""
        if not selected_video:
            return None
            
        captions = selected_video["captions"]
        task_options = {}
        
        for caption_name, caption_data in captions.items():
            short_name = self.ui.config_names_to_short_names.get(caption_name, caption_name)
            # Add reviewer info to the display
            annotator = caption_data["annotator"]
            reviewer = caption_data["reviewer"]
            display_with_info = f"{short_name} (A:{annotator[:8]}, R:{reviewer[:8]})"
            task_options[display_with_info] = caption_data
        
        selected_task_display = st.sidebar.selectbox(
            "Select Task:",
            list(task_options.keys()),
            key="selected_task"
        )
        
        if selected_task_display:
            return task_options[selected_task_display]
        return None
    
    def render_video_display(self, selected_video: Dict[str, Any]):
        """Render video display in the right column"""
        if not selected_video:
            return
            
        st.subheader("📹 Video Preview")
        
        # Display video
        video_url = selected_video["video_url"]
        if video_url:
            st.video(video_url)
        else:
            st.warning("Video URL not available")
        
        # Display video info
        st.write(f"**Video ID:** {selected_video['video_id']}")
        st.write(f"**Sheet:** {selected_video['sheet_name']}")
        st.write(f"**Total Tasks Completed:** {len(selected_video['captions'])}")
        
        # Display reviewer info
        reviewers = selected_video.get('reviewers', [])
        if reviewers:
            if len(reviewers) == 1:
                st.write(f"**Reviewer:** {reviewers[0]}")
            else:
                st.write(f"**Reviewers:** {', '.join(reviewers)}")
        
        # Show all captions summary
        with st.expander("📝 All Captions Summary", expanded=False):
            for caption_name, caption_data in selected_video["captions"].items():
                st.write(f"**{caption_name}**")
                st.write(f"- Annotator: {caption_data['annotator']}")
                st.write(f"- Reviewer: {caption_data['reviewer']}")
                st.write(f"- Timestamp: {self.data_manager.format_timestamp(caption_data['timestamp'])}")
                st.write("---")
    
    def get_caption_instruction_for_task(self, task: str) -> str:
        """Get the caption instruction for the task using PromptGenerator"""
        try:
            if task in self.caption_programs:
                caption_program = self.caption_programs[task]
                return caption_program.get_prompt_without_video_info()
            else:
                return f"Please provide a detailed caption for {task.replace('_', ' ')}."
        except Exception as e:
            st.warning(f"Could not load caption instruction for {task}: {e}")
            return f"Please provide a detailed caption for {task.replace('_', ' ')}."
    
    def get_json_policy_for_task(self, task: str) -> Dict[str, Any]:
        """Get the JSON policy structure for the task"""
        if not self.json_policy:
            return {}
        
        # Try to find the task-specific policy in the JSON policy
        task_prompts = {
            "subject_description": "subject",
            "scene_composition_dynamics": "scene", 
            "subject_motion_dynamics": "motion",
            "spatial_framing_dynamics": "spatial",
            "camera_framing_dynamics": "camera",
            "color_composition_dynamics": "color",
            "lighting_setup_dynamics": "lighting",
            "lighting_effects_dynamics": "effects"
        }
        
        prompt_key = task_prompts.get(task, task)
        
        if prompt_key in self.json_policy:
            return self.json_policy[prompt_key]
        elif task in self.json_policy:
            return self.json_policy[task]
        else:
            return {}
    
    def get_default_prompt_template(self) -> str:
        """Get the default prompt template"""
        return """Please convert the following caption into the JSON format shown below:

{json_prompt}

Caption Instruction:
{caption_instruction}

Caption: {caption}

Instructions:
1. Use the exact same JSON keys as shown above
2. Preserve all important information from the caption
3. Organize the information appropriately under each key
4. If the caption doesn't contain some information, please review the caption instruction above to determine what should be the input
5. It is okay to leave fields blank as "" if nothing is mentioned in the caption
6. Return only valid JSON without any additional text"""
    
    def render_llm_testing_interface(self, selected_video: Dict[str, Any], selected_caption: Dict[str, Any]):
        """Render the LLM testing interface in the left column"""
        if not selected_video or not selected_caption:
            st.info("Please select a video and task to begin testing LLM prompts.")
            return
            
        st.subheader("🤖 LLM Caption Testing")
        
        # Add instructions
        with st.expander("📖 Instructions", expanded=False):
            st.markdown("""
            **How to use this interface:**
            1. **Select a video and task** from the sidebar
            2. **Review the final caption** that was approved by reviewers
            3. **Review the JSON structure** loaded from `json_policy/json_policy.json`
            4. **Review the caption instruction** that was used to create the original caption
            5. **Edit the prompt template** below - use `{json_prompt}`, `{caption_instruction}`, and `{caption}` placeholders
            6. **Choose an LLM model** and click "Generate JSON" to test the conversion
            7. **Iterate on the prompt** to improve the JSON output format
            
            The goal is to convert human-written captions into structured JSON format while preserving all important information.
            """)
        
        # Display final caption information
        st.write("### 📋 Final Caption")
        final_caption = selected_caption["final_caption"]
        annotator = selected_caption["annotator"]
        reviewer = selected_caption["reviewer"]
        timestamp = self.data_manager.format_timestamp(selected_caption["timestamp"])
        
        with st.container(border=True):
            st.write(f"**Annotator:** {annotator}")
            st.write(f"**Reviewer:** {reviewer}")
            st.write(f"**Completed:** {timestamp}")
            st.write("**Caption:**")
            st.write(final_caption)
        
        # Get task info
        task = selected_caption["task"]
        
        # Display JSON structure - make it span full width
        st.write("### 📋 Target JSON Structure")
        json_policy = self.get_json_policy_for_task(task)
        
        if json_policy:
            st.code(json.dumps(json_policy, indent=2), language="json")
        else:
            st.warning(f"No JSON policy found for task: {task}")
            st.info("Using default conversion prompt.")
        
        # Display caption instruction
        st.write("### 📋 Caption Instruction")
        caption_instruction = self.get_caption_instruction_for_task(task)
        with st.expander("View Caption Instruction", expanded=False):
            st.write(caption_instruction)
        
        # Prompt input section
        st.write("### ✏️ Prompt Template")
        
        # Load default prompt template
        default_prompt = self.get_default_prompt_template()
        
        prompt_template = st.text_area(
            "Edit the prompt template (use {json_prompt}, {caption_instruction}, {caption} placeholders):",
            value=default_prompt,
            height=250,
            key="prompt_template"
        )
        
        # LLM selection and generate button
        col1, col2 = st.columns(2)
        with col1:
            available_llms = get_all_llms()
            selected_llm = st.selectbox(
                "Select LLM:",
                available_llms,
                index=available_llms.index("gpt-4o-2024-08-06") if "gpt-4o-2024-08-06" in available_llms else 0,
                key="selected_llm"
            )
        
        with col2:
            generate_clicked = st.button("🚀 Generate JSON", type="primary", use_container_width=True)
        
        # Handle generation outside of columns to span full width
        if generate_clicked:
            if "{caption}" not in prompt_template:
                st.error("Prompt template must contain {caption} placeholder!")
            else:
                self.generate_json_caption(prompt_template, final_caption, selected_llm, json_policy, caption_instruction)
    
    def generate_json_caption(self, prompt_template: str, final_caption: str, selected_llm: str, json_policy: Dict[str, Any], caption_instruction: str):
        """Generate JSON version of caption using LLM"""
        try:
            # Prepare the JSON prompt part
            if json_policy:
                json_prompt = json.dumps(json_policy, indent=2)
            else:
                json_prompt = "Please use an appropriate JSON structure for this type of caption."
            
            # Prepare the final prompt by substituting placeholders
            final_prompt = prompt_template.format(
                json_prompt=json_prompt,
                caption_instruction=caption_instruction,
                caption=final_caption
            )
            
            with st.spinner(f"Generating JSON with {selected_llm}..."):
                # Get LLM instance
                llm = get_llm(model=selected_llm, secrets=st.secrets)
                
                # Generate response (text only)
                response = llm.generate(final_prompt)
                
                # Handle empty or whitespace-only responses
                if not response or not response.strip():
                    st.error("⚠️ LLM returned an empty response. Please try again or adjust the prompt.")
                    return
                
                # Clean the response - remove markdown formatting
                response = response.strip()
                
                # Remove markdown code block formatting if present
                if response.startswith('```json'):
                    response = response[7:]  # Remove ```json
                elif response.startswith('```'):
                    response = response[3:]   # Remove ```
                
                if response.endswith('```'):
                    response = response[:-3]  # Remove trailing ```
                
                response = response.strip()
                
                # Display results - now spans full width since it's outside columns
                st.write("### 📄 Generated JSON")
                
                # Try to parse as JSON for better formatting
                try:
                    parsed_json = json.loads(response)
                    # Display with 2-space indentation
                    st.code(json.dumps(parsed_json, indent=2), language="json")
                    st.success("✅ Valid JSON generated!")
                except json.JSONDecodeError as e:
                    # If not valid JSON, display as text
                    st.code(response, language="json")
                    st.error(f"⚠️ Response is not valid JSON format: {e}")
                    
                    # Additional debug info
                    st.info(f"Response length: {len(response)} characters")
                    if len(response) > 0:
                        st.info(f"First 50 chars: `{repr(response[:50])}`")
                
                # Store in session state for potential reuse
                if "generated_results" not in st.session_state:
                    st.session_state.generated_results = []
                
                st.session_state.generated_results.append({
                    "prompt": final_prompt,
                    "response": response,
                    "llm": selected_llm,
                    "timestamp": st.session_state.get("current_timestamp", "")
                })
                
        except KeyError as e:
            st.error(f"Missing placeholder in prompt template: {e}")
            st.info("Make sure your prompt template includes {json_prompt}, {caption_instruction}, and {caption} placeholders.")
        except Exception as e:
            st.error(f"Error generating JSON with {selected_llm}: {e}")
    
    def run(self):
        """Main application entry point"""
        st.set_page_config(
            page_title="LLM Caption Testing",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🤖 LLM Caption Testing Interface")
        st.markdown("Test different prompts for converting final captions to JSON format")
        
        # Get all reviewed videos
        reviewed_videos = self.get_all_reviewed_videos()
        
        # Render sidebar
        selected_video = self.render_video_selection_sidebar(reviewed_videos)
        selected_caption = self.render_task_selection_sidebar(selected_video)
        
        # Main content area - split into two columns
        left_col, right_col = st.columns([1, 1])
        
        with left_col:
            self.render_llm_testing_interface(selected_video, selected_caption)
        
        with right_col:
            self.render_video_display(selected_video)


if __name__ == "__main__":
    args = parse_args()
    app = LLMTestApp(args.config_type)
    app.run()