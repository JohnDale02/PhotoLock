import os
import cv2
import json
from upload_image import upload_image
from upload_video import upload_video

def upload_saved_media(upload_lock):
    """
    Thread function for uploading saved media (images and videos) in the background when WiFi is available.

    Parameters:
        upload_lock (threading.Lock): A lock to ensure that only one upload operation occurs at a time.

    This function:
    - Continuously checks for WiFi connectivity (via the `wifi_status` global variable).
    - If WiFi is available, it iterates through the `tmpImages` and `tmpVideos` directories to find saved images and videos.
    - Uploads each image or video found along with its associated metadata.
    - Deletes the media and metadata files from the local storage after successful upload.
    """
    global wifi_status

    while True:
        if wifi_status:
            with upload_lock:
                # Check if the 'tmpImages' directory exists
                if os.path.exists(os.path.join(os.getcwd(), "tmpImages")):
                    save_image_filepath = os.path.join(os.getcwd(), "tmpImages")
                else:
                    print("There is no 'tmpImages' directory")

                # Check if the 'tmpVideos' directory exists
                if os.path.exists(os.path.join(os.getcwd(), "tmpVideos")):
                    save_video_filepath = os.path.join(os.getcwd(), "tmpVideos")
                else:
                    print("There is no 'tmpVideos' directory")

                # Upload saved images
                for file_name in os.listdir(save_image_filepath):
                    if file_name.lower().endswith('.png'):
                        file_path = os.path.join(save_image_filepath, file_name)  # Get the full path to the image
                        image = cv2.imread(file_path)  # Read the image
                        _, encoded_image = cv2.imencode(".png", image)  # Encode the image

                        # Get the matching JSON metadata file
                        file_path_metadata = os.path.join(save_image_filepath, file_name[:-3] + 'json')
                        metadata = read_metadata(file_path_metadata)

                        try:
                            upload_image(encoded_image.tobytes(), metadata)  # Upload the image with its metadata
                            print("------------------------------------------------------")
                            print("Uploaded Saved Image")
                            # Remove the image and metadata files after a successful upload
                            os.remove(file_path)
                            os.remove(file_path_metadata)
                        except Exception as e:
                            print(f"Error uploading saved image: {str(e)}")

                # Upload saved videos
                for file_name in os.listdir(save_video_filepath):
                    if file_name.lower().endswith('.avi'):
                        file_path = os.path.join(save_video_filepath, file_name)  # Get the full path to the video
                        with open(file_path, 'rb') as video:
                            video_bytes = video.read()

                        # Get the matching JSON metadata file
                        file_path_metadata = os.path.join(save_video_filepath, file_name[:-3] + 'json')
                        metadata = read_metadata(file_path_metadata)

                        try:
                            upload_video(video_bytes, metadata)  # Upload the video with its metadata
                            print("------------------------------------------------------")
                            print("Uploaded Saved Video")
                            # Remove the video and metadata files after a successful upload
                            os.remove(file_path)
                            os.remove(file_path_metadata)
                        except Exception as e:
                            print(f"Error uploading saved video: {str(e)}")

def read_metadata(file_path_metadata):
    """
    Read metadata from a JSON file.

    Parameters:
        file_path_metadata (str): The file path to the JSON metadata file.

    Returns:
        dict: The metadata as a dictionary.
    """
    with open(file_path_metadata, 'r') as file:
        metadata = json.load(file)
        return metadata
