import streamlit as st
import os
import json
import argparse
from feedback_app import (
    parse_args, load_video_data, get_video_id, load_json, highlight_differences, split_into_words,
    get_filename, load_data, FOLDER, FEEDBACK_FILE_POSTFIX, PREV_FEEDBACK_FILE_POSTFIX,
    load_config, extract_frames, file_check, config_names_to_short_names, ANNOTATORS, REVIEWER_FILE_POSTFIX,
    display_feedback_info, display_feedback_differences, display_caption_differences, CONTAINER_HEIGHT
)
from datetime import datetime

def get_video_status(video_id, output_dir):
    """Get the status of a video's caption completion and previous iterations"""
    # Initialize all variables
    status = "not_completed"
    current_file = None
    prev_file = None
    current_user = None
    prev_user = None
    
    # Check all relevant files
    feedback_file = get_filename(video_id, output_dir, FEEDBACK_FILE_POSTFIX)
    prev_feedback_file = get_filename(video_id, output_dir, PREV_FEEDBACK_FILE_POSTFIX)
    reviewer_file = get_filename(video_id, output_dir, REVIEWER_FILE_POSTFIX)
    
    # Determine status based on file existence and content
    if not os.path.exists(feedback_file):
        return status, current_file, prev_file, current_user, prev_user
        
    current_file = feedback_file
    with open(feedback_file, 'r') as f:
        current_data = json.load(f)
        current_user = current_data.get("user")
    
    if not os.path.exists(reviewer_file):
        status = "completed_not_reviewed"
        return status, current_file, prev_file, current_user, prev_user
    
    # Load reviewer data
    with open(reviewer_file, 'r') as f:
        reviewer_data = json.load(f)
        reviewer_double_check = reviewer_data.get("reviewer_double_check", False)
        
        if reviewer_double_check:
            status = "approved"
            # For approved files, load previous feedback if it exists
            if os.path.exists(prev_feedback_file):
                with open(prev_feedback_file, 'r') as pf:
                    prev_data = json.load(pf)
                    prev_user = prev_data.get("user")
        else:
            status = "rejected"
            # For rejected files, must have prev feedback with different user
            assert os.path.exists(prev_feedback_file), f"Rejected file {video_id} must have previous feedback"
            with open(prev_feedback_file, 'r') as pf:
                prev_data = json.load(pf)
                prev_user = prev_data.get("user")
                with open(feedback_file, 'r') as cf:
                    current_data = json.load(cf)
                    current_user = current_data.get("user")
                    if prev_user == current_user:
                        # This means the caption was just rejected but it has not been updated yet
                        # In this case, we should show the previous version and treat it as not reviewed
                        status = "completed_not_reviewed"
                        prev_user = None
                        prev_file = None
                        return status, current_file, prev_file, current_user, prev_user
        
        prev_file = prev_feedback_file if os.path.exists(prev_feedback_file) else None
    
    return status, current_file, prev_file, current_user, prev_user

def calculate_accuracy_stats(video_urls, output_dir):
    """Calculate accuracy statistics for all videos in the given directory.
    
    Returns:
        dict: Dictionary containing statistics for each annotator:
            {
                'annotator_name': {
                    'total_completed': int,
                    'total_reviewed': int,
                    'approved': int,
                    'rejected': int,
                    'accuracy': float
                }
            }
    """
    stats = {}
    
    for video_url in video_urls:
        video_id = get_video_id(video_url)
        status, _, prev_file, current_user, prev_user = get_video_status(video_id, output_dir)
        
        # Skip if not completed
        if status == "not_completed":
            continue
            
        # Determine the annotator (original caption creator)
        annotator = prev_user if prev_file else current_user
        if annotator is None:
            print(f"annotator is None for video {video_id}")
            import pdb; pdb.set_trace()
            
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

def get_video_format_func(output_dir, video_urls=None):
    def video_format_func(video_url):
        if video_urls is not None:
            video_index = video_urls.index(video_url)
        else:
            video_index = ""
            
        video_id = get_video_id(video_url)
        video_url = video_url.split("/")[-1]
        
        # Get status and format accordingly
        status, _, _, _, _ = get_video_status(video_id, output_dir)
        status_emoji_map = {
            "not_completed": "",  # Not completed - no emoji
            "completed_not_reviewed": "✅",  # Completed but not reviewed - single checkmark
            "approved": "✅✅",  # Approved - double checkmark
            "rejected": "❌"  # Rejected
        }
        
        return f"{status_emoji_map[status]}{video_index}. {video_url}"
                    
    return video_format_func

def login_page(args):
    st.title("Video Caption Difference Viewer Login")

    # Create a form for login
    with st.form("login_form"):
        # Annotator selection dropdown
        selected_annotator = st.selectbox(
            "Select Your Name:",
            list(ANNOTATORS.keys()),
            key="selected_annotator"
        )
        
        # Password input
        password = st.text_input("Enter Password:", type="password", key="password_input")
        
        # File selection dropdown
        selected_file = st.selectbox(
            "Select Video URLs File:", args.video_urls_files, key="selected_urls_file"
        )

        submit_button = st.form_submit_button("Login")

        if submit_button:
            # Check if password matches
            if password == ANNOTATORS[selected_annotator]["password"]:
                # Store the selected file and annotator in session state
                st.session_state.video_urls_file = selected_file
                st.session_state.logged_in = True
                st.session_state.logged_in_user = selected_annotator
                st.success(f"Login successful! Welcome, {selected_annotator}!")
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

def format_timestamp(iso_timestamp):
    """Format ISO timestamp to a more readable format (YYYY-MM-DD HH:MM)"""
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return iso_timestamp  # Return original if parsing fails

def display_caption_expander(data, user, timestamp):
    """Helper function to display caption information in an expander"""
    st.write("##### Annotator")
    st.write(f"**Annotator:** {user}")
    st.write(f"**Timestamp:** {format_timestamp(timestamp)}")
    st.write("##### Pre-caption")
    st.write(data.get("pre_caption", "No pre-caption available"))
    
    # Use the existing display_feedback_info function from feedback_app.py
    display_feedback_info(data)

def display_accuracy_statistics(config_names, config_dict, video_urls, args):
    """Display accuracy statistics for all configs in an expander"""
    with st.expander("📊 Accuracy Statistics", expanded=False):
        # Calculate stats for all configs
        all_stats = {}
        for config_name in config_names:
            config = config_dict[config_name]
            output_dir = os.path.join(FOLDER, args.output, config["output_name"])
            if not os.path.exists(output_dir):
                continue
            stats = calculate_accuracy_stats(video_urls, output_dir)
            if stats:
                all_stats[config_name] = stats
        
        if not all_stats:
            st.info("No completed videos found for any task.")
        else:
            # Create tabs for each task
            task_tabs = st.tabs([config_names_to_short_names[config_name] for config_name in all_stats.keys()])
            
            # Add content to each tab
            for tab, (config_name, stats) in zip(task_tabs, all_stats.items()):
                with tab:
                    # Create markdown table string
                    table_str = "| Annotator | Total Completed | Total Reviewed | Approved | Rejected | Accuracy |\n"
                    table_str += "|-----------|----------------|----------------|----------|----------|----------|\n"
                    
                    # Add data rows for each annotator
                    for annotator, data in sorted(stats.items()):
                        if data['total_reviewed'] > 0:
                            table_str += f"| {annotator} | {data['total_completed']} | {data['total_reviewed']} | {data['approved']} | {data['rejected']} | {data['accuracy']:.1%} |\n"
                        else:
                            table_str += f"| {annotator} | {data['total_completed']} | 0 | 0 | 0 | N/A |\n"
                    # Display the table
                    st.markdown(table_str)

def main(args):
    # Set page config first
    st.set_page_config(initial_sidebar_state="collapsed", layout="wide")

    # Check login status
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_page(args)
        return
    
    # After successful login, update the output directory based on the logged-in user if personalize_output is True
    if args.personalize_output and "logged_in_user" in st.session_state:
        # Only set the personalized output directory once in session state
        if "personalized_output" not in st.session_state:
            username = convert_name_to_username(st.session_state.logged_in_user)
            st.session_state.personalized_output = f"{args.output}_{username}"
        
        # Use the stored personalized output directory
        args.output = st.session_state.personalized_output
        st.sidebar.write(f"**Output Directory:** {args.output}")

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
        with st.container(height=CONTAINER_HEIGHT, border=False):
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
            st.title(f"Caption Difference Viewer - {config.get('name', '')}")
            video_urls = load_json(FOLDER / st.session_state.video_urls_file)
            output_dir = os.path.join(FOLDER, args.output, config["output_name"])
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Add status explanation expander
            with st.expander("📝 Status Indicators Explanation", expanded=False):
                st.markdown("""
                | Emoji | Status | Description |
                |-------|--------|-------------|
                |  | Not Completed | Video has not been captioned yet |
                | ✅ | Completed | Video has been captioned but not reviewed |
                | ✅✅ | Approved | Video has been reviewed and double-checked |
                | ❌ | Rejected | Video needs revision (different users in current and previous feedback) |
                """)

            # Display accuracy statistics
            display_accuracy_statistics(config_names, config_dict, video_urls, args)

            # Select video
            selected_video = st.selectbox(
                "Select a video:",
                video_urls,
                format_func=get_video_format_func(output_dir, video_urls=video_urls),
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
                    st.image(extracted_frames[0], caption="First Frame")
                with col2:
                    st.image(extracted_frames[1], caption="Last Frame")
            
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
                
                st.link_button("🔗 Report Label Errors Here", "https://docs.google.com/spreadsheets/d/1sAYL86ERcaC_vrVuloXxtPJXKzeuj8fukHtNv6nRCJ0/edit?usp=sharing")

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
        with st.container(height=CONTAINER_HEIGHT, border=True):
            status, current_file, prev_file, current_user, prev_user = get_video_status(video_id, output_dir)
            
            if status == "not_completed":
                st.warning("Please complete this caption first.")
            elif status == "completed_not_reviewed":
                st.info("The caption has been completed but not reviewed yet.")
            elif status == "approved":
                # For approved captions, only show the current version
                current_data = load_data(video_id, output_dir=output_dir, file_postfix=FEEDBACK_FILE_POSTFIX)
                st.success("✅ This caption has been approved! Great job!")
                st.write("**Current Version:**")
                display_caption_expander(current_data, current_user, current_data.get("timestamp", "Unknown"))
            else:  # rejected
                # Load both current and previous captions
                current_data = load_data(video_id, output_dir=output_dir, file_postfix=FEEDBACK_FILE_POSTFIX)
                prev_data = load_data(video_id, output_dir=output_dir, file_postfix=PREV_FEEDBACK_FILE_POSTFIX)
                reviewer_data = load_data(video_id, output_dir=output_dir, file_postfix=REVIEWER_FILE_POSTFIX)
                st.subheader("Caption Changes")
                
                # Display metadata information
                current_timestamp = format_timestamp(current_data.get("timestamp", "Unknown"))
                prev_timestamp = format_timestamp(prev_data.get("timestamp", "Unknown"))
                
                st.write(f"**Current Version:** By {current_user} on {current_timestamp}")
                st.write(f"**Previous Version:** By {prev_user} on {prev_timestamp}")
                
                # Display a message if the same user made both versions
                st.warning("❌ This caption was rejected and needs to be fixed.")
                
                # Display the differences
                current_caption = current_data["final_caption"]
                prev_caption = prev_data["final_caption"]
                
                # Create tabs for different views
                tab1, tab2, tab3, tab4 = st.tabs(["Feedback Differences", "Caption Differences", "Previous Version", "Current Version"])
                
                with tab1:
                    st.subheader("Feedback Differences")
                    display_feedback_differences(
                        prev_feedback=prev_data,
                        feedback_data=current_data,
                        diff_prompt=args.diff_prompt,
                        reviewer_data=reviewer_data
                    )
                    
                with tab2:
                    st.subheader("Caption Differences")
                    display_caption_differences(
                        prev_feedback=prev_data,
                        feedback_data=current_data,
                        diff_prompt=args.diff_cap_prompt,
                        reviewer_data=reviewer_data
                    )
                    
                with tab3:
                    st.subheader("Previous Version")
                    display_caption_expander(prev_data, prev_user, prev_data.get('timestamp', ''))
                    
                with tab4:
                    st.subheader("Current Version")
                    display_caption_expander(current_data, current_user, current_data.get('timestamp', ''))

if __name__ == "__main__":
    args = parse_args()
    main(args) 