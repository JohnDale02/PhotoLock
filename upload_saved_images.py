# function for checking if we have saved images and uploading all of them
import os
from upload_image import upload_image
import cv2
import json

def upload_saved_images(save_image_filepath):

    # get all png files in a folder
    # for each png file (and matching json file)
    # Iterate over all files in the folder
    count = 0
    for file_name in os.listdir(save_image_filepath):
        count += 1
        # Check if the file is a PNG
        if file_name.lower().endswith('.png'):
            file_path = os.path.join(save_image_filepath, file_name)
            # Call the upload function

            image = cv2.imread(file_path) 
            _, encoded_image = cv2.imencode(".png", image)
            
            file_path_metadata = os.path.join(save_image_filepath, file_name[:-3]+'json') # get matching json
            metadata = read_metadata(file_path_metadata)

            try:
                upload_image(encoded_image.tobytes(), metadata)   # cv2 png object, metadat
                print(f"Uploaded Image")
            except Exception as e:
                print(f"Error uploading saved image: {str(e)}")
    
    print(f"Done uploading {count} saved images")
                

def read_metadata(file_path_metadata):
     with open(file_path_metadata, 'r') as file:
        metadata = json.load(file)
        return metadata

upload_saved_images("~/SDP-Camera/tmpImages")
