import streamlit as st
import difflib
import os
import re
from feedback_app import (
    load_video_data, get_video_id, load_json, 
    get_filename, load_data, FOLDER, FEEDBACK_FILE_POSTFIX, PREV_FEEDBACK_FILE_POSTFIX,
    load_config, extract_frames, file_check, config_names_to_short_names, ANNOTATORS,
    convert_name_to_username
)
from datetime import datetime
import argparse

def parse_args():
    """Parse command line arguments for the new annotator diff app"""
    parser = argparse.ArgumentParser(description="New Annotator Comparison Viewer")
    parser.add_argument("--configs", type=str, default="all_configs.json", help="Path to the JSON config file")
    parser.add_argument(
        "--video_urls_files",
        nargs="+",
        type=str,
        default=[
            "video_urls/new_annotator_exam/exam.json",
        ],
        help="List of paths to test URLs files",
    )
    parser.add_argument("--output", type=str, default="output_captions", help="Path to the original output directory")
    parser.add_argument("--output_new_annotator", type=str, default="output_new_annotator", help="Path to the new annotator output directory")
    parser.add_argument("--video_data", type=str, default="video_data/20250227_0507ground_and_setup/videos.json", help="Path to the video data file")
    parser.add_argument("--label_collections", nargs="+", type=str, default=["cam_motion", "cam_setup"], help="List of label collections to load from the video data")
    parser.add_argument("--personalize_output", action="store_true", default=True, help="Whether to personalize the output directory based on the logged-in user")
    return parser.parse_args()

def get_video_status(video_id, output_dir, new_annotator_output_dir):
    """Get the status of a video's caption completion and compare with new annotator version"""
    current_file = get_filename(video_id, output_dir, FEEDBACK_FILE_POSTFIX)
    new_annotator_file = get_filename(video_id, new_annotator_output_dir, FEEDBACK_FILE_POSTFIX)
    
    if not os.path.exists(current_file):
        # print(f"Current file does not exist: {current_file}")
        return "not_done", None, None, None, None
    elif not os.path.exists(new_annotator_file):
        # print(f"New annotator file does not exist: {new_annotator_file}")
        return "not_done_by_new_annotator", current_file, None, None, None
    else:
        # Load both current and new annotator data to check users
        current_data = load_data(video_id, output_dir=output_dir, file_postfix=FEEDBACK_FILE_POSTFIX)
        new_annotator_data = load_data(video_id, output_dir=new_annotator_output_dir, file_postfix=FEEDBACK_FILE_POSTFIX)
        
        current_user = current_data.get("user", "Unknown")
        new_annotator_user = new_annotator_data.get("user", "Unknown")
        
        return "done_by_new_annotator", current_file, new_annotator_file, current_user, new_annotator_user

def split_into_words(text):
    """Split text into words for better diff visualization"""
    # Split by whitespace and punctuation
    words = re.findall(r"\w+|\W+", text)
    return words

def highlight_differences(text1, text2):
    """Highlight differences between two texts using HTML with word-level granularity"""
    # Split texts into words
    words1 = split_into_words(text1)
    words2 = split_into_words(text2)
    
    # Use difflib to find differences
    differ = difflib.Differ()
    diff = list(differ.compare(words1, words2))
    
    # Process the diff to create HTML with highlighting
    result = []
    for word in diff:
        if word.startswith('  '):  # unchanged
            result.append(word[2:])
        elif word.startswith('- '):  # deleted
            result.append(f'<span style="color: red; text-decoration: line-through;">{word[2:]}</span>')
        elif word.startswith('+ '):  # added
            result.append(f'<span style="color: green; font-weight: bold;">{word[2:]}</span>')
    
    return ''.join(result)

def get_video_format_func(output_dir, new_annotator_output_dir):
    """Format function for video selection dropdown with status emojis"""
    def format_func(video_url):
        video_id = get_video_id(video_url)
        status, _, _, _, _ = get_video_status(video_id, output_dir, new_annotator_output_dir)
        
        emoji_map = {
            "not_done": "❓",  # for not completed
            "not_done_by_new_annotator": "❌",  # for completed but not by new annotator
            "done_by_new_annotator": "✅"  # for done by new annotator
        }
        
        emoji = emoji_map[status]
        return f"{emoji} {video_url.split('/')[-1]}"
    
    return format_func

def login_page(args):
    st.title("New Annotator Comparison Viewer Login")

    # Create a form for login
    with st.form("login_form"):
        # Annotator selection dropdown
        selected_annotator = st.selectbox(
            "Select Annotator Name:",
            list(ANNOTATORS.keys()),
            key="selected_annotator"
        )
        
        # File selection dropdown
        selected_file = st.selectbox(
            "Select Video URLs File:", args.video_urls_files, key="selected_urls_file"
        )

        submit_button = st.form_submit_button("Login")

        if submit_button:
            # Store the selected file and annotator in session state
            st.session_state.video_urls_file = selected_file
            st.session_state.logged_in = True
            st.session_state.logged_in_user = selected_annotator
            st.success(f"Login successful! Welcome, {selected_annotator}!")
            st.rerun()

def format_timestamp(iso_timestamp):
    """Format ISO timestamp to a more readable format (YYYY-MM-DD HH:MM)"""
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return iso_timestamp  # Return original if parsing fails

def main(args):
    # Set page config first
    st.set_page_config(initial_sidebar_state="collapsed", layout="wide")

    # Check login status
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_page(args)
        return
    
    # After successful login, update the new annotator output directory based on the logged-in user if personalize_output is True
    if args.personalize_output and "logged_in_user" in st.session_state:
        # Only set the personalized output directory once in session state
        if "personalized_output" not in st.session_state:
            username = convert_name_to_username(st.session_state.logged_in_user)
            st.session_state.personalized_output = f"{args.output_new_annotator}_{username}"
        
        # Use the stored personalized output directory for new annotator
        args.output_new_annotator = st.session_state.personalized_output
        st.sidebar.write(f"**New Annotator Output Directory:** {args.output_new_annotator}")

    # Load video data
    video_data_dict = load_video_data(args.video_data, label_collections=args.label_collections)
    if "file_check_passed" not in st.session_state:
        file_check(st.session_state.video_urls_file, video_data_dict)
        st.session_state.file_check_passed = True

    # Create two columns
    page_col1, page_col2 = st.columns([1, 1])  # Left column is smaller, right column is wider

    # Add logout button
    st.sidebar.title("User Options")
    st.sidebar.write(f"Logged in as: **{st.session_state.logged_in_user}**")
    if st.sidebar.button("Logout"):
        # Clear session state and logout
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Debug information
    st.sidebar.header("Debug Information")
    st.sidebar.write("Full Session State:")
    for key, value in st.session_state.items():
        st.sidebar.write(f"{key}: {value}")
    try:
        configs = load_config(FOLDER / args.configs)
        configs = [load_config(FOLDER / config) for config in configs]
    except FileNotFoundError:
        st.error(f"Config file not found: {args.configs}")
        return

    with page_col1:
        config_dict = {config["name"]: config for config in configs}
        config_names = list(config_dict.keys())
        # Dropdown to select a config, updating session state
        selected_config = st.selectbox(
            "Select a task:",
            config_names,
            index=config_names.index(st.session_state.get('last_config_id', config_names[0])),
            key="selected_task",
        )

        # Track task changes to reset state
        if 'last_config_id' not in st.session_state:
            st.session_state.last_config_id = selected_config
        elif st.session_state.last_config_id != selected_config:
            # Config changed, reset all state variables
            # First, collect all keys to remove
            keys_to_remove = []
            for key in st.session_state:
                # Keep api_key and last_config_id
                if key not in ['api_key', 'last_config_id', 'file_check_passed', 'logged_in', 'video_urls_file', 'last_video_id', 'last_selected_video', 'logged_in_user', 'personalized_output']:
                    keys_to_remove.append(key)

            # Remove all collected keys
            for key in keys_to_remove:
                del st.session_state[key]

            # Set the new video id
            st.session_state.last_config_id = selected_config
            print(f"Config changed to: {selected_config}")
            st.rerun()  # Force a rerun to ensure clean state

        config = config_dict[selected_config]
        st.title(f"New Annotator Comparison Viewer - {config.get('name', '')}")
        video_urls = load_json(FOLDER / st.session_state.video_urls_file)
        output_dir = os.path.join(FOLDER, args.output, config["output_name"])
        new_annotator_output_dir = os.path.join(FOLDER, args.output_new_annotator, config["output_name"])
        
        # if not os.path.exists(output_dir):
        #     os.makedirs(output_dir)
        # if not os.path.exists(new_annotator_output_dir):
        #     os.makedirs(new_annotator_output_dir)

        # Select video
        selected_video = st.selectbox(
            "Select a video:",
            video_urls,
            format_func=get_video_format_func(output_dir, new_annotator_output_dir),
            index=video_urls.index(st.session_state.get('last_selected_video', video_urls[0])),
            key="selected_video"
        )
        video_id = get_video_id(selected_video)

        # Track video changes to reset state
        if 'last_video_id' not in st.session_state:
            st.session_state.last_video_id = video_id
            st.session_state.last_selected_video = selected_video
        elif st.session_state.last_video_id != video_id:
            # Video changed, reset all state variables
            # First, collect all keys to remove
            keys_to_remove = []
            for key in st.session_state:
                # Keep api_key and last_video_id
                if key not in ['api_key', 'last_config_id', 'selected_config', 'last_video_id', 'last_selected_video', 'file_check_passed', 'logged_in', 'video_urls_file', 'logged_in_user', 'personalized_output']:
                    keys_to_remove.append(key)

            # Remove all collected keys
            for key in keys_to_remove:
                del st.session_state[key]

            # Set the new video id
            st.session_state.last_video_id = video_id
            st.session_state.last_selected_video = selected_video

            st.rerun()  # Force a rerun to ensure clean state

        # Display video
        st.video(selected_video)

        # Display first and last frames
        extracted_frames = extract_frames(selected_video, [0, -1])
        # Expandable section
        with st.expander("Frames (Click to Expand/Collapse)", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.image(extracted_frames[0], caption="First Frame", use_container_width=True)
            with col2:
                st.image(extracted_frames[1], caption="Last Frame", use_container_width=True)
        
        with st.expander("Show Links", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            # ['cam_motion', 'cam_setup', 'lighting_setup'] check workflows['cam_motion'].editing_url
            with col1:
                if 'cam_motion' in video_data_dict[video_id].workflows:
                    st.link_button("🔗 Cam-Motion", video_data_dict[video_id].workflows['cam_motion'].editing_url)
                else:
                    st.link_button("🔗 Cam-Motion", "https://example.com/a", type='secondary', disabled=True)
                    
            with col2:
                if 'cam_setup' in video_data_dict[video_id].workflows:
                    st.link_button("🔗 Cam-Setup", video_data_dict[video_id].workflows['cam_setup'].editing_url)
                else:
                    st.link_button("🔗 Cam-Setup", "https://example.com/b", type='secondary', disabled=True)
                    
            with col3:
                if 'lighting_setup' in video_data_dict[video_id].workflows:
                    st.link_button("🔗 Lighting-Setup", video_data_dict[video_id].workflows['lighting_setup'].editing_url)
                else:
                    st.link_button("🔗 Lighting-Setup", "https://example.com/c", type='secondary', disabled=True)
            
            st.link_button("🔗 Report Label Errors Here", "https://docs.google.com/spreadsheets/d/1sAYL86ERcaC_vrVuloXxtPJXKzeuj8fukHtNv6nRCJ0/edit?usp=sharing", use_container_width=True)

        # Get indices
        current_index = video_urls.index(selected_video)
        current_task_index = config_names.index(selected_config)

        # Keys to keep
        preserved_keys = [
            'api_key', 'last_config_id', 'selected_config',
            'last_video_id', 'last_selected_video', 
            'file_check_passed', 'logged_in', 'video_urls_file', 'logged_in_user', 'personalized_output'
        ]

        def reset_state_except(preserved):
            keys_to_remove = [key for key in st.session_state if key not in preserved]
            for key in keys_to_remove:
                del st.session_state[key]
            st.rerun()

        # Create a single horizontal row with 4 nav buttons
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])

        with col1:
            if current_index > 0:
                if st.button("Prev Video ⏪"):
                    st.session_state.last_selected_video = video_urls[current_index - 1]
                    st.session_state.last_video_id = get_video_id(video_urls[current_index - 1])
                    reset_state_except(preserved_keys)
            else:
                st.button("Prev Video ⏪", disabled=True)

        with col2:
            if current_task_index > 0:
                prev_task_short_name = config_names_to_short_names[config_names[current_task_index - 1]]
                if st.button(f"{prev_task_short_name} Task ⬅️"):
                    st.session_state.last_config_id = config_names[current_task_index - 1]
                    reset_state_except(preserved_keys)
            else:
                st.button("No Prev Task ⬅️", disabled=True)
        
        with col3:
            task_short_name = config_names_to_short_names[selected_config]
            st.button(f"{task_short_name} Task 📍", disabled=True)

        with col4:
            if current_task_index < len(config_names) - 1:
                next_task_short_name = config_names_to_short_names[config_names[current_task_index + 1]]
                if st.button(f"{next_task_short_name} Task ➡️"):
                    st.session_state.last_config_id = config_names[current_task_index + 1]
                    reset_state_except(preserved_keys)
            else:
                st.button("No Next Task ➡️ ", disabled=True)

        with col5:
            if current_index < len(video_urls) - 1:
                if st.button("Next Video ⏩"):
                    st.session_state.last_selected_video = video_urls[current_index + 1]
                    st.session_state.last_video_id = get_video_id(video_urls[current_index + 1])
                    reset_state_except(preserved_keys)
            else:
                st.button("Next Video ⏭️", disabled=True)

    with page_col2:
        status, current_file, new_annotator_file, current_user, new_annotator_user = get_video_status(video_id, output_dir, new_annotator_output_dir)
        
        if status == "not_done":
            st.warning("Please complete this caption first.")
        elif status == "not_done_by_new_annotator":
            st.info("No new annotator version found.")
        else:  # done_by_new_annotator
            # Load both current and new annotator captions
            current_data = load_data(video_id, output_dir=output_dir, file_postfix=FEEDBACK_FILE_POSTFIX)
            new_annotator_data = load_data(video_id, output_dir=new_annotator_output_dir, file_postfix=FEEDBACK_FILE_POSTFIX)
            
            st.subheader("Caption Comparison")
            
            # Display metadata information
            current_timestamp = format_timestamp(current_data.get("timestamp", "Unknown"))
            new_annotator_timestamp = format_timestamp(new_annotator_data.get("timestamp", "Unknown"))
            
            st.write(f"**Ground Truth Version:** By {current_user} on {current_timestamp}")
            st.write(f"**Your Version:** By {new_annotator_user} on {new_annotator_timestamp}")
            
            # Create tabs for viewing captions
            tab1, tab2, tab3, tab4 = st.tabs(["Ground Truth Version", "Your Version", "Caption Differences", "Feedback Differences"])
            
            with tab1:
                st.subheader("Ground Truth Version")
                st.write(f"**User:** {current_user}")
                st.write(f"**Timestamp:** {format_timestamp(current_data.get('timestamp', ''))}")
                st.write("**Caption:**")
                st.write(current_data.get("final_caption", "No caption available"))
                
                # Add pre-caption, initial feedback, and GPT feedback information
                with st.expander("Pre-caption and feedback", expanded=True):
                    st.write("**Pre-caption:**")
                    st.write(current_data.get("pre_caption", "No pre-caption available"))
                    st.write("**Human Feedback:**")
                    st.write(current_data.get("initial_feedback", "No initial feedback available"))
                    st.write("**GPT-Polished Feedback:**")
                    st.write(current_data.get("gpt_feedback", "No GPT feedback available"))
            
            with tab2:
                st.subheader("Your Version")
                st.write(f"**User:** {new_annotator_user}")
                st.write(f"**Timestamp:** {format_timestamp(new_annotator_data.get('timestamp', ''))}")
                st.write("**Caption:**")
                st.write(new_annotator_data.get("final_caption", "No caption available"))
                
                # Add pre-caption, initial feedback, and GPT feedback information
                with st.expander("Pre-caption and feedback", expanded=True):
                    st.write("**Pre-caption:**")
                    st.write(new_annotator_data.get("pre_caption", "No pre-caption available"))
                    st.write("**Human Feedback:**")
                    st.write(new_annotator_data.get("initial_feedback", "No initial feedback available"))
                    st.write("**GPT-Polished Feedback:**")
                    st.write(new_annotator_data.get("gpt_feedback", "No GPT feedback available"))
            
            with tab3:
                st.subheader("Highlighted Differences")
                st.write("**Differences Summary:**")
                
                # Get captions
                original_caption = current_data.get("final_caption", "")
                new_caption = new_annotator_data.get("final_caption", "")
                
                # Check if there are any differences
                if original_caption == new_caption:
                    st.success("No differences found between the ground truth and your version.")
                else:
                    # Highlight differences
                    highlighted_diff = highlight_differences(original_caption, new_caption)
                    st.markdown(highlighted_diff, unsafe_allow_html=True)
                
                # Calculate statistics instead of showing all words
                original_words = split_into_words(original_caption)
                new_words = split_into_words(new_caption)
                
                # Calculate word counts
                original_word_count = len([w for w in original_words if w.strip()])
                new_word_count = len([w for w in new_words if w.strip()])
                
                # Calculate character counts
                original_char_count = len(original_caption)
                new_char_count = len(new_caption)
                
                # Calculate percentage changes
                word_change_percent = ((new_word_count - original_word_count) / max(original_word_count, 1)) * 100
                char_change_percent = ((new_char_count - original_char_count) / max(original_char_count, 1)) * 100
                
                # Display statistics
                st.write("**Caption Statistics:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Ground Truth Version:**")
                    st.write(f"- Word count: {original_word_count}")
                    st.write(f"- Character count: {original_char_count}")
                
                with col2:
                    st.write(f"**Your Version:**")
                    st.write(f"- Word count: {new_word_count}")
                    st.write(f"- Character count: {new_char_count}")
                
                st.write("**Differences:**")
                st.write(f"- Word count difference: {new_word_count - original_word_count} ({word_change_percent:.1f}%)")
                st.write(f"- Character count difference: {new_char_count - original_char_count} ({char_change_percent:.1f}%)")
                
                # Show a summary of the caption content
                st.write("**Caption Summary:**")
                if original_caption and new_caption:
                    st.write("**Ground Truth Caption:**")
                    st.write(original_caption[:200] + "..." if len(original_caption) > 200 else original_caption)
                    
                    st.write("**Your Caption:**")
                    st.write(new_caption[:200] + "..." if len(new_caption) > 200 else new_caption)
                else:
                    st.write("No caption available for comparison.")
                
                # Show key differences (most significant changes)
                st.write("**Key Differences:**")
                
                # Find the most significant changes (longer phrases)
                original_phrases = [p for p in original_caption.split('.') if p.strip()]
                new_phrases = [p for p in new_caption.split('.') if p.strip()]
                
                # Find added and removed phrases
                added_phrases = []
                removed_phrases = []
                
                for phrase in new_phrases:
                    if phrase.strip() and phrase.strip() not in original_phrases:
                        added_phrases.append(phrase.strip())
                
                for phrase in original_phrases:
                    if phrase.strip() and phrase.strip() not in new_phrases:
                        removed_phrases.append(phrase.strip())
                
                # Show top 3 most significant changes
                if added_phrases:
                    st.write("**Added Phrases:**")
                    for i, phrase in enumerate(added_phrases[:3]):
                        st.write(f"{i+1}. {phrase}")
                    if len(added_phrases) > 3:
                        st.write(f"... and {len(added_phrases) - 3} more")
                elif removed_phrases:
                    st.write("**No added phrases.**")
                
                if removed_phrases:
                    st.write("**Removed Phrases:**")
                    for i, phrase in enumerate(removed_phrases[:3]):
                        st.write(f"{i+1}. {phrase}")
                    if len(removed_phrases) > 3:
                        st.write(f"... and {len(removed_phrases) - 3} more")
                elif added_phrases:
                    st.write("**No removed phrases.**")
                
                if not added_phrases and not removed_phrases:
                    st.write("**No significant differences found.**")

            with tab4:
                st.subheader("Initial Feedback Differences")
                st.write("**Differences in Initial Feedback:**")
                
                # Get initial feedback
                original_feedback = current_data.get("initial_feedback")
                new_feedback = new_annotator_data.get("initial_feedback")
                
                # Convert None to empty string
                original_feedback = "" if original_feedback is None else original_feedback
                new_feedback = "" if new_feedback is None else new_feedback
                
                # Check if there are any differences
                if original_feedback == new_feedback:
                    st.success("No differences found between the ground truth and your initial feedback.")
                else:
                    # Highlight differences
                    highlighted_feedback_diff = highlight_differences(original_feedback, new_feedback)
                    st.markdown(highlighted_feedback_diff, unsafe_allow_html=True)
                
                # Calculate statistics instead of showing all words
                original_feedback_words = split_into_words(original_feedback)
                new_feedback_words = split_into_words(new_feedback)
                
                # Calculate word counts
                original_word_count = len([w for w in original_feedback_words if w.strip()])
                new_word_count = len([w for w in new_feedback_words if w.strip()])
                
                # Calculate character counts
                original_char_count = len(original_feedback)
                new_char_count = len(new_feedback)
                
                # Calculate percentage changes
                word_change_percent = ((new_word_count - original_word_count) / max(original_word_count, 1)) * 100
                char_change_percent = ((new_char_count - original_char_count) / max(original_char_count, 1)) * 100
                
                # Display statistics
                st.write("**Feedback Statistics:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Ground Truth Version:**")
                    st.write(f"- Word count: {original_word_count}")
                    st.write(f"- Character count: {original_char_count}")
                
                with col2:
                    st.write(f"**Your Version:**")
                    st.write(f"- Word count: {new_word_count}")
                    st.write(f"- Character count: {new_char_count}")
                
                st.write("**Differences:**")
                st.write(f"- Word count difference: {new_word_count - original_word_count} ({word_change_percent:.1f}%)")
                st.write(f"- Character count difference: {new_char_count - original_char_count} ({char_change_percent:.1f}%)")
                
                # Show a summary of the feedback content
                st.write("**Feedback Summary:**")
                if original_feedback and new_feedback:
                    st.write("**Ground Truth Feedback:**")
                    st.write(original_feedback[:200] + "..." if len(original_feedback) > 200 else original_feedback)
                    
                    st.write("**Your Feedback:**")
                    st.write(new_feedback[:200] + "..." if len(new_feedback) > 200 else new_feedback)
                else:
                    st.write("No feedback available for comparison.")

if __name__ == "__main__":
    args = parse_args()
    main(args) 