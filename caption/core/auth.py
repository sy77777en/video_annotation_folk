# caption/core/auth.py
import streamlit as st
import os
import json
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from caption.core.data_manager import DataManager


def load_annotators_from_files(input_dir="annotator") -> Dict[str, Dict[str, str]]:
    """Load annotators from individual JSON files.
    
    Args:
        input_dir: Directory containing the JSON files
        
    Returns:
        Dictionary of annotators with their passwords
    """
    annotators = {}
    
    # Check if directory exists
    if not os.path.exists(input_dir):
        print(f"Warning: Annotator directory {input_dir} does not exist")
        return annotators
    
    # Load each JSON file
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    annotators.update(data)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
    
    return annotators


# Load annotators from files
ANNOTATORS = load_annotators_from_files()
APPROVED_REVIEWERS = [
    "Zhiqiu Lin", "Siyuan Cen", "Yuhan Huang", "Hewei Wang", 
    "Tiffany Ling", "Isaac Li", "Shihang Zhu"
]

# Ensure all approved reviewers are in annotators dictionary
assert set(APPROVED_REVIEWERS) <= set(ANNOTATORS.keys()), \
    "All approved reviewers must be in the ANNOTATORS dictionary"


class AuthManager:
    """Handles authentication and login logic"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def show_login_page(self, app_config):
        """Unified login page for both portals"""
        st.title("🎥 Video Caption and Review System")
        st.markdown(f"### Welcome to the {app_config.name}")
        
        # Create tabs for different login methods
        tab1, tab2, tab3 = st.tabs(["📋 Login by Sheet", "👤 Login by Annotator", "📋 Job Assignment"])

        with tab1:
            self._render_sheet_login_tab(app_config)
        
        with tab2:
            self._render_annotator_login_tab(app_config)
            
        with tab3:
            self._render_job_assignment_tab()
    
    def _render_sheet_login_tab(self, app_config):
        """Render the sheet-based login tab"""
        with st.form("login_form_sheet"):
            st.markdown("#### Login to access video sheets")
            
            # Annotator selection dropdown
            selected_annotator = st.selectbox(
                "Select Your Name:",
                list(ANNOTATORS.keys()),
                key="selected_annotator_sheet",
                index=None,
                placeholder="Type or select your name...",
            )
            
            # Password input
            password = st.text_input("Enter Password:", type="password", key="password_input_sheet")
            
            # File selection dropdown with completion status
            try:
                configs = self.data_manager.load_config(app_config.configs_file)
                configs = [self.data_manager.load_config(config) for config in configs]
                
                # Check completion status for each file
                start_time = time.time()
                file_status = {}
                for video_urls_file in app_config.video_urls_files:
                    status_dict, annotators_dict, reviewers_dict = self.data_manager.check_video_completion_status(
                        video_urls_file, configs, app_config.output_dir
                    )
                    
                    # Count completed and reviewed videos
                    completed = sum(1 for _, (is_completed, _) in status_dict.items() if is_completed)
                    reviewed = sum(1 for _, (_, is_reviewed) in status_dict.items() if is_reviewed)
                    total = len(status_dict)
                    
                    # Format annotator and reviewer info
                    annotator_str = ", ".join([f"{annotator} ({count})" for annotator, count in annotators_dict.items()])
                    reviewer_str = ", ".join([f"{reviewer} ({count})" for reviewer, count in reviewers_dict.items()])
                    
                    # Create status string
                    if completed == total and reviewed == total:
                        status = "✅✅"
                    elif completed == total:
                        status = "✅"
                    else:
                        status = ""
                    
                    file_status[video_urls_file] = (
                        f"{status} {os.path.basename(video_urls_file)} "
                        f"({completed}/{total} completed, {reviewed}/{total} reviewed) "
                        f"(Annotators: {annotator_str}, Reviewers: {reviewer_str})"
                    )
                
                end_time = time.time()
                print(f"Completion status check took {end_time - start_time:.2f} seconds")
                
                # Create format function for selectbox
                def format_file_with_status(file_path):
                    return file_status.get(file_path, file_path)
                
                selected_file = st.selectbox(
                    "Select Video URLs File:",
                    app_config.video_urls_files,
                    key="selected_urls_file_sheet",
                    format_func=format_file_with_status
                )
            except Exception as e:
                st.error(f"Error checking completion status: {e}")
                selected_file = st.selectbox(
                    "Select Video URLs File:",
                    app_config.video_urls_files,
                    key="selected_urls_file_sheet"
                )

            submit_button = st.form_submit_button("🚀 Login", use_container_width=True)

            if submit_button:
                if selected_annotator and password == ANNOTATORS[selected_annotator]["password"]:
                    # Store the video URLs and annotator in session state
                    st.session_state.video_urls = self.data_manager.load_json(selected_file)
                    st.session_state.logged_in = True
                    st.session_state.logged_in_user = selected_annotator
                    st.session_state.login_method = "sheet"
                    st.success(f"Login successful! Welcome, {selected_annotator}!")
                    st.rerun()
                else:
                    st.error("Incorrect password or missing name. Please try again.")
    
    def _render_annotator_login_tab(self, app_config):
        """Render the annotator-based login tab"""
        with st.form("login_form_annotator"):
            st.markdown("#### Search for specific annotator's videos")
            
            # Annotator selection dropdown for login
            selected_annotator = st.selectbox(
                "Select Your Name:",
                list(ANNOTATORS.keys()),
                key="selected_annotator_annotator",
                index=None,
                placeholder="Type or select your name...",
            )
            
            # Password input
            password = st.text_input("Enter Password:", type="password", key="password_input_annotator")
            
            # Dropdown to select which annotator's videos to search for
            target_annotator = st.selectbox(
                "Search for videos completed by:",
                list(ANNOTATORS.keys()),
                key="target_annotator_select",
                index=None,
                placeholder="Type or select annotator name...",
            )
            
            # Options for filtering
            col1, col2 = st.columns(2)
            with col1:
                not_yet_reviewed = st.checkbox(
                    "Show only videos not yet reviewed",
                    value=True,
                    key="not_yet_reviewed"
                )
            with col2:
                show_only_rejected = st.checkbox(
                    "Show only rejected videos",
                    value=False,
                    key="show_only_rejected"
                )

            submit_button = st.form_submit_button("🔍 Search & Login", use_container_width=True)

            if submit_button:
                if selected_annotator and password == ANNOTATORS[selected_annotator]["password"]:
                    try:
                        configs = self.data_manager.load_config(app_config.configs_file)
                        configs = [self.data_manager.load_config(config) for config in configs]
                        
                        # Get annotator videos
                        start_time = time.time()
                        matching_videos = self.data_manager.get_annotator_videos(
                            target_annotator, configs, app_config.output_dir,
                            not_yet_reviewed, show_only_rejected
                        )
                        end_time = time.time()
                        print(f"Getting annotator videos took {end_time - start_time:.2f} seconds")
                        
                        if not matching_videos:
                            st.error(f"No matching videos found for annotator {target_annotator}.")
                        else:
                            st.session_state.video_urls = matching_videos
                            st.session_state.logged_in = True
                            st.session_state.logged_in_user = selected_annotator
                            st.session_state.login_method = "annotator"
                            st.session_state.target_annotator = target_annotator
                            st.success(f"Login successful! Welcome, {selected_annotator}! "
                                     f"Found {len(matching_videos)} matching videos for {target_annotator}.")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error getting annotator videos: {e}")
                else:
                    st.error("Incorrect password or missing name. Please try again.")
    
    def _render_job_assignment_tab(self):
        """Render the job assignment tab"""
        st.markdown("#### Job Assignment Spreadsheet")
        st.markdown("Access the master job assignment spreadsheet to view task allocations and progress.")
        
        st.link_button(
            "📋 **Open Job Assignment Spreadsheet**", 
            "https://docs.google.com/spreadsheets/d/10g-ynle9VCDrCcDCxEfBafVRdbOAckzl0y6S-J22kDY/edit?gid=0#gid=0",
            use_container_width=True,
            type="primary"
        )
        
        st.markdown("---")
        st.info("💡 This spreadsheet contains task assignments, deadlines, and progress tracking for all team members.")
    
    @staticmethod
    def is_logged_in() -> bool:
        """Check if user is logged in"""
        return st.session_state.get('logged_in', False)
    
    @staticmethod
    def get_current_user() -> Optional[str]:
        """Get current logged in user"""
        return st.session_state.get('logged_in_user')
    
    @staticmethod
    def logout():
        """Clear all session state and logout"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    @staticmethod
    def can_annotator_redo(video_id: str, output_dir: str, current_user: str, data_manager: DataManager) -> bool:
        """Check if the current user (as annotator) can redo the caption"""
        annotator, reviewer = data_manager.get_annotator_and_reviewer(video_id, output_dir)
        
        # If no annotator yet, anyone can be the annotator
        if not annotator:
            return True
        
        # If same annotator, check if it's been reviewed
        if annotator == current_user:
            reviewer_data = data_manager.load_data(video_id, output_dir, "_review.json")
            return not reviewer_data  # Can redo if not reviewed yet
        
        return False
    
    @staticmethod
    def can_reviewer_redo(video_id: str, output_dir: str, current_user: str, data_manager: DataManager) -> bool:
        """Check if the current user (as reviewer) can redo the caption"""
        annotator, reviewer = data_manager.get_annotator_and_reviewer(video_id, output_dir)
        
        # Must be an approved reviewer
        if current_user not in APPROVED_REVIEWERS:
            return False
        
        # Cannot review if you're the annotator
        if annotator == current_user:
            return False
        
        return True