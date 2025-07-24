# caption/interfaces/review_interface.py
import streamlit as st
from typing import Dict, Any, List, Optional
from pathlib import Path

from caption.core.data_manager import DataManager
from caption.core.ui_components import UIComponents


class ReviewInterface:
    """Review and comparison interface"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.ui = UIComponents()
    
    def render_review_interface(self, video_id: str, config: Dict[str, Any], 
                               output_dir: str, **kwargs):
        """Main review interface"""
        with st.container(height=self.ui.CONTAINER_HEIGHT, border=True):
            status, current_file, prev_file, current_user, prev_user = self.data_manager.get_video_status(
                video_id, output_dir
            )
            
            if status == "not_completed":
                st.warning("Please complete this caption first.")
            elif status == "completed_not_reviewed":
                st.info("The caption has been completed but not reviewed yet.")
            elif status == "approved":
                self._render_approved_caption(video_id, output_dir, current_user, current_file)
            else:  # rejected
                self._render_rejected_caption(video_id, output_dir, current_user, prev_user, 
                                            current_file, prev_file, kwargs.get('args'))
    
    def _render_approved_caption(self, video_id: str, output_dir: str, current_user: str, current_file: str):
        """Render approved caption view"""
        current_data = self.data_manager.load_data(video_id, output_dir, self.data_manager.FEEDBACK_FILE_POSTFIX)
        st.success("✅ This caption has been approved! Great job!")
        st.write("**Current Version:**")
        self._display_caption_expander(current_data, current_user, current_data.get("timestamp", "Unknown"))
    
    def _render_rejected_caption(self, video_id: str, output_dir: str, current_user: str, prev_user: str,
                               current_file: str, prev_file: str, args: Any):
        """Render rejected caption view with comparisons"""
        # Load both current and previous captions
        current_data = self.data_manager.load_data(video_id, output_dir, self.data_manager.FEEDBACK_FILE_POSTFIX)
        prev_data = self.data_manager.load_data(video_id, output_dir, self.data_manager.PREV_FEEDBACK_FILE_POSTFIX)
        reviewer_data = self.data_manager.load_data(video_id, output_dir, self.data_manager.REVIEWER_FILE_POSTFIX)
        
        st.subheader("Caption Changes")
        
        # Display metadata information
        current_timestamp = self.data_manager.format_timestamp(current_data.get("timestamp", "Unknown"))
        prev_timestamp = self.data_manager.format_timestamp(prev_data.get("timestamp", "Unknown"))
        
        st.write(f"**Current Version:** By {current_user} on {current_timestamp}")
        st.write(f"**Previous Version:** By {prev_user} on {prev_timestamp}")
        
        st.warning("❌ This caption was rejected and needs to be fixed.")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            "Feedback Differences", "Caption Differences", "Previous Version", "Current Version"
        ])
        
        with tab1:
            st.subheader("Feedback Differences")
            self.display_feedback_differences(
                prev_feedback=prev_data,
                feedback_data=current_data,
                diff_prompt=args.diff_prompt if args else None,
                reviewer_data=reviewer_data
            )
            
        with tab2:
            st.subheader("Caption Differences")
            self.display_caption_differences(
                prev_feedback=prev_data,
                feedback_data=current_data,
                diff_prompt=args.diff_cap_prompt if args else None,
                reviewer_data=reviewer_data
            )
            
        with tab3:
            st.subheader("Previous Version")
            self._display_caption_expander(prev_data, prev_user, prev_data.get('timestamp', ''))
            
        with tab4:
            st.subheader("Current Version")
            self._display_caption_expander(current_data, current_user, current_data.get('timestamp', ''))
    
    def _display_caption_expander(self, data: Dict[str, Any], user: str, timestamp: str):
        """Helper function to display caption information"""
        st.write("##### Annotator")
        st.write(f"**Annotator:** {user}")
        st.write(f"**Timestamp:** {self.data_manager.format_timestamp(timestamp)}")
        st.write("##### Pre-caption")
        st.write(data.get("pre_caption", "No pre-caption available"))
        
        # Use the existing display_feedback_info function
        self.ui.display_feedback_info(data, display_pre_caption_instead_of_final_caption=False)
    
    def display_accuracy_statistics(self, config_names: List[str], config_dict: Dict[str, Any], 
                                   video_urls: List[str], output_dir: str):
        """Display accuracy statistics for all configs in an expander"""
        with st.expander("📊 Accuracy Statistics", expanded=False):
            # Calculate stats for all configs
            all_stats = {}
            for config_name in config_names:
                config = config_dict[config_name]
                config_output_dir = str(Path(output_dir) / config["output_name"])
                if not Path(config_output_dir).exists():
                    continue
                stats = self._calculate_accuracy_stats(video_urls, config_output_dir)
                if stats:
                    all_stats[config_name] = stats
            
            if not all_stats:
                st.info("No completed videos found for any task.")
            else:
                # Create tabs for each task
                task_tabs = st.tabs([self.ui.config_names_to_short_names[config_name] 
                                   for config_name in all_stats.keys()])
                
                # Add content to each tab
                for tab, (config_name, stats) in zip(task_tabs, all_stats.items()):
                    with tab:
                        self._render_accuracy_table(stats)
    
    def _calculate_accuracy_stats(self, video_urls: List[str], output_dir: str) -> Dict[str, Dict[str, Any]]:
        """Calculate accuracy statistics for all videos in the given directory"""
        stats = {}
        
        for video_url in video_urls:
            video_id = self.data_manager.get_video_id(video_url)
            status, _, prev_file, current_user, prev_user = self.data_manager.get_video_status(video_id, output_dir)
            
            # Skip if not completed
            if status == "not_completed":
                continue
                
            # Determine the annotator (original caption creator)
            annotator = prev_user if prev_file else current_user
            if annotator is None:
                print(f"annotator is None for video {video_id}")
                continue
                
            # Initialize annotator stats if not exists
            if annotator not in stats:
                stats[annotator] = {
                    'total_completed': 0,
                    'total_reviewed': 0,
                    'approved': 0,
                    'rejected': 0,
                    'accuracy': 0.0
                }
            
            # Update total completed
            stats[annotator]['total_completed'] += 1
            
            # Update reviewed stats if applicable
            if status in ["approved", "rejected"]:
                stats[annotator]['total_reviewed'] += 1
                if status == "approved":
                    stats[annotator]['approved'] += 1
                else:  # rejected
                    stats[annotator]['rejected'] += 1
        
        # Calculate accuracy for each annotator
        for annotator in stats:
            total = stats[annotator]['total_reviewed']
            if total > 0:
                stats[annotator]['accuracy'] = stats[annotator]['approved'] / total
        
        return stats
    
    def _render_accuracy_table(self, stats: Dict[str, Dict[str, Any]]):
        """Render accuracy statistics table"""
        # Create markdown table string
        table_str = "| Annotator | Total Completed | Total Reviewed | Approved | Rejected | Accuracy |\n"
        table_str += "|-----------|----------------|----------------|----------|----------|----------|\n"
        
        # Add data rows for each annotator
        for annotator, data in sorted(stats.items()):
            if data['total_reviewed'] > 0:
                table_str += (f"| {annotator} | {data['total_completed']} | {data['total_reviewed']} | "
                            f"{data['approved']} | {data['rejected']} | {data['accuracy']:.1%} |\n")
            else:
                table_str += (f"| {annotator} | {data['total_completed']} | 0 | 0 | 0 | N/A |\n")
        
        # Display the table
        st.markdown(table_str)
    
    def display_feedback_differences(self, prev_feedback: Dict[str, Any], feedback_data: Dict[str, Any], 
                                   diff_prompt: Optional[str] = None, reviewer_data: Optional[Dict[str, Any]] = None):
        """Display differences between current and previous feedback"""
        if not prev_feedback or not feedback_data:
            st.error("Previous feedback or current feedback does not exist. Please report this bug to Zhiqiu Lin.")
            return
        
        # Check if feedback is duplicated (rejected but not corrected)
        annotator_name = prev_feedback.get("user", "Unknown annotator")
        reviewer_name = (reviewer_data.get("reviewer_name", feedback_data.get("user", "Unknown reviewer")) 
                        if reviewer_data else feedback_data.get("user", "Unknown reviewer"))
        
        if prev_feedback == feedback_data:
            st.error(f"⚠️ **{annotator_name}'s** caption was rejected by **{reviewer_name}** "
                    f"but hasn't been corrected yet. Please ask **{reviewer_name}** to correct the caption.")
            return
        
        st.info(f"Displaying differences between **{annotator_name}'s** and **{reviewer_name}'s** feedback")
        
        st.write(f"##### **{annotator_name}'s** Original Feedback (GPT Polished)")
        st.write(prev_feedback.get("gpt_feedback", "No GPT feedback available"))
        
        st.write(f"##### **{reviewer_name}'s** Feedback (GPT Polished)")
        st.write(feedback_data.get("gpt_feedback", "No GPT feedback available"))
        
        st.write("##### Summary of Differences")
        st.markdown(self.ui.highlight_differences(
            prev_feedback.get("gpt_feedback", ""), 
            feedback_data.get("gpt_feedback", ""), 
            run_length=5
        ), unsafe_allow_html=True)
        
        st.write("##### ChatGPT summary of differences")
        if diff_prompt:
            self.ui.highlight_differences_gpt(
                prev_feedback.get("gpt_feedback", ""),
                feedback_data.get("gpt_feedback", ""),
                diff_prompt=str(self.data_manager.folder / diff_prompt),
                diff_key="gpt_feedback_diff_feedback",
                llm_key="gpt_feedback_diff_compare_llm",
                prompt_key="gpt_feedback_diff_compare_prompt",
                old_feedback=prev_feedback.get("gpt_feedback", ""),
                new_feedback=feedback_data.get("gpt_feedback", "")
            )
    
    def display_caption_differences(self, prev_feedback: Dict[str, Any], feedback_data: Dict[str, Any], 
                                  diff_prompt: Optional[str] = None, reviewer_data: Optional[Dict[str, Any]] = None):
        """Display differences between current and previous captions"""
        if not prev_feedback or not feedback_data:
            st.error("Previous feedback or current feedback does not exist. Please report this bug to Zhiqiu Lin.")
            return
        
        # Check if feedback is duplicated (rejected but not corrected)
        annotator_name = prev_feedback.get("user", "Unknown annotator")
        reviewer_name = (reviewer_data.get("reviewer_name", feedback_data.get("user", "Unknown reviewer")) 
                        if reviewer_data else feedback_data.get("user", "Unknown reviewer"))
        
        if prev_feedback == feedback_data:
            st.error(f"⚠️ **{annotator_name}'s** caption was rejected by **{reviewer_name}** "
                    f"but hasn't been corrected yet. Please ask **{reviewer_name}** to correct the caption.")
            return
        
        st.info(f"Displaying differences between **{annotator_name}'s** and **{reviewer_name}'s** captions")
        
        st.write(f"##### **{annotator_name}'s** Original Caption")
        st.write(prev_feedback.get("final_caption", "No caption available"))
        
        st.write(f"##### **{reviewer_name}'s** Revised Caption")
        st.write(feedback_data.get("final_caption", "No caption available"))
        
        st.write("##### Summary of Differences")
        st.markdown(self.ui.highlight_differences(
            prev_feedback.get("final_caption", ""), 
            feedback_data.get("final_caption", ""), 
            run_length=5
        ), unsafe_allow_html=True)
        
        st.write("##### ChatGPT summary of differences")
        if diff_prompt:
            self.ui.highlight_differences_gpt(
                prev_feedback.get("final_caption", ""),
                feedback_data.get("final_caption", ""),
                diff_prompt=str(self.data_manager.folder / diff_prompt),
                diff_key="final_caption_diff_feedback",
                llm_key="final_caption_diff_compare_llm",
                prompt_key="final_caption_diff_compare_prompt",
                old_caption=prev_feedback.get("final_caption", ""),
                new_caption=feedback_data.get("final_caption", "")
            )