import boto3
import json
import base64
import mysql.connector
import os
import cv2
import numpy as np
from twilio.rest import Client
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import hashlib
import subprocess

def handler(event, context):
    """
    AWS Lambda handler for processing and verifying media files uploaded to S3.

    This function handles media files (images and videos) uploaded to an S3 bucket, verifies
    their authenticity using digital signatures, and processes the verified files. If the
    verification is successful, the media is converted (if necessary), uploaded to another
    S3 bucket, and a notification is sent via SMS. If verification fails, an SMS notification
    is sent indicating the failure.

    Args:
        event (dict): The event payload containing S3 object details.
        context (object): AWS Lambda context object (not used in this function).

    Returns:
        dict: A dictionary containing the HTTP status code, success message, and any errors.
    """
    # Create an S3 client
    s3_client = boto3.client('s3')

    # Extract bucket name and object key from the event
    object_key = str(event['Records'][0]['s3']['object']['key'])
    print("Object key: should be NewImage.png or NewVideo.avi", object_key)
    bucket_name = 'unverifiedimages'

    # Determine if the file is an image or video based on the file extension
    image = object_key.endswith(".png")
    print(f"Is this an image: {image}")

    errors = ""

    try:
        # Get the object from S3
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        except Exception as e:
            errors += f"Error: Get object error : {str(e)}"

        # Process the media based on whether it's an image or video
        if image:
            temp_media_path = '/tmp/TempNewImage.png'
            s3_client.download_file(bucket_name, object_key, temp_media_path)
            media = cv2.imread(temp_media_path)
            _, encoded_image = cv2.imencode('.png', media)
            encoded_media = encoded_image.tobytes()
        else:
            temp_media_path = '/tmp/TempNewVideo.avi'
            s3_client.download_file(bucket_name, object_key, temp_media_path)
            print("Downloading video Done")
            temp_mp4_path = '/tmp/TempNewMp4.mp4'
            with open(temp_media_path, 'rb') as video:
                encoded_media = video.read()
                print(encoded_media[-10:])
                
        # Access the object's metadata
        metadata = response['Metadata']

        try:
            fingerprint, camera_number, date_data, time_data, location_data, signature, signature_string = recreate_data(metadata)
        except Exception as e:
            errors += f"Error: Cannot recreate time and metadata {str(e)}"

        try:
            print("Storing JSON details")
            store_json_details(temp_media_path, fingerprint, camera_number, date_data, time_data, location_data, signature_string)
            print("Stored JSON details")
        except Exception as e:
            errors += f"Error: Cannot store JSON details {str(e)}"
        
        try:
            public_key_base64 = get_public_key(int(camera_number))
            public_key = base64.b64decode(public_key_base64)
        except Exception as e:
            errors += f"Error: Public key error: {str(e)}"

        try:
            combined_data = create_combined(fingerprint, camera_number, encoded_media, date_data, time_data, location_data)
        except Exception as e:
            errors += f"Error: Couldn't combine data: {str(e)}"

        try: 
            valid = verify_signature(combined_data, signature, public_key)
        except Exception as e:
            errors += f"Error: Error verifying or denying signature {str(e)}"

        if valid:
            try:
                media_save_name, media_number = upload_verified(
                    s3_client, fingerprint, camera_number, date_data, time_data, location_data, 
                    signature, temp_media_path, image
                )
            except Exception as e:
                errors += f"Issue uploading to verified bucket: {str(e)}"

            try:
                convert_to_mp4(temp_media_path, temp_mp4_path)
                upload_verified_mp4(s3_client, fingerprint, temp_mp4_path, media_number)
            except Exception as e:
                errors += f"Issue uploading to verified bucket: {str(e)}"

            try:
                send_text(valid, fingerprint, media_save_name)
            except Exception as e:
                errors += f"Issue sending text: {str(e)}"

            # Clean up temporary files
            os.remove(temp_media_path)
            os.remove(temp_mp4_path)
            
        else:
            try:
                send_text(valid, fingerprint)
            except Exception as e:
                errors += f"Issue sending text after failing verification: {str(e)}"

    except Exception as e:
        errors += f'There was an exception: {str(e)}'

    print("Errors: ", errors)

    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully!'),
        'errors': errors,
    }

def recreate_data(metadata):
    """
    Extracts and returns relevant data from metadata.

    Args:
        metadata (dict): The metadata dictionary containing fingerprint, camera number, 
                         date, time, location, and signature.

    Returns:
        tuple: A tuple containing fingerprint, camera number, date, time, location, 
               signature, and signature string.
    """
    fingerprint = metadata.get('fingerprint')
    camera_number = metadata.get('cameranumber')
    date_data = metadata.get('date')
    time_data = metadata.get('time')
    location_data = metadata.get('location')
    signature_string = metadata.get('signature')
    signature = base64.b64decode(signature_string)

    return fingerprint, camera_number, date_data, time_data, location_data, signature, signature_string

def create_combined(fingerprint, camera_number, media, date, time, location):
    """
    Combines the provided data into a single byte object.

    Args:
        fingerprint (str): The fingerprint data.
        camera_number (str): The camera number.
        media (bytes): The media file data.
        date (str): The date of the media capture.
        time (str): The time of the media capture.
        location (str): The location of the media capture.

    Returns:
        bytes: The combined byte object containing all provided data.
    """
    encoded_fingerprint = fingerprint.encode('utf-8')
    encoded_number = camera_number.encode('utf-8')
    encoded_date = date.encode('utf-8')
    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_fingerprint + encoded_number + media + encoded_date + encoded_time + encoded_location

    return combined_data

def get_public_key(camera_number):
    """
    Retrieves the public key for the specified camera number from the database.

    Args:
        camera_number (int): The camera number for which the public key is to be retrieved.

    Returns:
        str: The base64-encoded public key.
    """
    # Database connection details
    host = ""
    user = ""
    password = ""
    database = ""

    # Connect to the database
    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    cursor = connection.cursor()

    # SQL query to retrieve the public key
    query = "SELECT PublicKey FROM Cameras WHERE CameraNumber = %s"
    cursor.execute(query, (int(camera_number),))

    # Fetch the result
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        public_key = result[0]
        return public_key  # Return the public key
    
    return 'Public key not found'

def upload_verified(s3_client, fingerprint, camera_number, date_data, time_data, location_data, signature, temp_media_path, image):
    """
    Uploads verified media and metadata to an S3 bucket.

    Args:
        s3_client: The Boto3 S3 client.
        fingerprint (str): The fingerprint of the user.
        camera_number (str): The camera number.
        date_data (str): The date of the media capture.
        time_data (str): The time of the media capture.
        location_data (str): The location of the media capture.
        signature (bytes): The signature for verification.
        temp_media_path (str): The path to the temporary media file.
        image (bool): Whether the media is an image (True) or video (False).

    Returns:
        tuple: A tuple containing the saved media file name and media number.
    """
    bucket_name  = ''.join(fingerprint.split()).lower()
    destination_bucket_name = bucket_name

    try:
        media_number = get_next_number_for_new_file(destination_bucket_name)
    except Exception as e:
        pass
    
    media_file_name = f"{media_number}.png" if image else f"{media_number}.avi"

    # Create JSON data
    json_data = {
        "Fingerprint": fingerprint,
        "Camera Number": camera_number,
        "Date": date_data,
        "Time": time_data,
        "Location": location_data,
        "Signature_Base64": base64.b64encode(signature).decode('utf-8')
    }

    # Save JSON data to a file with the same name as the media file
    json_file_name = f"{media_number}.json"
    temp_json_path = f'/tmp/{json_file_name}'

    with open(temp_json_path, 'w') as json_file:
        json.dump(json_data, json_file)

    try:
        s3_client.upload_file(temp_media_path, destination_bucket_name, media_file_name)
    except Exception as e:
        pass
        
    try:  # Upload JSON file to the same S3 bucket
        s3_client.upload_file(temp_json_path, destination_bucket_name, json_file_name)
    except Exception as e:
        pass

    # Clean up: Delete temporary files
    os.remove(temp_json_path)

    return media_file_name, media_number

def upload_verified_mp4(s3_client, fingerprint, temp_mp4_path, media_number):
    """
    Uploads a verified MP4 file to an S3 bucket.

    Args:
        s3_client: The Boto3 S3 client.
        fingerprint (str): The fingerprint of the user.
        temp_mp4_path (str): The path to the temporary MP4 file.
        media_number (int): The media number.

    Returns:
        None
    """
    bucket_name  = ''.join(fingerprint.split()).lower()
    destination_bucket_name = bucket_name
    media_file_name = f"{media_number}.mp4"

    try:
        s3_client.upload_file(temp_mp4_path, destination_bucket_name, media_file_name, ExtraArgs={'ContentType': 'video/mp4'})
    except Exception as e:
        pass

def get_next_number_for_new_file(bucket_name):
    """
    Retrieves the next available number for a new file in the S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.

    Returns:
        int: The next available number for the new file.
    """
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    highest_number = 0

    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get('Contents', []):
            file_name = obj['Key']
            try:
                number = int(file_name.split('.')[0])
                if number > highest_number:
                    highest_number = number
            except ValueError:
                continue
    
    return highest_number + 1

def verify_signature(combined_data, signature, public_key):
    """
    Verifies the digital signature of the combined data.

    Args:
        combined_data (bytes): The combined data that was signed.
        signature (bytes): The signature to verify.
        public_key (bytes): The public key to use for verification.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    temp_public_key_path = '/tmp/recreated_public_key.pem'

    with open(temp_public_key_path, "wb") as file:
        file.write(public_key)

    with open(temp_public_key_path, "rb") as key_file:
        public_key_data = key_file.read()

    public_key = serialization.load_pem_public_key(public_key_data)

    try:
        public_key.verify(
            signature,
            combined_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        os.remove(temp_public_key_path)
        return True
    
    except InvalidSignature:
        os.remove(temp_public_key_path)
        return False

def send_text(valid, fingerprint, image_save_name="default"):
    """
    Sends an SMS notification indicating the result of the verification process.

    Args:
        valid (bool): Whether the verification was successful.
        fingerprint (str): The fingerprint of the user.
        image_save_name (str): The name of the saved image or video file.

    Returns:
        None
    """
    account_sid = '#'  # Twilio Account SID
    auth_token = '#'   # Twilio Auth Token
    client = Client(account_sid, auth_token)

    if valid:
        body = f"Your Image was Successfully Authenticated. Stored as {image_save_name}"
    else:
        body = f"Your Image failed to be Authenticated. Deleted"

    numbers = {
        "Dani Kasti": '+18025577844', 
        "John Dale": '+17819159187',
        "Darius Paradie": '+16032496942',
        "Jace Christakis": '+17819993514'
    }
    
    receiving_user = numbers[fingerprint]

    message = client.messages.create(
        from_='+18573664416',
        body=body,
        to=receiving_user
    )

def store_json_details(temp_image_path, fingerprint, camera_number, date_data, time_data, location_data, signature):
    """
    Stores the JSON details of the media in the database.

    Args:
        temp_image_path (str): The path to the temporary image file.
        fingerprint (str): The fingerprint of the user.
        camera_number (str): The camera number.
        date_data (str): The date of the media capture.
        time_data (str): The time of the media capture.
        location_data (str): The location of the media capture.
        signature (str): The base64-encoded signature.

    Returns:
        None
    """
    # Hash the image data to use as an index
    with open(temp_image_path, 'rb') as file:
        data = file.read()
        hash_object = hashlib.sha256()
        hash_object.update(data)
        image_hash = hash_object.hexdigest()

    # Convert details to JSON format
    details = json.dumps({
        'Fingerprint': fingerprint,
        'Camera Number': camera_number,
        'Date': date_data,
        'Time': time_data,
        'Location': location_data,
        'Signature_Base64': signature
    })
    
    print(f"Image Hash: {image_hash}")
    print(f"Details: {details}")

    # Database connection details
    host = ""
    user = ""
    password = ""
    database = ""

    # Connect to the database
    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    cursor = connection.cursor()

    query = """
    INSERT INTO image_data (image_hash, data)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE data = %s
    """

    cursor.execute(query, (image_hash, details, details))
    
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    print(f"Stored the data with image hash {image_hash}, Time: {time_data}, Date: {date_data}, Location: {location_data}")

def convert_to_mp4(temp_media_path, temp_mp4_path):
    """
    Converts an AVI file to MP4 using FFmpeg.

    Args:
        temp_media_path (str): The path to the temporary AVI file.
        temp_mp4_path (str): The path to save the converted MP4 file.

    Returns:
        None
    """
    print("Trying to convert to mp4 from avi...........")

    command_convert_to_mp4 = [
        'ffmpeg',
        '-i', temp_media_path,          # Input file path
        '-c:v', 'libx264',              # Video codec to use (H.264)
        '-crf', '23',                   # Constant Rate Factor (CRF) value, 18-28 is a good range, lower is higher quality
        '-preset', 'medium',            # Preset for compression efficiency (balance between speed and quality)
        '-c:a', 'aac',                  # Audio codec to use (AAC)
        '-b:a', '128k',                 # Audio bitrate
        '-strict', 'experimental',      # Allow experimental codecs (if needed for AAC)
        temp_mp4_path                   # Output file path
    ]

    process = subprocess.Popen(command_convert_to_mp4, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    print(f"Video output: stdout {stdout}, stderr: {stderr}")
