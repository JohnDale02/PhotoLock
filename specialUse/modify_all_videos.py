import cv2
import numpy as np
import os

def alter_video(video_path, temp_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height), isColor=False)

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            out.write(gray_frame)
        else:
            break

    cap.release()
    out.release()

    os.remove(video_path)
    os.rename(temp_path, video_path)
    print(f"Video {os.path.basename(video_path)} overwritten with the modified version successfully.")

def process_all_avi_files(input_directory):
    for filename in os.listdir(input_directory):
        if filename.endswith('.avi'):
            video_path = os.path.join(input_directory, filename)
            temp_path = os.path.join(input_directory, f"temp_{filename}")  # Temporary file path
            
            alter_video(video_path, temp_path)

# Input directory where the AVI files are stored
input_directory = "C:\\S3Backup"

# Process all AVI files in the directory
process_all_avi_files(input_directory)
