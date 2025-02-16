import cv2
import numpy as np

def extract_frame(video_path: str, frame_number: int) -> np.ndarray:
    """
    Extracts a specific frame from a video using OpenCV and converts it to RGB format.

    Parameters:
        video_path (str): Path or URL to the video file.
        frame_number (int): The frame index to extract. Supports negative indices:
                            -1 refers to the last frame, -2 to the second last, etc.

    Returns:
        np.ndarray: The extracted frame in RGB format.
    
    Raises:
        ValueError: If the video cannot be opened or the frame number is out of range.
        RuntimeError: If the frame extraction fails.
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Error: Unable to open video {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Convert negative indices to positive (e.g., -1 -> last frame)
    if frame_number < 0:
        frame_number = total_frames + frame_number  # Adjust for negatives

    if frame_number < 0 or frame_number >= total_frames:
        raise ValueError(f"Error: Frame number {frame_number} is out of range (0 to {total_frames - 1})")

    # Set the frame position
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    # Read the frame
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError(f"Error: Unable to extract frame {frame_number} from {video_path}")

    # Convert BGR to RGB for easier visualization
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

def extract_middle_frame(video_path: str) -> np.ndarray:
    """
    Extracts the middle frame of a video using OpenCV.

    Parameters:
        video_path (str): Path or URL to the video file.

    Returns:
        np.ndarray: The extracted middle frame in RGB format.
    
    Raises:
        ValueError: If the video cannot be opened.
        RuntimeError: If the frame extraction fails.
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Error: Unable to open video {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    middle_frame_index = total_frames // 2  # Get the middle frame index

    cap.release()

    return extract_frame(video_path, middle_frame_index)


if __name__ == "__main__":
    # Example usage
    video_path = "your_video.mp4"

    # Extract first and last frames using positive and negative indices
    first_frame = extract_frame(video_path, 0)
    last_frame = extract_frame(video_path, -1)  # Using negative index for last frame
