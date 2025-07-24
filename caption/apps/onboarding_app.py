import argparse
import streamlit as st
import os
from datetime import datetime
from pathlib import Path

# Import from the new structure
from caption.config import get_config
from caption.core import AuthManager, DataManager, VideoUtils, UIComponents, CaptionEngine
from caption.interfaces import CaptionInterface, ReviewInterface


def parse_args():
    """Parse command line arguments for the new annotator onboarding system"""
    parser = argparse.ArgumentParser(description="New Annotator Onboarding System")
    parser.add_argument("--config-type", type=str, default="main", 
                       choices=["main", "lighting"],
                       help="Configuration type to use")
    parser.add_argument(
        "--video_urls_files",
        nargs="+",
        type=str,
        default=["video_urls/new_annotator_exam/exam.json"],
        help="List of paths to test URLs files",
    )
    parser.add_argument("--output_new_annotator", type=str, default="output_onboarding/output_new_annotator", 
                       help="Path to the new annotator output directory")
    return parser.parse_args()


class OnboardingApp:
    """New Annotator Onboarding Application"""
    
    def __init__(self, config_type: str, video_urls_files: list, output_new_annotator: str):
        # Get base config and modify for new annotator use
        self.base_config = get_config(config_type)
        
        # Override specific settings for new annotator training
        self.base_config.video_urls_files = video_urls_files
        self.base_config.personalize_output = True
        
        self.output_new_annotator = output_new_annotator
        self.folder_path = Path(__file__).parent.parent  # Go up to caption/ directory
        
        # Initialize core components
        self.data_manager = DataManager(self.folder_path)
        self.auth_manager = AuthManager(self.data_manager)
        self.video_utils = VideoUtils()
        self.caption_engine = CaptionEngine(self.data_manager)
        self.ui = UIComponents()
        
        # Initialize interfaces
        self.caption_interface = CaptionInterface(self.data_manager, self.caption_engine)
        self.review_interface = ReviewInterface(self.data_manager)
    
    def run(self):
        """Main application entry point"""
        st.set_page_config(
            page_title="New Annotator Onboarding System",
            page_icon="🎓",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Check login status
        if not self.auth_manager.is_logged_in():
            self._show_login_page()
            return
        
        # Setup personalized output
        self._setup_personalized_output()
        
        # Check mode selection
        if "selected_portal_mode" not in st.session_state:
            self._show_mode_selection()
            return
        
        # Route to appropriate mode
        if st.session_state.selected_portal_mode == "caption":
            self._run_caption_mode()
        elif st.session_state.selected_portal_mode == "comparison":
            self._run_comparison_mode()
        else:
            if 'selected_portal_mode' in st.session_state:
                del st.session_state.selected_portal_mode
            st.rerun()
    
    def _show_login_page(self):
        """Show unified login page for new annotator system"""
        st.title("🎓 New Annotator Onboarding System")
        st.markdown(f"### Welcome to the {self.base_config.name} Onboarding")
        
        with st.form("new_annotator_login_form"):
            st.markdown("#### Login to access the onboarding system")
            
            # Import ANNOTATORS from auth module
            from caption.core.auth import ANNOTATORS
            
            # Annotator selection dropdown
            selected_annotator = st.selectbox(
                "Select Your Name:",
                list(ANNOTATORS.keys()),
                key="selected_annotator",
                index=None,
                placeholder="Type or select your name...",
            )
            
            # Password input
            password = st.text_input("Enter Password:", type="password", key="password_input")
            
            # File selection dropdown
            selected_file = st.selectbox(
                "Select Training Video Set:", 
                self.base_config.video_urls_files, 
                key="selected_urls_file",
                format_func=lambda x: f"📋 {os.path.basename(x)}"
            )

            submit_button = st.form_submit_button("🚀 Login", use_container_width=True)

            if submit_button:
                if selected_annotator and password == ANNOTATORS[selected_annotator]["password"]:
                    # Load video URLs and store in session state
                    video_urls = self.data_manager.load_json(selected_file)
                    st.session_state.video_urls = video_urls
                    st.session_state.logged_in = True
                    st.session_state.logged_in_user = selected_annotator
                    st.session_state.selected_portal_file = selected_file
                    # Set portal mode flag so other components know it's running in portal mode
                    st.session_state.selected_portal = True
                    st.success(f"Login successful! Welcome to training, {selected_annotator}!")
                    st.rerun()
                else:
                    st.error("Incorrect password or missing name. Please try again.")
    
    def _show_mode_selection(self):
        """Show mode selection page after login"""
        st.title("🎯 Select Training Mode")
        st.markdown(f"### Welcome, **{st.session_state.logged_in_user}**!")
        st.markdown("Choose your training activity:")
        
        st.markdown("---")
        
        # Create two columns for mode selection
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("### 📝 Caption Creation Mode")
            st.markdown("""
            **Practice Creating Captions**
            - Generate AI-powered pre-captions
            - Provide feedback to refine captions
            - Submit final captions for review
            
            *Use this mode to practice and create your caption submissions.*
            """)
            if st.button("🚀 Start Caption Training", key="caption_mode", use_container_width=True):
                st.session_state.selected_portal_mode = "caption"
                self._clear_mode_state()
                st.rerun()
        
        with col2:
            st.markdown("### 🔍 Comparison Mode")
            st.markdown("""
            **Compare Your Work with Ground Truth**
            - View differences between your captions and ground truth versions
            - Compare feedback and ratings
            - Learn from ground truth annotations
            
            *Use this mode to review and learn from your submissions.*
            """)
            if st.button("🔍 Compare with Ground Truth", key="comparison_mode", use_container_width=True):
                st.session_state.selected_portal_mode = "comparison"
                self._clear_mode_state()
                st.rerun()
        
        st.markdown("---")
        
        # Logout option
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    def _setup_personalized_output(self):
        """Setup personalized output directory"""
        if self.base_config.personalize_output and "logged_in_user" in st.session_state:
            if "personalized_output" not in st.session_state:
                username = self.video_utils.convert_name_to_username(st.session_state.logged_in_user)
                st.session_state.personalized_output = f"{self.output_new_annotator}_{username}"
                print(f"Personalized output directory: {st.session_state.personalized_output}")
                
                # Copy feedback files from main project for precaption
                self.caption_engine.copy_feedback_for_precaption(
                    self.base_config.configs_file,
                    st.session_state.video_urls,
                    self.base_config.main_project_output,
                    st.session_state.personalized_output
                )
            
            self.output_new_annotator = st.session_state.personalized_output
    
    def _run_caption_mode(self):
        """Run caption creation mode"""
        # Add mode navigation
        self._add_mode_navigation_sidebar("caption")
        
        # Prepare config for caption creation
        caption_config = self.base_config
        caption_config.output_dir = self.output_new_annotator
        
        # Load video data
        video_data_dict = self.data_manager.load_video_data(
            self.base_config.video_data_file, 
            self.base_config.label_collections
        )
        
        # File check
        if "file_check_passed_caption" not in st.session_state:
            if self.video_utils.file_check(st.session_state.video_urls, video_data_dict, self.data_manager):
                st.session_state.file_check_passed_caption = True
            else:
                return
        
        # Create two columns
        page_col1, page_col2 = st.columns([1, 1])
        
        with page_col1:
            self._render_caption_sidebar(video_data_dict, caption_config)
        
        with page_col2:
            self._render_caption_main_interface(video_data_dict, caption_config)
    
    def _run_comparison_mode(self):
        """Run comparison mode"""
        # Add mode navigation
        self._add_mode_navigation_sidebar("comparison")
        
        # Load video data
        video_data_dict = self.data_manager.load_video_data(
            self.base_config.video_data_file, 
            self.base_config.label_collections
        )
        
        # File check
        if "file_check_passed_comparison" not in st.session_state:
            if self.video_utils.file_check(st.session_state.video_urls, video_data_dict, self.data_manager):
                st.session_state.file_check_passed_comparison = True
            else:
                return
        
        # Create two columns
        page_col1, page_col2 = st.columns([1, 1])
        
        with page_col1:
            self._render_comparison_sidebar(video_data_dict)
        
        with page_col2:
            self._render_comparison_main_interface(video_data_dict)
    
    def _render_caption_sidebar(self, video_data_dict: dict, caption_config):
        """Render caption mode sidebar"""
        # Load configs
        try:
            configs = self.data_manager.load_config(self.base_config.configs_file)
            configs = [self.data_manager.load_config(config) for config in configs]
        except FileNotFoundError:
            st.error(f"Config file not found: {self.base_config.configs_file}")
            return
        
        config_dict = {config["name"]: config for config in configs}
        config_names = list(config_dict.keys())
        
        # Task selection
        selected_config = st.selectbox(
            "Select a task:",
            config_names,
            index=config_names.index(st.session_state.get('last_config_id_caption', config_names[0])),
            key="selected_task_caption",
        )
        
        # Handle config changes
        self._handle_config_change_caption(selected_config)
        
        config = config_dict[selected_config]
        st.markdown(f"### {config.get('name', 'Caption Training')}")
        
        # Get video URLs and output directory
        video_urls = st.session_state.video_urls
        output_dir = str(self.folder_path / self.output_new_annotator / config["output_name"])
        
        # Display instructions
        self._display_instructions(config)
        
        # Video selection
        selected_video = st.selectbox(
            "Select a video:",
            video_urls,
            format_func=self.video_utils.get_video_format_func(output_dir, video_urls, self.data_manager),
            index=video_urls.index(st.session_state.get('last_selected_video_caption', video_urls[0])),
            key="selected_video_caption"
        )
        
        # Handle video changes
        video_id = self.data_manager.get_video_id(selected_video)
        self._handle_video_change_caption(video_id, selected_video)
        
        # Display video and related info
        self.video_utils.display_video_with_frames(selected_video)
        self.video_utils.display_video_links(video_id, video_data_dict)
        
        # Navigation buttons
        preserved_keys = [
            'api_key', 'last_config_id_caption', 'last_video_id_caption', 'last_selected_video_caption',
            'file_check_passed_caption', 'logged_in', 'video_urls', 'logged_in_user', 
            'selected_portal_mode', 'selected_portal_file', 'personalized_output',
            'selected_portal', 'login_method', 'target_annotator'
        ]
        
        self.ui.display_navigation_buttons(
            video_urls, config_names, selected_video, selected_config, 
            preserved_keys, self.data_manager
        )
        
        # Store current selections
        st.session_state.current_config_caption = config
        st.session_state.current_config_dict_caption = config_dict
        st.session_state.current_selected_config_caption = selected_config
        st.session_state.current_output_dir_caption = output_dir
        st.session_state.current_video_id_caption = video_id
        st.session_state.current_selected_video_caption = selected_video
    
    def _render_caption_main_interface(self, video_data_dict: dict, caption_config):
        """Render caption mode main interface"""
        if not hasattr(st.session_state, 'current_config_caption'):
            return
        
        # Session state initialization
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 0
        if 'precaption_data' not in st.session_state:
            st.session_state.precaption = {}
        if 'feedback_data' not in st.session_state:
            st.session_state.feedback_data = {}
        
        # Call the caption interface
        self.caption_interface.render_feedback_interface(
            video_id=st.session_state.current_video_id_caption,
            config=st.session_state.current_config_caption,
            output_dir=st.session_state.current_output_dir_caption,
            caption_program=self.base_config.caption_programs[st.session_state.current_config_caption["task"]],
            video_data_dict=video_data_dict,
            selected_video=st.session_state.current_selected_video_caption,
            args=caption_config,
            selected_config=st.session_state.current_selected_config_caption,
            config_dict=st.session_state.current_config_dict_caption
        )
    
    def _render_comparison_sidebar(self, video_data_dict: dict):
        """Render comparison mode sidebar"""
        # Load configs
        try:
            configs = self.data_manager.load_config(self.base_config.configs_file)
            configs = [self.data_manager.load_config(config) for config in configs]
        except FileNotFoundError:
            st.error(f"Config file not found: {self.base_config.configs_file}")
            return
        
        config_dict = {config["name"]: config for config in configs}
        config_names = list(config_dict.keys())
        
        # Task selection
        selected_config = st.selectbox(
            "Select a task:",
            config_names,
            index=config_names.index(st.session_state.get('last_config_id_comparison', config_names[0])),
            key="selected_task_comparison",
        )
        
        # Handle config changes
        self._handle_config_change_comparison(selected_config)
        
        config = config_dict[selected_config]
        st.title(f"Caption Comparison - {config.get('name', '')}")
        
        # Get directories
        video_urls = st.session_state.video_urls
        output_dir = str(self.folder_path / self.base_config.output_dir / config["output_name"])
        new_annotator_output_dir = str(self.folder_path / self.output_new_annotator / config["output_name"])
        
        # Video selection with comparison format
        selected_video = st.selectbox(
            "Select a video:",
            video_urls,
            format_func=self._get_comparison_video_format_func(output_dir, new_annotator_output_dir, video_urls),
            index=video_urls.index(st.session_state.get('last_selected_video_comparison', video_urls[0])),
            key="selected_video_comparison"
        )
        
        # Handle video changes
        video_id = self.data_manager.get_video_id(selected_video)
        self._handle_video_change_comparison(video_id, selected_video)
        
        # Display video and related info
        self.video_utils.display_video_with_frames(selected_video)
        self.video_utils.display_video_links(video_id, video_data_dict)
        
        # Navigation buttons
        preserved_keys = [
            'api_key', 'last_config_id_comparison', 'last_video_id_comparison', 'last_selected_video_comparison', 
            'file_check_passed_comparison', 'logged_in', 'video_urls', 'logged_in_user', 
            'selected_portal_mode', 'selected_portal_file', 'personalized_output',
            'selected_portal', 'login_method', 'target_annotator'
        ]
        
        self.ui.display_navigation_buttons(
            video_urls, config_names, selected_video, selected_config, 
            preserved_keys, self.data_manager
        )
        
        # Store current selections
        st.session_state.current_config_comparison = config
        st.session_state.current_output_dir_comparison = output_dir
        st.session_state.current_new_annotator_output_dir_comparison = new_annotator_output_dir
        st.session_state.current_video_id_comparison = video_id
    
    def _render_comparison_main_interface(self, video_data_dict: dict):
        """Render comparison mode main interface"""
        if not hasattr(st.session_state, 'current_config_comparison'):
            return
        
        with st.container(height=930, border=True):
            video_id = st.session_state.current_video_id_comparison
            output_dir = st.session_state.current_output_dir_comparison
            new_annotator_output_dir = st.session_state.current_new_annotator_output_dir_comparison
            
            status, current_file, new_annotator_file, current_user, new_annotator_user = self._get_comparison_video_status(
                video_id, output_dir, new_annotator_output_dir
            )
            
            if status == "not_done":
                st.warning("⚠️ No ground truth available for this video.")
            elif status == "not_done_by_new_annotator":
                st.info("📝 You haven't created a caption for this video yet. Switch to Caption Mode to create one!")
            else:  # done_by_new_annotator
                self._render_comparison_results(video_id, output_dir, new_annotator_output_dir, 
                                              current_user, new_annotator_user)
    
    def _render_comparison_results(self, video_id: str, output_dir: str, new_annotator_output_dir: str,
                                 current_user: str, new_annotator_user: str):
        """Render comparison results"""
        # Load both current and new annotator captions
        current_data = self.data_manager.load_data(video_id, output_dir, self.data_manager.FEEDBACK_FILE_POSTFIX)
        new_annotator_data = self.data_manager.load_data(video_id, new_annotator_output_dir, self.data_manager.FEEDBACK_FILE_POSTFIX)
        
        st.subheader("📊 Caption Comparison Results")
        
        # Display metadata information
        current_timestamp = self._format_timestamp(current_data.get("timestamp", "Unknown"))
        new_annotator_timestamp = self._format_timestamp(new_annotator_data.get("timestamp", "Unknown"))
        
        # Create info boxes
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**📚 Ground Truth**\nBy {current_user}\n{current_timestamp}")
        with col2:
            st.success(f"**👤 Your Version**\nBy {new_annotator_user}\n{new_annotator_timestamp}")
        
        # Create tabs for viewing captions
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔄 Feedback Differences", 
            "📝 Caption Differences", 
            "📚 Ground Truth", 
            "👤 Your Version"
        ])
        
        with tab1:
            st.subheader("Feedback Comparison")
            st.markdown("*Compare your feedback approach with the expert's feedback.*")
            self.review_interface.display_feedback_differences(
                prev_feedback=new_annotator_data,
                feedback_data=current_data,
                diff_prompt=self.base_config.diff_prompt
            )
        
        with tab2:
            st.subheader("Caption Comparison")
            st.markdown("*See the differences between your final caption and the expert's caption.*")
            self.review_interface.display_caption_differences(
                prev_feedback=new_annotator_data,
                feedback_data=current_data,
                diff_prompt=self.base_config.diff_cap_prompt
            )
        
        with tab3:
            st.subheader("📚 Ground Truth Version")
            st.markdown("*Expert annotation for reference and learning.*")
            st.write(f"**Expert:** {current_user}")
            st.write(f"**Created:** {self._format_timestamp(current_data.get('timestamp', ''))}")
            self.ui.display_feedback_info(current_data, display_pre_caption_instead_of_final_caption=False)
        
        with tab4:
            st.subheader("👤 Your Version")
            st.markdown("*Your annotation work for comparison.*")
            st.write(f"**Annotator:** {new_annotator_user}")
            st.write(f"**Created:** {self._format_timestamp(new_annotator_data.get('timestamp', ''))}")
            self.ui.display_feedback_info(new_annotator_data, display_pre_caption_instead_of_final_caption=True)
    
    def _get_comparison_video_status(self, video_id: str, output_dir: str, new_annotator_output_dir: str):
        """Get the status of a video's caption completion for comparison"""
        current_file = self.data_manager.get_filename(video_id, output_dir, self.data_manager.FEEDBACK_FILE_POSTFIX)
        new_annotator_file = self.data_manager.get_filename(video_id, new_annotator_output_dir, self.data_manager.FEEDBACK_FILE_POSTFIX)
        
        if not os.path.exists(current_file):
            return "not_done", None, None, None, None
        elif not os.path.exists(new_annotator_file):
            return "not_done_by_new_annotator", current_file, None, None, None
        else:
            # Load both current and new annotator data to check users
            current_data = self.data_manager.load_data(video_id, output_dir, self.data_manager.FEEDBACK_FILE_POSTFIX)
            new_annotator_data = self.data_manager.load_data(video_id, new_annotator_output_dir, self.data_manager.FEEDBACK_FILE_POSTFIX)
            
            current_user = current_data.get("user", "Unknown")
            new_annotator_user = new_annotator_data.get("user", "Unknown")
            
            return "done_by_new_annotator", current_file, new_annotator_file, current_user, new_annotator_user
    
    def _get_comparison_video_format_func(self, output_dir: str, new_annotator_output_dir: str, video_urls: list):
        """Format function for video selection dropdown with status emojis for comparison mode"""
        def format_func(video_url: str) -> str:
            video_index = video_urls.index(video_url) + 1
            video_id = self.data_manager.get_video_id(video_url)
            status, _, _, _, _ = self._get_comparison_video_status(video_id, output_dir, new_annotator_output_dir)
            
            emoji_map = {
                "not_done": "❓",  # for not completed
                "not_done_by_new_annotator": "⏳",  # hourglass for completed but not by new annotator
                "done_by_new_annotator": "✅"  # for done by new annotator
            }
            
            emoji = emoji_map[status]
            return f"{emoji}{video_index}. {video_url.split('/')[-1]}"
        
        return format_func
    
    def _add_mode_navigation_sidebar(self, current_mode: str):
        """Add consistent mode navigation to sidebar"""
        with st.sidebar:
            if current_mode == "caption":
                st.title("📝 Caption Training")
            else:
                st.title("🔍 Comparison Mode")
                
            st.write(f"**User:** {st.session_state.logged_in_user}")
            
            if self.base_config.personalize_output:
                st.write(f"**Your Output:** {self.output_new_annotator}")
            
            st.markdown("---")
            
            # Mode switching
            if current_mode == "caption":
                if st.button("🔄 Switch to Comparison Mode"):
                    st.session_state.selected_portal_mode = "comparison"
                    self._clear_mode_state()
                    st.rerun()
            else:
                if st.button("🔄 Switch to Caption Mode"):
                    st.session_state.selected_portal_mode = "caption"
                    self._clear_mode_state()
                    st.rerun()
            
            if st.button("🏠 Back to Mode Selection"):
                if 'selected_portal_mode' in st.session_state:
                    del st.session_state.selected_portal_mode
                self._clear_mode_state()
                st.rerun()
            
            if st.button("🚪 Logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    def _clear_mode_state(self):
        """Clear mode-specific state while preserving login and navigation state"""
        preserve_keys = {
            'logged_in', 'logged_in_user', 'video_urls', 'selected_portal_file',
            'selected_portal_mode', 'file_check_passed_caption', 'file_check_passed_comparison', 
            'personalized_output', 'selected_portal', 'login_method', 'target_annotator'
        }
        
        keys_to_clear = [k for k in st.session_state.keys() if k not in preserve_keys]
        for key in keys_to_clear:
            del st.session_state[key]
    
    def _display_instructions(self, config: dict):
        """Display task instructions"""
        with st.expander("📜 Caption Instructions (Click to Expand/Collapse)", expanded=False):
            if "instruction_file" not in config:
                st.warning("No instruction_file found in the configuration file.")
            else:
                instruction_text = self.ui.load_txt(str(self.folder_path / config["instruction_file"]))
                st.write(instruction_text)
    
    def _format_timestamp(self, iso_timestamp: str) -> str:
        """Format ISO timestamp to a more readable format"""
        try:
            dt = datetime.fromisoformat(iso_timestamp)
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return iso_timestamp
    
    def _handle_config_change_caption(self, selected_config: str):
        """Handle configuration changes for caption mode"""
        if 'last_config_id_caption' not in st.session_state:
            st.session_state.last_config_id_caption = selected_config
        elif st.session_state.last_config_id_caption != selected_config:
            # Clear relevant state on config change
            keys_to_remove = [key for key in st.session_state 
                             if key.endswith('_caption') and key not in ['last_config_id_caption']]
            for key in keys_to_remove:
                del st.session_state[key]
            st.session_state.last_config_id_caption = selected_config
            st.rerun()
    
    def _handle_config_change_comparison(self, selected_config: str):
        """Handle configuration changes for comparison mode"""
        if 'last_config_id_comparison' not in st.session_state:
            st.session_state.last_config_id_comparison = selected_config
        elif st.session_state.last_config_id_comparison != selected_config:
            # Clear relevant state on config change  
            keys_to_remove = [key for key in st.session_state 
                             if key.endswith('_comparison') and key not in ['last_config_id_comparison']]
            for key in keys_to_remove:
                del st.session_state[key]
            st.session_state.last_config_id_comparison = selected_config
            st.rerun()
    
    def _handle_video_change_caption(self, video_id: str, selected_video: str):
        """Handle video changes for caption mode"""
        if 'last_video_id_caption' not in st.session_state:
            st.session_state.last_video_id_caption = video_id
            st.session_state.last_selected_video_caption = selected_video
        elif st.session_state.last_video_id_caption != video_id:
            # Clear relevant state on video change
            keys_to_remove = [key for key in st.session_state 
                             if key.endswith('_caption') and key not in ['last_config_id_caption', 'last_video_id_caption', 'last_selected_video_caption']]
            for key in keys_to_remove:
                del st.session_state[key]
            st.session_state.last_video_id_caption = video_id
            st.session_state.last_selected_video_caption = selected_video
            st.rerun()
    
    def _handle_video_change_comparison(self, video_id: str, selected_video: str):
        """Handle video changes for comparison mode"""
        if 'last_video_id_comparison' not in st.session_state:
            st.session_state.last_video_id_comparison = video_id
            st.session_state.last_selected_video_comparison = selected_video
        elif st.session_state.last_video_id_comparison != video_id:
            # Clear relevant state on video change
            keys_to_remove = [key for key in st.session_state 
                             if key.endswith('_comparison') and key not in ['last_config_id_comparison', 'last_video_id_comparison', 'last_selected_video_comparison']]
            for key in keys_to_remove:
                del st.session_state[key]
            st.session_state.last_video_id_comparison = video_id
            st.session_state.last_selected_video_comparison = selected_video
            st.rerun()


def main():
    """Main entry point"""
    args = parse_args()
    app = OnboardingApp(args.config_type, args.video_urls_files, args.output_new_annotator)
    app.run()


if __name__ == "__main__":
    main()