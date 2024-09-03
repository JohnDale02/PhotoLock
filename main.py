from create_image import create_image
from check_wifi import is_internet_available
from create_metadata import create_metadata
from create_combined import create_combined
from upload_image import upload_image
from create_digest import create_digest
from create_signature import create_signature
from GPS_uart import parse_nmea_sentence, read_gps_data
import cv2
import base64
from save_image import save_image
from save_metadata import save_metadata
import os
from upload_video import upload_video

def main(fingerprint: str, media_input, camera_number_string: str, save_media_filepath: str, 
         gps_lock, signature_lock, upload_lock):
    """
    Main function for processing and handling media (images/videos).

    This function processes media by capturing images or reading videos, fetching GPS data,
    creating combined data structures, generating digests and signatures, and uploading
    or saving the media based on internet availability.

    Args:
        fingerprint (str): The fingerprint identifier or username associated with the media.
        media_input: For images, this is a cv2 image array; for videos, this is the file path as a string.
        camera_number_string (str): The identifier for the camera/device capturing the media.
        save_media_filepath (str): The directory path where media should be saved locally.
        gps_lock (threading.Lock): A lock object to synchronize GPS data access.
        signature_lock (threading.Lock): A lock object to synchronize signature creation.
        upload_lock (threading.Lock): A lock object to synchronize upload operations.

    Returns:
        None
    """
    print("Main called; processing media for upload or local storage.")

    # Check if processing an image or video based on the save path
    if save_media_filepath.endswith('Images'):
        # ---------------------- Process Image ----------------------------
        print("Processing image.")

        image = media_input  # Received image input as cv2 image array

        # Encode the image to PNG format for transmission or storage
        success, encoded_image = cv2.imencode('.png', image)
        if not success:
            print("Error: Failed to encode image.")
            return

        print("Image encoded successfully.")

        # ---------- Capture GNSS Data (Time and Location) ------------------------
        lat_value, long_value, time_value, date_value = read_gps_data(gps_lock)
        location = f"{lat_value}, {long_value}"
        time_str = f"{time_value}"
        date_str = f"{date_value}"

        print(f"Received GPS Data - Date: {date_str}, Time: {time_str}, Location: {location}")

        # -------------- Combine Data for Digest Creation -------------------------
        combined_data = create_combined(
            fingerprint,
            camera_number_string,
            encoded_image.tobytes(),
            date_str,
            time_str,
            location
        )
        print("Combined data created for digest.")

        # ---------------- Create Digest for Signing ------------------------------
        try:
            digest = create_digest(combined_data)
            print("Digest created successfully.")
        except Exception as e:
            print(f"Error creating digest: {str(e)}")
            return

        # ---------------- Generate Signature Using TPM ---------------------------
        try:
            signature_string = create_signature(digest, signature_lock)
            print("Signature generated successfully.")
        except Exception as e:
            print(f"Error generating signature: {str(e)}")
            return

        # ---------------- Create Metadata Dictionary -----------------------------
        metadata = create_metadata(
            fingerprint,
            camera_number_string,
            date_str,
            time_str,
            location,
            signature_string
        )
        print("Metadata created successfully.")

        # ---------------- Upload or Save Image Based on Internet Availability -----
        with upload_lock:
            print("Acquired upload lock for image processing.")
            if is_internet_available():
                try:
                    print("Internet available. Attempting to upload image.")
                    upload_image(encoded_image.tobytes(), metadata)
                    print("Image uploaded successfully.")
                except Exception as e:
                    print(f"Error uploading image: {str(e)}")
                    print("Saving image locally due to upload failure.")
                    save_image(encoded_image.tobytes(), metadata, save_media_filepath)
            else:
                print("No internet connection. Saving image locally.")
                save_image(encoded_image.tobytes(), metadata, save_media_filepath)

    else:
        # ---------------------- Process Video ----------------------------
        print("Processing video.")

        video_filepath = media_input  # Video file path provided as input

        # ---------- Capture GNSS Data (Time and Location) ------------------------
        lat_value, long_value, time_value, date_value = read_gps_data(gps_lock)
        location = f"{lat_value}, {long_value}"
        time_str = f"{time_value}"
        date_str = f"{date_value}"

        print(f"Received GPS Data - Date: {date_str}, Time: {time_str}, Location: {location}")

        with upload_lock:
            print("Acquired upload lock for video processing.")

            # Read video bytes from the specified file path
            try:
                with open(video_filepath, 'rb') as video_file:
                    video_bytes = video_file.read()
                print("Video file read successfully.")
            except Exception as e:
                print(f"Error reading video file: {str(e)}")
                return

            # -------------- Combine Data for Digest Creation ---------------------
            combined_data = create_combined(
                fingerprint,
                camera_number_string,
                video_bytes,
                date_str,
                time_str,
                location
            )
            print("Combined data created for digest.")

            # ---------------- Create Digest for Signing --------------------------
            try:
                digest = create_digest(combined_data)
                print("Digest created successfully.")
            except Exception as e:
                print(f"Error creating digest: {str(e)}")
                return

            # ---------------- Generate Signature Using TPM -----------------------
            try:
                signature_string = create_signature(digest, signature_lock)
                print("Signature generated successfully.")
            except Exception as e:
                print(f"Error generating signature: {str(e)}")
                return

            # ---------------- Create Metadata Dictionary -------------------------
            try:
                metadata = create_metadata(
                    fingerprint,
                    camera_number_string,
                    date_str,
                    time_str,
                    location,
                    signature_string
                )
                print("Metadata created successfully.")
            except Exception as e:
                print(f"Error creating metadata: {str(e)}")
                return

            # ---------------- Save Metadata Locally ------------------------------
            try:
                base_filename = os.path.splitext(os.path.basename(video_filepath))[0]
                metadata_filepath = os.path.join(save_media_filepath, f"{base_filename}.json")
                save_metadata(metadata, metadata_filepath)
                print(f"Metadata saved locally at {metadata_filepath}.")
            except Exception as e:
                print(f"Error saving metadata: {str(e)}")
                return

            # ---------------- Upload or Save Video Based on Internet Availability -
            if is_internet_available():
                try:
                    print("Internet available. Attempting to upload video.")
                    upload_video(video_bytes, metadata)
                    print("Video uploaded successfully.")

                    # Remove local files after successful upload
                    os.remove(video_filepath)
                    os.remove(metadata_filepath)
                    print("Local video and metadata files deleted after upload.")
                except Exception as e:
                    print(f"Error uploading video: {str(e)}")
                    print("Video and metadata files will remain saved locally due to upload failure.")
            else:
                print("No internet connection. Video and metadata files saved locally for later upload.")
