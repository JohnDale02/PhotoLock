import os
from upload_image import upload_image
import cv2
import json
from check_wifi import is_internet_availableTwo

def upload_saved_images():
    """
    Check if there are saved images in the 'tmpImages' directory and upload them when the internet is available.

    This function:
    - Continuously checks if there is internet connectivity.
    - If internet is available, it iterates through the 'tmpImages' directory to find saved images and their associated metadata.
    - For each image found, it uploads the image along with its metadata to the cloud using the `upload_image` function.
    - After a successful upload, it deletes the image and metadata files from the local directory.
    """

    # Check if the 'tmpImages' directory exists in the current working directory
    if os.path.exists(os.path.join(os.getcwd(), "tmpImages")):
        save_image_filepath = os.path.join(os.getcwd(), "tmpImages")
    else:
        print("The 'tmpImages' directory does not exist.")
        return  # Exit the function if the directory does not exist

    while True:
        if is_internet_availableTwo():
            count = 0
            for file_name in os.listdir(save_image_filepath):
                count += 1
                # Check if the file is a PNG image
                if file_name.lower().endswith('.png'):
                    file_path = os.path.join(save_image_filepath, file_name)
                    # Read the image from the file
                    image = cv2.imread(file_path)
                    _, encoded_image = cv2.imencode(".png", image)
                    
                    # Get the matching JSON metadata file
                    file_path_metadata = os.path.join(save_image_filepath, file_name[:-3] + 'json')
                    metadata = read_metadata(file_path_metadata)

                    try:
                        # Upload the image and metadata
                        upload_image(encoded_image.tobytes(), metadata)
                        print("------------------------------------------------------")
                        print("Uploaded Saved Image")
                        # Remove the image and metadata files after a successful upload
                        os.remove(file_path)
                        os.remove(file_path_metadata)
                    except Exception as e:
                        print(f"Error uploading saved image: {str(e)}")

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

# Uncomment the following line to run the function:
# upload_saved_images()
