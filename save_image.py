import os
import cv2
import numpy as np
import json

def save_image(encoded_image_bytes, metadata, save_image_filepath):
    """
    Save an image and its associated metadata to the specified file path.

    Parameters:
        encoded_image_bytes (bytes): The image data in bytes, encoded as a PNG.
        metadata (dict): A dictionary containing the metadata for the image.
        save_image_filepath (str): The directory path where the image and metadata will be saved.

    This function:
    - Decodes the image bytes into a numpy array and then into an image.
    - Saves the image as a PNG file in the specified directory.
    - Saves the metadata as a JSON file in the same directory, with the same base filename as the image.
    """
    object_count = count_files(save_image_filepath)  # Get the current count of images in the directory
    image_filepath = os.path.join(save_image_filepath, f'{object_count}.png')  # Define the filepath for the new image
    metadata_filepath = os.path.join(save_image_filepath, f"{object_count}.json")  # Define the filepath for the metadata

    # Convert the bytes back into a numpy array for decoding
    encoded_image_np = np.frombuffer(encoded_image_bytes, dtype=np.uint8)
    # Decode the image from the numpy array
    decoded_image = cv2.imdecode(encoded_image_np, cv2.IMREAD_UNCHANGED)

    # Save the image as a PNG file
    cv2.imwrite(image_filepath, decoded_image)

    # Save the metadata as a JSON file
    with open(metadata_filepath, 'w') as file:
        json.dump(metadata, file)

def count_files(directory_path):
    """
    Helper function to return the number of PNG files in the specified directory.

    Parameters:
        directory_path (str): The directory path to search for PNG files.

    Returns:
        int: The number of PNG files in the directory.

    This function:
    - Checks if the directory exists.
    - Iterates over all files in the directory and counts how many end with the `.png` extension.
    """
    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return 0

    count = 0
    # Iterate over all files in the directory and count the PNG files
    for file_name in os.listdir(directory_path):
        if file_name.lower().endswith('.png'):
            count += 1

    return count
