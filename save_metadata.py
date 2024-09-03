import os
import cv2
import numpy as np
import json

def save_metadata(metadata, save_metadata_filepath):
    """
    Save metadata to a specified file path in JSON format.

    Parameters:
        metadata (dict): A dictionary containing the metadata to be saved.
        save_metadata_filepath (str): The file path where the metadata will be saved.

    This function:
    - Writes the metadata dictionary to a JSON file at the specified location.
    """
    # Open the specified file in write mode and dump the metadata dictionary into it as JSON
    with open(save_metadata_filepath, 'w') as file:
        json.dump(metadata, file)
