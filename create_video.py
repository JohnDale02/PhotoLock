import cv2
import subprocess
import base64
import os
import time

def create_video(save_video_filepath: str) -> tuple:
    """
    Captures a video, saves it to a specified file path, and returns the video data as bytes.

    This function captures video data using the camera, saves the video as an AVI file in the
    specified directory, and returns the video data as a byte object. It also returns the object
    count, which represents the number of videos saved in the directory.

    Args:
        save_video_filepath (str): The directory path where the video file will be saved.

    Returns:
        tuple: A tuple containing the video data as bytes and the object count (number of videos saved).
               Returns None if the video capture fails.
    """

    # Count the number of existing video files in the directory to generate a unique filename
    object_count = count_files(save_video_filepath)
    video_filepath = os.path.join(save_video_filepath, f'{object_count}.avi')

    # Capture the video and get the video data as bytes
    video_bytes = capture_video(video_filepath)

    if video_bytes is not None:
        print("\Video not None, Loading...")
        return video_bytes, object_count
    else:
        print("Video is None")
        return None


def capture_video(video_filename: str) -> bytes:
    """
    Initializes the camera and captures a video, saving it to the specified filename.

    This function uses the `ffmpeg` command-line tool to capture video from the camera
    and save it as an AVI file. It reads the video file into memory as bytes and returns
    the byte data.

    Args:
        video_filename (str): The filename where the captured video will be saved.

    Returns:
        bytes: The video data as a byte object. Returns None if the capture fails.
    """

    # Define the command and arguments to capture video using ffmpeg
    command = [
        'ffmpeg',
        '-framerate', '24',               # Set the frame rate to 24 fps
        '-video_size', '1280x720',         # Set the video resolution to 1280x720
        '-i', '/dev/video0',               # Input video device (e.g., webcam)
        '-f', 'alsa', '-i', 'default',     # Input audio device (e.g., default microphone)
        '-c:v', 'h264_v4l2m2m',            # Video codec (H.264 hardware encoding)
        '-pix_fmt', 'yuv420p',             # Pixel format
        '-b:v', '4M',                      # Video bitrate
        '-bufsize', '4M',                  # Buffer size
        '-c:a', 'aac',                     # Audio codec (AAC)
        '-b:a', '128k',                    # Audio bitrate
        '-threads', '4',                   # Number of threads for encoding
        video_filename                     # Output video file
    ]
    
    # Execute the ffmpeg command to capture the video
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    print(f"Video output: stdout {stdout}, stderr: {stderr}")

    # Read the captured video file and return it as bytes
    print("Reading and returning AVI bytes")
    video_bytes = None
    with open(video_filename, 'rb') as video:
        video_bytes = video.read()

    if video_bytes is None:
        return None
    else:
        return video_bytes


def count_files(directory_path: str) -> int:
    """
    Helper function to count the number of AVI files in a directory.

    This function counts the number of files in the specified directory that have an AVI file extension.

    Args:
        directory_path (str): The directory path where video files are stored.

    Returns:
        int: The number of AVI files in the directory.
    """

    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return 0

    count = 0
    # Iterate over all files in the directory and count AVI files
    for file_name in os.listdir(directory_path):
        if file_name.lower().endswith('.avi'):
            count += 1

    return count
